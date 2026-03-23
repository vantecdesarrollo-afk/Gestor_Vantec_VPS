from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, cast, String
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import StreamingResponse
import io
import csv
import uuid
import os
from fastapi.responses import FileResponse

# Importaciones locales
from src.database.session import get_db
from src.database.models import Comprobante, CfdiRelacionado
from src.api.endpoints.auth import get_active_entidad

router = APIRouter(prefix="/api/v1/comprobantes", tags=["Comprobantes"])

@router.get("/")
async def get_comprobantes(
    limit: int = Query(50),
    offset: int = Query(0),
    tipo: str | None = Query(None),
    estatus: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    entidad_id: uuid.UUID = Depends(get_active_entidad)
):
    try:
        # 1. Consulta a la DB
        query = (
            select(Comprobante)
            .options(selectinload(Comprobante.relacionados))
            .where(Comprobante.entidad_id == entidad_id)
        )
        
        if tipo:
            query = query.where(Comprobante.tipo_comprobante == tipo)

        # Filtros de Estatus Inteligente en DB (VCORE-BRIDGE)
        if estatus:
            if estatus == 'Pendiente':
                subquery = select(CfdiRelacionado.uuid_relacionado)
                query = query.where(
                    Comprobante.metodo_pago == 'PPD',
                    cast(Comprobante.uuid, String).notin_(subquery)
                )
            elif estatus == 'Pagado':
                sum_q = select(func.sum(CfdiRelacionado.monto_pagado)).where(
                    CfdiRelacionado.uuid_relacionado == cast(Comprobante.uuid, String)
                ).scalar_subquery()
                query = query.where(
                    (Comprobante.metodo_pago == 'PUE') |
                    ((Comprobante.metodo_pago == 'PPD') & (func.coalesce(sum_q, 0) >= Comprobante.total))
                )
            elif estatus in ['Parcial', 'Ambar', 'Ámbar']:
                sum_q = select(func.sum(CfdiRelacionado.monto_pagado)).where(
                    CfdiRelacionado.uuid_relacionado == cast(Comprobante.uuid, String)
                ).scalar_subquery()
                query = query.where(
                    Comprobante.metodo_pago == 'PPD',
                    func.coalesce(sum_q, 0) < Comprobante.total,
                    func.coalesce(sum_q, 0) > 0
                )
            elif estatus == 'Vigente':
                query = query.where(
                    Comprobante.metodo_pago.notin_(['PPD', 'PUE'])
                )

        query = query.order_by(Comprobante.fecha_emision.desc()).offset(offset).limit(limit)
        
        result = await db.execute(query)
        rows = result.scalars().all()
        
        # --- CARGA EFICIENTE DE DATOS PARA RELACIONADOS 360° ---
        row_uuids = [str(r.uuid) for r in rows]
        
        # 1. Relaciones directas (P -> I): ya están en r.relacionados
        all_rel_uuids = []
        for r in rows:
            all_rel_uuids.extend([rel.uuid_relacionado for rel in r.relacionados])
            
        # 2. Relaciones inversas (I -> P): buscar complementos que apuntan a estas facturas
        inverse_map = {}
        if row_uuids:
             inv_rels_q = await db.execute(
                  select(CfdiRelacionado, Comprobante.folio, Comprobante.serie, Comprobante.rfc_receptor, Comprobante.tipo_comprobante)
                  .join(Comprobante, func.lower(cast(Comprobante.uuid, String)) == func.lower(CfdiRelacionado.uuid_padre))
                  .where(func.lower(CfdiRelacionado.uuid_relacionado).in_([u.lower() for u in row_uuids]))
             )
             for row_inv in inv_rels_q.all():
                  rel_obj, folio, serie, rfc, tipo_doc = row_inv
                  u_rel = str(rel_obj.uuid_relacionado).lower()
                  if u_rel not in inverse_map:
                       inverse_map[u_rel] = []
                  type_label = "Pago" if tipo_doc == 'P' else "Relacionado"
                  from src.services.cfdi_storage import find_cfdi_attachments
                  inv_att = find_cfdi_attachments(str(rel_obj.uuid_padre), serie or "", folio or "", tipo_doc or "I")
                  inverse_map[u_rel].append({
                       "uuid": str(rel_obj.uuid_padre),
                       "monto": float(rel_obj.monto_pagado or 0),
                       "tipo_documento": type_label,
                       "folio": f"{serie or ''} {folio or 'S/N'}".strip(),
                       "rfc_receptor": rfc or "",
                       "pdf_exists": inv_att["pdf_path"] is not None,
                       "xml_exists": inv_att["xml_path"] is not None
                  })

        # 3. Headers para las relaciones directas (P -> I)
        rel_data_sub = {}
        if all_rel_uuids:
              rel_res = await db.execute(select(Comprobante.uuid, Comprobante.folio, Comprobante.serie, Comprobante.rfc_receptor, Comprobante.tipo_comprobante).where(func.lower(cast(Comprobante.uuid, String)).in_([u.lower() for u in all_rel_uuids])))
              for rr in rel_res.all():
                   rel_data_sub[str(rr[0]).lower()] = {"folio": rr[1], "serie": rr[2], "rfc_receptor": rr[3], "tipo": rr[4]}

        # 4. Batch Queries to avoid N+1
        all_page_uuids = [str(r.uuid).lower() for r in rows]
        
        # 4a. Batch SUM Payments (for P type)
        pagos_sum = {}
        if all_page_uuids:
             sum_p_batch = await db.execute(
                 select(cast(CfdiRelacionado.cfdi_id, String).label('uuid'), func.sum(CfdiRelacionado.monto_pagado))
                 .where(func.lower(cast(CfdiRelacionado.cfdi_id, String)).in_(all_page_uuids))
                 .group_by(cast(CfdiRelacionado.cfdi_id, String))
             )
             for row in sum_p_batch.all():
                  pagos_sum[str(row[0]).lower()] = float(row[1] or 0)
                  
        # 4b. Batch SUM Invoices (for PPD type)
        ppd_sum = {}
        if all_page_uuids:
             sum_ppd_batch = await db.execute(
                 select(func.lower(CfdiRelacionado.uuid_relacionado).label('uuid'), func.sum(CfdiRelacionado.monto_pagado))
                 .where(func.lower(CfdiRelacionado.uuid_relacionado).in_(all_page_uuids))
                 .group_by(func.lower(CfdiRelacionado.uuid_relacionado))
             )
             for row in sum_ppd_batch.all():
                  ppd_sum[str(row[0]).lower()] = float(row[1] or 0)
                  
        # 4c. Batch Cfdi Table to resolve paths directly without slow glob
        all_query_uuids = list(set(all_page_uuids + [str(u).lower() for u in all_rel_uuids]))
        cfdi_paths = {}
        if all_query_uuids:
             from src.database.models import Cfdi
             cfdi_batch = await db.execute(
                 select(func.lower(Cfdi.uuid), Cfdi.xml_file_path, Cfdi.pdf_file_path)
                 .where(func.lower(Cfdi.uuid).in_(all_query_uuids))
             )
             for row in cfdi_batch.all():
                  cfdi_paths[str(row[0]).lower()] = {"xml": row[1], "pdf": row[2]}

        # 4d. Concurrent fallback lookup for historical items to avoid sequential Glob slowing index
        async_fallback_map = {}
        from src.services.cfdi_storage import find_cfdi_attachments
        import concurrent.futures

        def get_missing_att(u, s, f, t):
             return u.lower(), find_cfdi_attachments(u, s, f, t)
             
        items_to_resolve = []
        for r in rows:
             u_l = str(r.uuid).lower()
             has_xml = os.path.exists(r.ruta_resguardo or "")
             has_pdf = os.path.exists((r.ruta_resguardo or "").replace('.xml', '.pdf'))
             c_p = cfdi_paths.get(u_l, {})
             if c_p.get("xml") and os.path.exists(c_p["xml"]): has_xml = True
             if c_p.get("pdf") and os.path.exists(c_p["pdf"]): has_pdf = True
             if not has_xml or not has_pdf:
                  items_to_resolve.append((str(r.uuid), r.serie or "", r.folio or "", r.tipo_comprobante or "I"))

        # Adicionar los de relaciones directas para el submenu
        for rel_u in all_rel_uuids:
             u_l = str(rel_u).lower()
             r_d = rel_data_sub.get(u_l, {})
             c_p = cfdi_paths.get(u_l, {})
             has_xml = True if c_p.get("xml") and os.path.exists(c_p["xml"]) else False
             has_pdf = True if c_p.get("pdf") and os.path.exists(c_p["pdf"]) else False
             if not has_xml or not has_pdf:
                  items_to_resolve.append((rel_u, r_d.get("serie", ""), r_d.get("folio", ""), r_d.get("tipo", "I")))

        if items_to_resolve:
             # Dedup
             items_to_resolve = list(set(items_to_resolve))
             with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                  futures = [executor.submit(get_missing_att, x[0], x[1], x[2], x[3]) for x in items_to_resolve]
                  for fut in concurrent.futures.as_completed(futures):
                       u_l, att = fut.result()
                       async_fallback_map[u_l] = att

        output = []
        for r in rows:
            try:
                # Calculamos el total real para los Pagos (P)
                uuid_lower = str(r.uuid).lower()
                total_final = float(r.total or 0)
                if r.tipo_comprobante == 'P':
                    total_final = pagos_sum.get(uuid_lower, 0.0)
    
                # --- VERIFICACIÓN DE ARCHIVOS ---
                ruta_xml = r.ruta_resguardo or ""
                xml_exists = os.path.exists(ruta_xml) and os.path.isfile(ruta_xml) if ruta_xml else False
                pdf_exists = os.path.exists(ruta_xml.replace('.xml', '.pdf')) if ruta_xml and ruta_xml.endswith('.xml') else False
    
                if not xml_exists or not pdf_exists:
                     c_path = cfdi_paths.get(uuid_lower, {})
                     if not xml_exists and c_path.get("xml") and os.path.exists(c_path["xml"]):
                          xml_exists = True
                     if not pdf_exists and c_path.get("pdf") and os.path.exists(c_path["pdf"]):
                          pdf_exists = True
                     if not xml_exists or not pdf_exists:
                          f_att = async_fallback_map.get(uuid_lower, {})
                          if not xml_exists and f_att.get("xml_path") and os.path.exists(f_att["xml_path"]): xml_exists = True
                          if not pdf_exists and f_att.get("pdf_path") and os.path.exists(f_att["pdf_path"]): pdf_exists = True

    
                # Lógica de Estatus Inteligente (VCORE-BRIDGE)
                estatus_final = "Vigente"
                if r.metodo_pago == 'PUE':
                    estatus_final = "Pagado"
                elif r.metodo_pago == 'PPD':
                    total_pagado = ppd_sum.get(uuid_lower, 0.0)
                    if total_pagado <= 0:
                        estatus_final = "Pendiente"
                    else:
                        estatus_final = "Pagado" if total_pagado >= float(r.total or 0) else "Parcial"
    
                # --- TRAZABILIDAD 360° ---
                reps_directos = []
                for rel in r.relacionados:
                     rel_uuid = str(rel.uuid_relacionado).lower()
                     rel_tipo = rel_data_sub.get(rel_uuid, {}).get("tipo") or "I"
                     rel_folio = rel_data_sub.get(rel_uuid, {}).get("folio") or ""
                     rel_serie = rel_data_sub.get(rel_uuid, {}).get("serie") or ""
                     
                     rel_c_path = cfdi_paths.get(rel_uuid, {})
                     r_xml = rel_c_path.get("xml")
                     r_pdf = rel_c_path.get("pdf")
                     rel_xml_exists = True if r_xml and os.path.exists(r_xml) else False
                     rel_pdf_exists = True if r_pdf and os.path.exists(r_pdf) else False
                     if not rel_xml_exists or not rel_pdf_exists:
                          f_att = async_fallback_map.get(rel_uuid, {})
                          if not rel_xml_exists and f_att.get("xml_path") and os.path.exists(f_att["xml_path"]): rel_xml_exists = True
                          if not rel_pdf_exists and f_att.get("pdf_path") and os.path.exists(f_att["pdf_path"]): rel_pdf_exists = True
                     
                     reps_directos.append({
                         "uuid": rel_uuid,
                         "monto": float(rel.monto_pagado or 0),
                         "tipo_documento": "Factura" if rel_tipo == 'I' else "Documento",
                         "folio": f"{rel_serie} {rel_folio}".strip() or "S/N",
                         "rfc_receptor": rel_data_sub.get(rel_uuid, {}).get("rfc_receptor", ""),
                         "pdf_exists": rel_pdf_exists,
                         "xml_exists": rel_xml_exists
                     })
                
                reps_inversos = inverse_map.get(str(r.uuid).lower(), [])
                reps_all = reps_directos + reps_inversos
    
                # 2. MAPEADO DE LLAVES PARA EL FRONTEND (VCORE)
                output.append({
                    "uuid": str(r.uuid),
                    "fecha": r.fecha_emision.strftime("%d/%m/%Y") if r.fecha_emision else "---",
                    "serie": r.serie or "",
                    "folio": r.folio or "",
                    "rfc_emisor": r.rfc_emisor,
                    "nombre_emisor": r.nombre_emisor,
                    "rfc_receptor": r.rfc_receptor,
                    "nombre_receptor": r.nombre_receptor or "S/N",
                    "tipo": r.tipo_comprobante or "I",
                    "total": total_final,
                    "moneda": r.moneda or "MXN",
                    "metodo_pago": r.metodo_pago or "---",
                    "forma_pago": r.forma_pago or "---",
                    "estatus": estatus_final,
                    "tiene_relacionados": len(reps_all) > 0,
                    "reps_asociados": reps_all,
                    "xml_exists": xml_exists,
                    "pdf_exists": pdf_exists
                    })
            except Exception as e_row:
                print(f"--- ERROR EN FILA {getattr(r, 'uuid', 'Desconocido')} --- : {str(e_row)}")
            
        return output

    except Exception as e:
        print(f"--- ERROR EN COMPROBANTES --- \n{str(e)}")
        raise HTTPException(status_code=500, detail=f"Error de mapeo con el frontend: {str(e)}")

