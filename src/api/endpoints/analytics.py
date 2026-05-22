from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
import io
import pandas as pd
from sqlalchemy.orm import selectinload
from typing import Optional
from sqlalchemy import select, func, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.session import get_db
from src.api.endpoints.auth import get_active_entidad
import uuid
from collections import defaultdict
from typing import Optional
from datetime import datetime
import os

# --- BLINDAJE L3 ---
from src.core.license_core import VantecSystemState

router = APIRouter(prefix="/api/v1/analytics", tags=["Analítica"])

# [VCORE L6] RUTAS RELATIVAS (ANTI-CRASH)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
UPLOAD_DIR = os.path.join(BASE_DIR, "Operacion_CFDI", "Upload_Universal")

@router.get("/dashboard")
async def get_dashboard(
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    moneda: Optional[str] = None,
    concepto: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db), 
    entidad_id: uuid.UUID = Depends(get_active_entidad)
):
    try:
        from src.database.models import Comprobante, CfdiConcepto, CfdiRelacionado
        from sqlalchemy import or_, and_, cast, String

        if not entidad_id:
            upload_files = 0
            try:
                if os.path.exists(UPLOAD_DIR):
                    upload_files = len([f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))])
            except: pass
            
            return {
                "total_ingresos": 0.0,
                "total_egresos": 0.0,
                "total_documentos": upload_files,
                "facturacion_mensual": [],
                "conceptos_options": [],
                "monedas_options": [],
                "envio_stats": {"exito": 0, "pendiente": 0},
                "ppd_pending_count": 0,
                "orphans_count": 0,
                "top_clientes": []
            }

        query = select(Comprobante)
        query = query.where(Comprobante.entidad_id == entidad_id)

        if search:
            search_raw = search.strip()
            search_clean = search_raw.replace('-', '').replace(' ', '')
            search_numeric = "".join(filter(str.isdigit, search_clean)).lstrip('0')
            folio_db_clean = func.ltrim(func.trim(func.coalesce(Comprobante.folio, '')), '0')
            serie_db_clean = func.trim(func.coalesce(Comprobante.serie, ''))
            
            search_conditions = [
                func.concat(serie_db_clean, folio_db_clean).ilike(f"%{search_clean.lstrip('0')}%"),
                cast(Comprobante.uuid, String).ilike(f"%{search_raw}%")
            ]
            if search_numeric:
                search_conditions.append(folio_db_clean.ilike(f"%{search_numeric}%"))
            query = query.where(or_(*search_conditions))

        if fecha_inicio:
             query = query.where(Comprobante.fecha_emision >= datetime.strptime(fecha_inicio, "%Y-%m-%d"))
        if fecha_fin:
             query = query.where(Comprobante.fecha_emision <= datetime.strptime(fecha_fin + " 23:59:59", "%Y-%m-%d %H:%M:%S"))

        if moneda and moneda != 'Todas' and moneda != 'ALL':
             query = query.where(Comprobante.moneda == moneda)
        if concepto:
             query = query.join(CfdiConcepto).where(CfdiConcepto.descripcion == concepto)

        result = await db.execute(query)
        data = result.scalars().all()
        
        ingresos = 0.0
        egresos = 0.0
        puntos_grafica = defaultdict(float)

        dates_sub = {c.fecha_emision.date() for c in data if c.fecha_emision}
        use_month_grouping = len(dates_sub) > 60

        for c in data:
            monto = float(c.total or 0)
            if c.tipo_comprobante == 'I':
                ingresos += monto
                if c.fecha_emision:
                    if use_month_grouping:
                         label = c.fecha_emision.strftime("%m/%Y")
                    else:
                         label = c.fecha_emision.strftime("%d/%m")
                    puntos_grafica[label] += monto
            elif c.tipo_comprobante == 'E':
                egresos += monto

        if use_month_grouping:
             sorted_points = sorted(puntos_grafica.items(), key=lambda x: datetime.strptime(x[0], "%m/%Y"))
        else:
             sorted_points = sorted(puntos_grafica.items(), key=lambda x: datetime.strptime(x[0], "%d/%m"))

        facturacion_mensual = [{"mes": k, "total": v} for k, v in sorted_points]

        q_concepts_list = select(CfdiConcepto.descripcion).distinct().join(Comprobante)
        if entidad_id:
             q_concepts_list = q_concepts_list.where(Comprobante.entidad_id == entidad_id)
        
        if concepto and len(concepto) >= 3:
             q_concepts_list = q_concepts_list.where(CfdiConcepto.descripcion.ilike(f"%{concepto}%"))
             
        q_concepts_list = q_concepts_list.limit(20)
        res_concepts_list = await db.execute(q_concepts_list)
        conceptos_options = [row[0] for row in res_concepts_list.all() if row[0]]

        q_monedas = select(Comprobante.moneda).distinct()
        if entidad_id:
             q_monedas = q_monedas.where(Comprobante.entidad_id == entidad_id)
        res_monedas = await db.execute(q_monedas)
        monedas_options = [row[0] for row in res_monedas.all() if row[0]]

        q_clientes = select(Comprobante.nombre_receptor, func.sum(Comprobante.total))
        if entidad_id:
             q_clientes = q_clientes.where(Comprobante.entidad_id == entidad_id)
        q_clientes = q_clientes.where(Comprobante.tipo_comprobante == 'I')
        q_clientes = q_clientes.group_by(Comprobante.nombre_receptor).order_by(func.sum(Comprobante.total).desc()).limit(5)
        res_clientes = await db.execute(q_clientes)
        top_clientes = [{"cliente": row[0] if row[0] and row[0].strip() else "Cliente Sin Identificar", "total": float(row[1] or 0)} for row in res_clientes.all()]

        from sqlalchemy import text
        # [VCORE L6] Auto-refresh materialized view to ensure pending PPD counts are up-to-date
        try:
            await db.execute(text("REFRESH MATERIALIZED VIEW v_ppd_semaforo_status"))
            await db.commit()
        except Exception as e:
            print(f"⚠️ [DASHBOARD] Warning: failed to refresh materialized view: {e}")

        q_ppd = select(func.count()).select_from(text("v_ppd_semaforo_status"))
        q_ppd = q_ppd.where(text("saldo_insoluto >= 1.00"))
        if entidad_id:
            q_ppd = q_ppd.where(text("entidad_id = :e_id")).params(e_id=entidad_id)
            
        res_ppd = await db.execute(q_ppd)
        ppd_pending_count = res_ppd.scalar() or 0

        q_orphans = select(func.count()).select_from(Comprobante).where(
            Comprobante.orphan_payment == True
        )
        if entidad_id:
             q_orphans = q_orphans.where(Comprobante.entidad_id == entidad_id)
        res_orphans = await db.execute(q_orphans)
        orphans_count = res_orphans.scalar() or 0

        return {
            "total_ingresos": round(ingresos, 2),
            "total_egresos": round(egresos, 2),
            "total_documentos": len(data),
            "facturacion_mensual": facturacion_mensual,
            "conceptos_options": conceptos_options,
            "monedas_options": monedas_options,
            "envio_stats": {"exito": 0, "pendiente": 0},
            "ppd_pending_count": ppd_pending_count,
            "orphans_count": orphans_count,
            "top_clientes": top_clientes
        }

    except Exception as e:
        import traceback
        print(f"--- ANALYTICS ERROR --- \n{str(e)}")
        traceback.print_exc()
        return {
            "total_ingresos": 0.0,
            "total_egresos": 0.0,
            "total_documentos": 0,
            "facturacion_mensual": [],
            "conceptos_options": [],
            "envio_stats": {"exito": 0, "pendiente": 0},
            "ppd_pending_count": 0,
            "orphans_count": 0,
            "top_clientes": []
        }

