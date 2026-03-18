from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, cast, String
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
import os
import glob

from src.database.session import get_db
from src.database.models import Comprobante, Cfdi, CfdiRelacionado
from src.api.endpoints.auth import get_active_entidad
from fastapi.responses import FileResponse

router = APIRouter(tags=["Comprobantes"])

@router.get("/")
async def get_comprobantes(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    entidad_id: uuid.UUID = Depends(get_active_entidad)
):
    """
    [ES] Lista los comprobantes indexados. Aislamiento Multi-tenant estricto.
    """
    try:
        query = (
            select(Comprobante)
            .where(Comprobante.entidad_id == entidad_id)
            .order_by(Comprobante.fecha_emision.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(query)
        comprobantes = result.scalars().all()

        output = []
        page_uuids = [str(c.uuid).lower() for c in comprobantes]
        
        uuid_to_folio = {str(comp.uuid).lower(): comp.folio for comp in comprobantes}
        uuid_to_receptor = {str(comp.uuid).lower(): comp.rfc_receptor for comp in comprobantes}

        rels_map = {u: [] for u in page_uuids}
        if page_uuids:
            q_rels = select(CfdiRelacionado).where(
                (func.lower(cast(CfdiRelacionado.uuid_padre, String)).in_(page_uuids)) |
                (func.lower(cast(CfdiRelacionado.cfdi_id, String)).in_(page_uuids))
            )
            res_rels = await db.execute(q_rels)
            all_rels = res_rels.scalars().all()
            
            for r in all_rels:
                padre = str(r.uuid_padre).lower() if r.uuid_padre else ""
                hijo = str(r.cfdi_id).lower() if r.cfdi_id else ""
                if padre in rels_map:
                    rels_map[padre].append(r)
                if hijo in rels_map and hijo != padre:
                    rels_map[hijo].append(r)
                    
        dir_files_cache = {}
        for c in comprobantes:
            if c.ruta_resguardo:
                dirname = c.ruta_resguardo if os.path.isdir(c.ruta_resguardo) else os.path.dirname(c.ruta_resguardo)
                if dirname not in dir_files_cache:
                    try:
                        dir_files_cache[dirname] = [f.lower() for f in os.listdir(dirname)]
                    except Exception:
                        dir_files_cache[dirname] = []

        for c in comprobantes:
            pdf_exists = False
            xml_exists = False
            
            if c.ruta_resguardo:
                dirname = c.ruta_resguardo if os.path.isdir(c.ruta_resguardo) else os.path.dirname(c.ruta_resguardo)
                files_in_dir = dir_files_cache.get(dirname, [])
                
                c_uuid_lower = str(c.uuid).lower()
                c_folio = str(c.folio).lower() if c.folio else ""
                c_folio_limpio = c_folio.lstrip('0') if c_folio else ""
                
                for f in files_in_dir:
                    match_uuid = c_uuid_lower in f
                    match_folio = c_folio and (c_folio in f)
                    match_limpio = c_folio_limpio and (f"{c_folio_limpio}.pdf" in f or f"{c_folio_limpio}.xml" in f)
                    
                    if match_uuid or match_folio or match_limpio:
                        if f.endswith('.pdf'): pdf_exists = True
                        if f.endswith('.xml'): xml_exists = True

            pdf_file_path = c.ruta_resguardo if c.ruta_resguardo else None
            xml_file_path = c.ruta_resguardo.replace('.pdf', '.xml').replace('.PDF', '.xml') if c.ruta_resguardo else None

            mis_relaciones = rels_map.get(str(c.uuid).lower(), [])
            reps_list = []
            for r in mis_relaciones:
                es_padre = str(r.uuid_padre).lower() == str(c.uuid).lower()
                rel_uuid = str(r.cfdi_id) if es_padre else str(r.uuid_padre)
                
                reps_list.append({
                    "uuid": rel_uuid,
                    "folio": uuid_to_folio.get(rel_uuid.lower(), "S/N"),
                    "monto": float(r.monto_pagado or 0),
                    "tipo": r.tipo_relacion or "PAGO",
                    "tipo_documento": "Pago" if es_padre else "Factura",
                    "rfc_receptor": uuid_to_receptor.get(rel_uuid.lower(), "")
                })
            
            total_monto_pago = sum(r["monto"] for r in reps_list)
            resolved_total = total_monto_pago if c.tipo_comprobante == 'P' and total_monto_pago > 0 else float(c.total or 0)

            # 🛠️ CORRECCIÓN DE ESTATUS PARA PAGOS
            estatus_cobro = "---"
            if c.tipo_comprobante == 'P':
                estatus_cobro = "PAGADO"
            elif c.metodo_pago == 'PUE':
                estatus_cobro = "PAGADO"
            elif c.metodo_pago == 'PPD':
                if total_monto_pago >= float(c.total or 0):
                    estatus_cobro = "PAGADO"
                elif total_monto_pago > 0:
                    estatus_cobro = "PAGO PARCIAL"
                else:
                    estatus_cobro = "PENDIENTE"

            output.append({
                "id": str(c.uuid),
                "uuid": str(c.uuid),
                "serie": c.serie,
                "folio": c.folio,
                "rfc_emisor": c.rfc_emisor,
                "rfc_receptor": c.rfc_receptor,
                "nombre_receptor": c.rfc_receptor,
                "status": c.status,
                "estatus_cobro": estatus_cobro,
                "total": resolved_total,
                "tipo_comprobante": c.tipo_comprobante,
                "metodo_pago": c.metodo_pago,
                "forma_pago": c.forma_pago,
                "fecha_emision": c.fecha_emision.isoformat() if c.fecha_emision else None,
                "pdf_file_path": pdf_file_path,
                "xml_file_path": xml_file_path,
                "pdf_exists": pdf_exists,
                "xml_exists": xml_exists,
                "saldo_pendiente": float(c.total or 0) - total_monto_pago if c.metodo_pago == 'PPD' else 0.0,
                "reps_asociados": reps_list
            })

        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en API: {str(e)}")

@router.get("/{uuid}")
async def get_comprobante_detail(
    uuid: str, 
    db: AsyncSession = Depends(get_db), 
    entidad_id: uuid.UUID = Depends(get_active_entidad)
):
    try:
        query = select(Comprobante).where(func.lower(cast(Comprobante.uuid, String)) == uuid.lower())
        res = await db.execute(query)
        comp = res.scalars().first()
        
        if not comp:
             raise HTTPException(status_code=404, detail="Comprobante no encontrado")

        descripcion = "Concepto no especificado"
        pdf_exists = False
        xml_exists = False

        if comp.ruta_resguardo:
             path_str = comp.ruta_resguardo
             dirname = path_str if os.path.isdir(path_str) else os.path.dirname(path_str)
             
             try:
                 files_in_dir = [f.lower() for f in os.listdir(dirname)]
                 c_folio_limpio = str(comp.folio).lstrip('0') if comp.folio else ""
                 
                 for f in files_in_dir:
                     if uuid.lower() in f or (c_folio_limpio and f"{c_folio_limpio}.xml" in f):
                         xml_exists = True
                         ruta_xml = os.path.join(dirname, f)
                     if uuid.lower() in f or (c_folio_limpio and f"{c_folio_limpio}.pdf" in f):
                         pdf_exists = True
             except:
                 pass

             if xml_exists:
                  try:
                       import xml.etree.ElementTree as ET
                       tree = ET.parse(ruta_xml)
                       root = tree.getroot()
                       namespaces = {'cfdi': root.tag.split('}')[0].strip('{')}
                       concepto = root.find('.//cfdi:Concepto', namespaces)
                       if concepto is not None:
                            descripcion = concepto.get('Descripcion') or "Sin descripción"
                  except Exception as e:
                       descripcion = f"Error al leer XML: {str(e)}"
        
        q_rels = select(CfdiRelacionado).where(
            (func.lower(cast(CfdiRelacionado.uuid_padre, String)) == uuid.lower()) |
            (func.lower(cast(CfdiRelacionado.cfdi_id, String)) == uuid.lower())
        )
        res_rels = await db.execute(q_rels)
        all_rels = res_rels.scalars().all()

        reps_list = []
        for r in all_rels:
            es_padre = str(r.uuid_padre).lower() == uuid.lower()
            rel_uuid = str(r.cfdi_id) if es_padre else str(r.uuid_padre)
            reps_list.append({
                "uuid": rel_uuid,
                "monto": float(r.monto_pagado or 0),
                "tipo": r.tipo_relacion or "PAGO"
            })

        total_monto_pago = sum(r["monto"] for r in reps_list)
        is_rep_computed = len(reps_list) > 0
        resolved_total = total_monto_pago if is_rep_computed and total_monto_pago > 0 else float(comp.total or 0)

        return {
             "id": str(comp.uuid),
             "uuid": str(comp.uuid),
             "serie": comp.serie,
             "folio": comp.folio,
             "rfc_emisor": comp.rfc_emisor,
             "rfc_receptor": comp.rfc_receptor,
             "status": comp.status,
             "total": resolved_total,
             "tipo_comprobante": comp.tipo_comprobante,
             "metodo_pago": comp.metodo_pago,
             "forma_pago": comp.forma_pago,
             "fecha_emision": comp.fecha_emision.isoformat() if comp.fecha_emision else None,
             "descripcion_concepto": descripcion,
             "pdf_exists": pdf_exists,
             "xml_exists": xml_exists,
             "reps_asociados": reps_list
        }
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Error en Detalle: {str(e)}")

@router.get("/{uuid}/xml")
async def get_comprobante_xml(
    uuid: str, 
    db: AsyncSession = Depends(get_db), 
    entidad_id: uuid.UUID = Depends(get_active_entidad)
):
    query = select(Comprobante).where(func.lower(cast(Comprobante.uuid, String)) == uuid.lower())
    res = await db.execute(query)
    comp = res.scalars().first()
    
    if not comp or not comp.ruta_resguardo:
        raise HTTPException(status_code=404, detail="Comprobante no encontrado o sin ruta")

    path_str = comp.ruta_resguardo
    dirname = path_str if os.path.isdir(path_str) else os.path.dirname(path_str)
    
    c_folio_limpio = str(comp.folio).lstrip('0') if comp.folio else ""
    try:
        files = os.listdir(dirname)
        for f in files:
            if f.lower().endswith('.xml') and (uuid.lower() in f.lower() or (c_folio_limpio and f"{c_folio_limpio}.xml" in f.lower())):
                return FileResponse(path=os.path.join(dirname, f), filename=f"{uuid}.xml")
    except:
        pass
              
    raise HTTPException(status_code=404, detail=f"Archivo XML no encontrado en disco.")

@router.get("/{uuid}/pdf")
async def get_comprobante_pdf(
    uuid: str, 
    db: AsyncSession = Depends(get_db), 
    entidad_id: uuid.UUID = Depends(get_active_entidad)
):
    query = select(Comprobante).where(func.lower(cast(Comprobante.uuid, String)) == uuid.lower())
    res = await db.execute(query)
    comp = res.scalars().first()

    if not comp or not comp.ruta_resguardo:
        raise HTTPException(status_code=404, detail="Comprobante no encontrado o sin ruta")

    path_str = comp.ruta_resguardo
    dirname = path_str if os.path.isdir(path_str) else os.path.dirname(path_str)

    c_folio_limpio = str(comp.folio).lstrip('0') if comp.folio else ""
    try:
        files = os.listdir(dirname)
        for f in files:
            if f.lower().endswith('.pdf') and (uuid.lower() in f.lower() or (c_folio_limpio and f"{c_folio_limpio}.pdf" in f.lower())):
                return FileResponse(path=os.path.join(dirname, f), filename=f"{uuid}.pdf")
    except:
        pass

    raise HTTPException(status_code=404, detail="El archivo PDF no se encuentra asociado a este comprobante")