@router.get("/export")
async def export_comprobantes(
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
    db: AsyncSession = Depends(get_db),
    entidad_id: uuid.UUID = Depends(get_active_entidad)
):
    try:
        from datetime import datetime
        query = (
            select(Comprobante)
            .options(selectinload(Comprobante.relacionados))
            .where(Comprobante.entidad_id == entidad_id)
        )
        if fecha_inicio and fecha_inicio.strip():
            query = query.where(Comprobante.fecha_emision >= datetime.fromisoformat(fecha_inicio))
        if fecha_fin and fecha_fin.strip():
            query = query.where(Comprobante.fecha_emision <= datetime.fromisoformat(fecha_fin))
            
        query = query.order_by(Comprobante.fecha_emision.desc())
        result = await db.execute(query)
        rows = result.scalars().all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeceras por bloque Dirección
        writer.writerow([
            # Identidad Fiscal
            "UUID", "Serie", "Folio", "Fecha Emisión/Timbrado", "RFC Emisor", "Nombre Emisor", "RFC Receptor", "Nombre Receptor", "Uso CFDI", "Tipo",
            # Financiero
            "Subtotal", "Descuento", "IVA Trasladado", "Impuestos Retenidos", "Total", "Moneda", "Tipo Cambio", "Método Pago", "Forma Pago",
            # Pagos (REPs)
            "Monto Pago Total", "Fecha Pago", "UUID Relacionado Origen", "Num. Parcialidad", "Saldo Anterior", "Importe Pagado", "Saldo Insoluto",
            # Control SAT
            "Estatus SAT", "Estatus VCORE"
        ])
        
        for r in rows:
            subtotal = float(r.subtotal or r.total or 0)
            descuento = float(r.descuento or 0)
            iva_tras = float(r.total_impuestos_trasladados or 0)
            imp_ret = float(r.total_impuestos_retenidos or 0)
            tipo_cambio = float(r.tipo_cambio or 1.0)
            
            est_int = "Vigente"
            if r.metodo_pago == 'PUE': est_int = "Pagado"
            elif r.metodo_pago == 'PPD':
                if not r.relacionados: est_int = "Pendiente"
                else:
                    tot_pag = sum(float(rel.monto_pagado or 0) for rel in r.relacionados)
                    est_int = "Pagado" if tot_pag >= float(r.total or 0) else "Parcial"
            
            # Subconsulta para tipo P suma para Monto Pago Total jika tipo P
            monto_pago_total = "-"
            if r.tipo_comprobante == 'P':
                monto_pago_total = sum(float(rel.monto_pagado or 0) for rel in r.relacionados)

            core_data = [
                str(r.uuid), r.serie or "", r.folio or "", 
                r.fecha_emision.strftime("%d/%m/%Y") if r.fecha_emision else "",
                r.rfc_emisor, r.nombre_emisor, r.rfc_receptor, r.nombre_receptor,
                "-", r.tipo_comprobante or "I", # Uso CFDI a "-"
                subtotal, descuento, iva_tras, imp_ret, float(r.total or 0), 
                r.moneda if r.moneda and r.moneda.strip() and r.moneda.upper() != "XXX" else "MXN", 
                tipo_cambio, r.metodo_pago or "", r.forma_pago or ""
            ]
            
            sat_data = [r.estatus_sat or "Vigente", est_int]

            if r.relacionados:
                for rel in r.relacionados:
                    rep_data = [
                        monto_pago_total, # Monto Pago Total
                        "-", # Fecha Pago (no hay en relacionados)
                        str(rel.uuid_relacionado), rel.num_parcialidad or "-",
                        float(rel.saldo_insoluto or 0) + float(rel.monto_pagado or 0), # Saldo Anterior
                        float(rel.monto_pagado or 0), # Importe Pagado
                        float(rel.saldo_insoluto or 0) # Saldo Insoluto
                    ]
                    writer.writerow(core_data + rep_data + sat_data)
            else:
                rep_data = ["-", "-", "-", "-", "-", "-", "-"]
                writer.writerow(core_data + rep_data + sat_data)
                
        output.seek(0)
        return StreamingResponse(
            io.StringIO(output.getvalue()), 
            media_type="text/csv", 
            headers={"Content-Disposition": f"attachment; filename=reporte_comprobantes.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar: {str(e)}")

@router.get("/{uuid}/xml")
async def get_comprobante_xml(uuid: str, db: AsyncSession = Depends(get_db)):
    query = select(Comprobante).where(func.lower(cast(Comprobante.uuid, String)) == uuid.lower())
    res = await db.execute(query)
    comp = res.scalars().first()
    
    from src.database.models import Cfdi
    alt_q = select(Cfdi).where(func.lower(Cfdi.uuid) == uuid.lower())
    alt_res = await db.execute(alt_q)
    alt_comp = alt_res.scalars().first()
    
    my_serie = getattr(comp, 'serie', "") if comp else (getattr(alt_comp, 'serie', "") if alt_comp else "")
    my_folio = getattr(comp, 'folio', "") if comp else (getattr(alt_comp, 'folio', "") if alt_comp else "")
    my_tipo = getattr(comp, 'tipo_comprobante', "I") if comp else (getattr(alt_comp, 'tipo_comprobante', "I") if alt_comp else "I")

    from src.services.cfdi_storage import find_cfdi_attachments
    att = find_cfdi_attachments(uuid, my_serie, my_folio, my_tipo)
    
    actual_path = att["xml_path"]
    
    if not actual_path or not os.path.exists(actual_path):
         if alt_comp and alt_comp.xml_file_path and os.path.exists(alt_comp.xml_file_path):
              actual_path = alt_comp.xml_file_path
              
    if not actual_path or not os.path.exists(actual_path):
        import glob
        for pattern in [f"storage/**/{uuid}.xml", f"Operacion_CFDI/**/{uuid}.xml", f"**/{uuid}.xml"]:
            matches = glob.glob(pattern, recursive=True)
            if matches:
                 actual_path = matches[0]
                 break

    if not actual_path or not os.path.exists(actual_path):
        raise HTTPException(status_code=404, detail="Archivo XML no encontrado en almacenamiento histórico o workspace")

    friendly_name = f"{(comp.serie or '') + (comp.folio or uuid)}.xml"
    return FileResponse(path=actual_path, filename=friendly_name)

@router.get("/{uuid}/pdf")
async def get_comprobante_pdf(uuid: str, db: AsyncSession = Depends(get_db)):
    query = select(Comprobante).where(func.lower(cast(Comprobante.uuid, String)) == uuid.lower())
    res = await db.execute(query)
    comp = res.scalars().first()
    
    actual_path = comp.ruta_resguardo if comp and comp.ruta_resguardo else None
    if actual_path:
        if os.path.isdir(actual_path):
            tmp_pth = os.path.join(actual_path, f"{uuid}.pdf")
            actual_path = tmp_pth if os.path.exists(tmp_pth) else None
        else:
            tmp_pth = actual_path.replace('.xml', '.pdf')
            actual_path = tmp_pth if os.path.exists(tmp_pth) else None
    else:
        actual_path = None

    if not actual_path or not os.path.exists(actual_path):
        import glob
        search_paths = [f"storage/**/{uuid}.pdf", f"Operacion_CFDI/**/{uuid}.pdf", f"**/{uuid}.pdf"]
        for pattern in search_paths:
            matches = glob.glob(pattern, recursive=True)
            if matches:
                 actual_path = os.path.abspath(matches[0])
                 break

    alt_comp = None
    if not actual_path or not os.path.exists(actual_path):
        from src.database.models import Cfdi
        alt_q = select(Cfdi).where(func.lower(Cfdi.uuid) == uuid.lower())
        alt_res = await db.execute(alt_q)
        alt_comp = alt_res.scalars().first()

    if not actual_path or not os.path.exists(actual_path):
        from src.services.cfdi_storage import find_cfdi_attachments
        my_serie = getattr(comp, 'serie', "") if comp else (getattr(alt_comp, 'serie', "") if alt_comp else "")
        my_folio = getattr(comp, 'folio', "") if comp else (getattr(alt_comp, 'folio', "") if alt_comp else "")
        my_tipo = getattr(comp, 'tipo_comprobante', "I") if comp else (getattr(alt_comp, 'tipo_comprobante', "I") if alt_comp else "I")
        
        att = find_cfdi_attachments(uuid, my_serie, my_folio, my_tipo)
        if att["pdf_path"]:
             actual_path = att["pdf_path"]

    if not actual_path or not os.path.exists(actual_path):
        if alt_comp and alt_comp.pdf_file_path and os.path.exists(alt_comp.pdf_file_path):
            actual_path = alt_comp.pdf_file_path
        else:
            # Fallback Generación On-the-Fly wkhtmltopdf
            xml_path = None
            if comp and comp.ruta_resguardo:
                 if os.path.exists(comp.ruta_resguardo): xml_path = comp.ruta_resguardo
                 elif os.path.exists(comp.ruta_resguardo.replace('.pdf', '.xml')): xml_path = comp.ruta_resguardo.replace('.pdf', '.xml')
            
            if not xml_path or not os.path.exists(xml_path):
                 import glob
                 xml_matches = glob.glob(f"**/{uuid}.xml", recursive=True)
                 if xml_matches: xml_path = xml_matches[0]
            
            if not xml_path and alt_comp and os.path.exists(alt_comp.xml_file_path):
                 xml_path = alt_comp.xml_file_path
                 
            if xml_path and os.path.exists(xml_path):
                 try:
                      import tempfile
                      dest_pdf = os.path.join(tempfile.gettempdir(), f"{uuid}.pdf")
                      from src.services.pdf_generator import generate_pdf_from_xml
                      
                      from src.database.models import Tenant
                      t_q = await db.execute(select(Tenant).where(Tenant.tenant_id == (comp.entidad_id if comp else alt_comp.tenant_id)))
                      t = t_q.scalar_one_or_none()
                      
                      success = generate_pdf_from_xml(xml_path, dest_pdf, uuid, getattr(t, 'logo_path', ""))
                      if not success or not os.path.exists(dest_pdf):
                           raise HTTPException(status_code=500, detail="Fallo inesperado al generar el PDF nativo con Edge.")
                      
                      return FileResponse(path=dest_pdf, filename=f"{uuid}.pdf")
                 except Exception as e_pdf:
                       raise HTTPException(status_code=500, detail="El PDF no existe en disco y la generación nativa falló: " + str(e_pdf))

            raise HTTPException(status_code=404, detail="Archivo PDF no encontrado en rutas de resguardo y fallo la generación")

    friendly_name = f"{(comp.serie or '') + (comp.folio or uuid)}.pdf" if comp else f"{uuid}.pdf"
    return FileResponse(path=actual_path, filename=friendly_name)

@router.get("/{uuid}")
async def get_comprobante_detail(uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        from src.database.models import CfdiRelacionado
        query = select(Comprobante).where(func.lower(cast(Comprobante.uuid, String)) == uuid.lower())
        res = await db.execute(query)
        comp = res.scalars().first()
        
        if not comp:
            # Intentar buscar en Cfdi table como fallback si es relacionado
            from src.database.models import Cfdi
            alt_q = select(Cfdi).where(func.lower(Cfdi.uuid) == uuid.lower())
            alt_res = await db.execute(alt_q)
            alt_comp = alt_res.scalars().first()
            if alt_comp:
                m_serie = ""
                m_folio = ""
                m_tipo = "I"
                import os
                from src.services.parser.cfdi_parser import CFDIParser
                if hasattr(alt_comp, "xml_file_path") and alt_comp.xml_file_path and os.path.exists(alt_comp.xml_file_path):
                    try:
                        parser = CFDIParser(alt_comp.xml_file_path)
                        m_data = parser.get_metadata()
                        m_serie = m_data.get("serie") or ""
                        m_folio = m_data.get("folio") or ""
                        m_tipo = m_data.get("tipo_comprobante") or "I"
                    except Exception:
                        pass
                return {
                    "uuid": alt_comp.uuid,
                    "serie": m_serie,
                    "folio": m_folio,
                    "tipo_comprobante": m_tipo,
                    "metodo_pago": "---",
                    "forma_pago": "---",
                    "rfc_emisor": alt_comp.rfc_emisor,
                    "rfc_receptor": alt_comp.rfc_receptor,
                    "total": float(alt_comp.total or 0),
                    "descripcion_concepto": "Descargado de repositorio auxiliar"
                }
            raise HTTPException(status_code=404, detail="Comprobante no encontrado")

        # Si es tipo P, sumar asociados para total
        total_final = float(comp.total or 0)
        if comp.tipo_comprobante == 'P':
            sum_q = select(func.sum(CfdiRelacionado.monto_pagado)).where(func.lower(CfdiRelacionado.uuid_padre) == uuid.lower())
            sum_res = await db.execute(sum_q)
            val_pago = sum_res.scalar()
            if val_pago is not None:
                 total_final = float(val_pago)

        # Buscar descripción (de DashCfdiConcept si existe)
        descripcion = "Sin descripción"
        try:
            from src.database.models_dashboard_opt import DashCfdiDocument, DashCfdiConcept
            concept_q = select(DashCfdiConcept.descripcion).distinct().join(DashCfdiDocument).where(
                func.lower(DashCfdiDocument.uuid_fiscal) == uuid.lower()
            )
            concept_res = await db.execute(concept_q)
            first_concept = concept_res.scalars().first()
            if first_concept:
                descripcion = first_concept
        except Exception as e:
            print(f"Error fetching description from DB: {str(e)}")

        # FALLBACK: Extraer del XML si sigue sin descripción
        if descripcion == "Sin descripción" and comp.ruta_resguardo:
            try:
                import xml.etree.ElementTree as ET
                actual_path = comp.ruta_resguardo
                if os.path.isdir(actual_path):
                     actual_path = os.path.join(comp.ruta_resguardo, f"{uuid}.xml")
                elif not actual_path.lower().endswith('.xml'):
                     actual_path = actual_path.replace('.pdf', '.xml')
                     
                if os.path.exists(actual_path):
                    tree = ET.parse(actual_path)
                    root = tree.getroot()
                    ns = {
                        'cfdi': 'http://www.sat.gob.mx/cfd/4',
                        'cfdi33': 'http://www.sat.gob.mx/cfd/3'
                    }
                    # Intentar CFDI 4.0
                    conceptos = root.find('.//cfdi:Conceptos', ns)
                    if conceptos is not None:
                        concept_nodes = conceptos.findall('cfdi:Concepto', ns)
                        if concept_nodes:
                            descripcion = " | ".join([c.get('Descripcion', '') for c in concept_nodes if c.get('Descripcion')])
                    else:
                        # Intentar CFDI 3.3
                        conceptos = root.find('.//cfdi33:Conceptos', ns)
                        if conceptos is not None:
                            concept_nodes = conceptos.findall('cfdi33:Concepto', ns)
                            if concept_nodes:
                                descripcion = " | ".join([c.get('Descripcion', '') for c in concept_nodes if c.get('Descripcion')])
            except Exception as xml_e:
                print(f"Error parsing XML for description: {str(xml_e)}")

        return {
            "uuid": str(comp.uuid),
            "serie": comp.serie or "",
            "folio": comp.folio or "",
            "tipo_comprobante": comp.tipo_comprobante or "I",
            "metodo_pago": comp.metodo_pago or "PUE",
            "forma_pago": comp.forma_pago or "03",
            "rfc_emisor": comp.rfc_emisor,
            "rfc_receptor": comp.rfc_receptor,
            "total": total_final,
            "descripcion_concepto": descripcion
        }
    except Exception as e:
        print(f"--- ERROR EN COMPROBANTE DETAIL --- \n{str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en detalle del comprobante: {str(e)}")