@router.get("/sabana_atomica")
async def get_sabana_atomica_report(
    version: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    entidad_id: uuid.UUID = Depends(get_active_entidad)
):
    # --- CERROJO L3 VANTEC ---
    if VantecSystemState.IS_RESTRICTED:
        raise HTTPException(status_code=403, detail="🔒 MODO RESTRINGIDO: El periodo de evaluación de reportes ha finalizado. Adquiera una licencia para habilitar la descarga.")

    if not entidad_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=428, detail="CONTEXTO_RFC_OBLIGATORIO")

    try:
        from src.services.report_service import ReportService
        from fastapi.responses import StreamingResponse
        import io
        import csv

        service = ReportService()
        data = await service.get_sabana_atomica(str(entidad_id), db, version)

        output = io.StringIO()
        output.write('\ufeff')
        writer = csv.DictWriter(output, fieldnames=[
            "parent_uuid", "folio", "fecha", "rfc_emisor", "rfc_receptor", 
            "tipo", "moneda", "version_cfdi", "version_pago", "origen_dato",
            "regimen_fiscal_receptor", "tipo_cambio", "detalle", "importe", 
            "naturaleza", "uuid_relacionado", "total_auditado_mxn",
            "parcialidad", "saldo_anterior", "monto_pagado", "saldo_insoluto"
        ])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

        output.seek(0)
        filename = f"Sabana_Atomica_{version or 'Global'}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        from fastapi import HTTPException
        print(f"--- REPORT ERROR --- \n{str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al generar Sábana Atómica: {str(e)}")

@router.get("/export")
async def export_data(
    format: str = Query("xlsx"),
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    moneda: Optional[str] = None,
    concepto: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    entidad_id: uuid.UUID = Depends(get_active_entidad)
):
    # --- CERROJO L3 VANTEC ---
    if VantecSystemState.IS_RESTRICTED:
        raise HTTPException(status_code=403, detail="🔒 MODO RESTRINGIDO: El periodo de evaluación de reportes ha finalizado. Adquiera una licencia para habilitar la descarga.")

    try:
        from src.database.models import Comprobante, CfdiConcepto, CfdiRelacionado
        from sqlalchemy import or_, select, cast, String
        import pandas as pd
        import io
        from fastapi.responses import StreamingResponse
        from fastapi import HTTPException
        from datetime import datetime
        
        if not fecha_inicio and not fecha_fin and not search:
            from dateutil.relativedelta import relativedelta
            fecha_inicio_dt = datetime.now() - relativedelta(months=6)
            fecha_inicio = fecha_inicio_dt.strftime("%Y-%m-%d")
        
        query = select(Comprobante).options(
             selectinload(Comprobante.relacionados)
        ).where(Comprobante.entidad_id == entidad_id)
        
        if search:
            search_raw = search.strip()
            search_clean = search_raw.replace('-', '').replace(' ', '')
            folio_db_clean = func.ltrim(func.trim(func.coalesce(Comprobante.folio, '')), '0')
            serie_db_clean = func.trim(func.coalesce(Comprobante.serie, ''))
            
            query = query.where(or_(
                func.concat(serie_db_clean, folio_db_clean).ilike(f"%{search_clean.lstrip('0')}%"),
                cast(Comprobante.uuid, String).ilike(f"%{search_raw}%")
            ))
            
        if fecha_inicio:
            query = query.where(Comprobante.fecha_emision >= datetime.strptime(fecha_inicio, "%Y-%m-%d"))
        if fecha_fin:
            query = query.where(Comprobante.fecha_emision <= datetime.strptime(fecha_fin + " 23:59:59", "%Y-%m-%d %H:%M:%S"))
            
        if moneda and moneda != 'Todas' and moneda != 'ALL':
            query = query.where(Comprobante.moneda == moneda)
            
        if concepto:
            query = query.join(CfdiConcepto).where(CfdiConcepto.descripcion == concepto)
            
        result = await db.execute(query.order_by(Comprobante.fecha_emision.desc()))
        rows = result.scalars().all()

        q_rel = select(CfdiRelacionado).join(Comprobante).where(Comprobante.entidad_id == entidad_id)
        res_rel = await db.execute(q_rel)
        all_rels = res_rel.scalars().all()
        
        payments_map = defaultdict(float)
        relations_map = defaultdict(list)
        
        uuid_to_folio = {str(r.uuid).upper(): f"{r.serie or ''}{r.folio or ''}".strip() for r in rows}

        for rel in all_rels:
            invoice_uuid = str(rel.uuid_relacionado).upper()
            payments_map[invoice_uuid] += float(rel.monto_pagado or 0)
            
            pago_uuid = str(rel.cfdi_id).upper()
            pago_folio = uuid_to_folio.get(pago_uuid, "S/F")
            relations_map[invoice_uuid].append(f"{pago_folio} | {pago_uuid}")

        columns = [
            "UUID", "Folio", "Fecha", "Emisor", "Receptor", "Tipo", "Moneda", 
            "Monto Real", "Total Comprobante (Auditado)", "Subtotal", 
            "Método Pago", "Estatus SAT", "ESTATUS VCORE", "Pagos/Relaciones"
        ]

        if format == 'xlsx':
            data_list = []
            for r in rows:
                r_uuid = str(r.uuid).upper()
                total = float(r.total or 0)
                monto_pagado = payments_map.get(r_uuid, 0.0)
                estatus_vcore = "PAGADO" if (total - monto_pagado) <= 0.01 else "PENDIENTE"
                
                data_list.append({
                    "UUID": r_uuid,
                    "Folio": f"{r.serie or ''}{r.folio or ''}".strip(),
                    "Fecha": r.fecha_emision.strftime("%Y-%m-%d") if r.fecha_emision else "",
                    "Emisor": r.rfc_emisor,
                    "Receptor": r.rfc_receptor,
                    "Tipo": r.tipo_comprobante,
                    "Moneda": r.moneda,
                    "Monto Real": float(r.subtotal or 0),
                    "Total Comprobante (Auditado)": total,
                    "Subtotal": float(r.subtotal or 0),
                    "Método Pago": r.metodo_pago or "PPD",
                    "Estatus SAT": r.estatus_sat or "Vigente",
                    "ESTATUS VCORE": estatus_vcore,
                    "Pagos/Relaciones": ", ".join(relations_map.get(r_uuid, [])) if r.tipo_comprobante == 'I' else "N/A"
                })

            df = pd.DataFrame(data_list)
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sábana_Maestra_VCore')
                workbook = writer.book
                worksheet = writer.sheets['Sábana_Maestra_VCore']
                
                header_format = workbook.add_format({'bold': True, 'bg_color': '#1E3A5F', 'font_color': 'white'})
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                for i, col in enumerate(df.columns):
                    column_len = max(df[col].astype(str).str.len().max(), len(col)) + 2
                    worksheet.set_column(i, i, column_len)

            output.seek(0)
            filename = f"VCore_Sabana_Real_{datetime.now().strftime('%Y%m%d')}.xlsx"
            
            return StreamingResponse(
                output,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Cache-Control": "no-cache"
                }
            )

        else:
            async def csv_generator():
                yield '\ufeff'
                import csv
                output_str = io.StringIO()
                writer = csv.DictWriter(output_str, fieldnames=columns)
                writer.writeheader()
                yield output_str.getvalue()
                output_str.truncate(0)
                output_str.seek(0)

                for r in rows:
                    r_uuid = str(r.uuid).upper()
                    total = float(r.total or 0)
                    monto_pagado = payments_map.get(r_uuid, 0.0)
                    estatus_vcore = "PAGADO" if (total - monto_pagado) <= 0.01 else "PENDIENTE"
                    
                    row_dict = {
                        "UUID": r_uuid,
                        "Folio": f"{r.serie or ''}{r.folio or ''}".strip(),
                        "Fecha": r.fecha_emision.strftime("%Y-%m-%d") if r.fecha_emision else "",
                        "Emisor": r.rfc_emisor,
                        "Receptor": r.rfc_receptor,
                        "Tipo": r.tipo_comprobante,
                        "Moneda": r.moneda,
                        "Monto Real": float(r.subtotal or 0),
                        "Total Comprobante (Auditado)": total,
                        "Subtotal": float(r.subtotal or 0),
                        "Método Pago": r.metodo_pago or "PPD",
                        "Estatus SAT": r.estatus_sat or "Vigente",
                        "ESTATUS VCORE": estatus_vcore,
                        "Pagos/Relaciones": ", ".join(relations_map.get(r_uuid, [])) if r.tipo_comprobante == 'I' else "N/A"
                    }
                    writer.writerow(row_dict)
                    yield output_str.getvalue()
                    output_str.truncate(0)
                    output_str.seek(0)

            filename = f"VCore_Sabana_Stream_{datetime.now().strftime('%Y%m%d')}.csv"
            
            return StreamingResponse(
                csv_generator(),
                media_type="text/csv; charset=utf-8-sig",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Cache-Control": "no-cache"
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))