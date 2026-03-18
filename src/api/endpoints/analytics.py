from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select, func, cast, String
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.session import get_db
from src.database.models import Comprobante, CfdiRelacionado
from src.api.endpoints.auth import get_active_entidad
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/v1/analytics", tags=["Analítica"])

@router.get("/dashboard")
async def get_dashboard_analytics(
    request: Request,
    moneda: str = Query(None),
    concepto: str = Query(None),
    fecha_inicio: str = Query(None),
    fecha_fin: str = Query(None),
    db: AsyncSession = Depends(get_db),
    entidad_id: uuid.UUID = Depends(get_active_entidad)
):
    try:
        query = select(Comprobante).where(Comprobante.entidad_id == entidad_id)
        
        if fecha_inicio:
            try:
                 query = query.where(Comprobante.fecha_emision >= datetime.strptime(fecha_inicio, "%Y-%m-%d"))
            except: pass
        if fecha_fin:
            try:
                 query = query.where(Comprobante.fecha_emision <= datetime.strptime(f"{fecha_fin} 23:59:59", "%Y-%m-%d %H:%M:%S"))
            except: pass

        result = await db.execute(query)
        data = result.scalars().all()
        
        # Filtrado Base
        filtered_data = []
        page_uuids = [str(c.uuid).lower() for c in data]
        
        # Mapas rápidos en memoria
        uuid_to_tipo = {str(c.uuid).lower(): c.tipo_comprobante for c in data}
        
        # RELACIONES BIDIRECCIONALES (Fix para Pagos Huérfanos en Dashboard)
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

        conceptos_found = set() # Omitido temporalmente por rendimiento (no leemos el disco)
        monedas_found = {"MXN", "USD", "EUR"} 

        # Procesamiento de Data
        for c in data:
            c_uuid_lower = str(c.uuid).lower()
            tipo_comp = c.tipo_comprobante or "I"
            
            # Construir relaciones resueltas
            mis_relaciones = rels_map.get(c_uuid_lower, [])
            total_monto_pago = sum(float(r.monto_pagado or 0) for r in mis_relaciones)
            
            # Calibrar Total: Si es pago (P), el total real es la suma de los montos relacionados
            resolved_total = total_monto_pago if tipo_comp == 'P' and total_monto_pago > 0 else float(c.total or 0)

            filtered_data.append({
                 "uuid": c_uuid_lower,
                 "total": resolved_total,
                 "tipo_comprobante": tipo_comp,
                 "metodo_pago": c.metodo_pago,
                 "rfc_receptor": c.rfc_receptor,
                 "fecha_emision": c.fecha_emision
            })

        data = filtered_data
        
        # Cálculos de Negocio
        ingresos = sum(item["total"] for item in data if item["tipo_comprobante"].upper() == 'I')
        egresos = sum(item["total"] for item in data if item["tipo_comprobante"].upper() == 'E')
        
        # Conteo de Pendientes PPD (Evaluando pagos parciales)
        ppd_pendientes_count = 0
        for item in data:
            if item["tipo_comprobante"].upper() == 'I' and item["metodo_pago"] == 'PPD':
                monto_pagado_a_esta_factura = sum(
                    float(r.monto_pagado or 0) for r in rels_map.get(item["uuid"], []) 
                    if str(r.uuid_padre).lower() == item["uuid"]
                )
                if monto_pagado_a_esta_factura < item["total"]:
                    ppd_pendientes_count += 1

        # Top Clientes
        clientes_dict = {}
        for item in data:
            if item["tipo_comprobante"].upper() == 'I':
                rfc = item["rfc_receptor"] or "N/A"
                clientes_dict[rfc] = clientes_dict.get(rfc, 0.0) + item["total"]
        
        top_clientes = []
        for rfc, monto in sorted(clientes_dict.items(), key=lambda x: x[1], reverse=True)[:5]:
            top_clientes.append({"rfc_receptor": rfc, "total_monto": monto})

        # Histórico
        historico_temp = {}
        for c in data:
            if c.get("tipo_comprobante") == 'I' and c.get("fecha_emision"):
                key = (c["fecha_emision"].year, c["fecha_emision"].month)
                historico_temp[key] = historico_temp.get(key, 0.0) + float(c.get("total") or 0)
                
        facturacion_mensual = []
        meses_nombres = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}
        for k in sorted(historico_temp.keys()):
            year, month = k
            mes_str = meses_nombres.get(month, "N/A")
            label = f"{mes_str} '{str(year)[2:]}"
            facturacion_mensual.append({"mes": label, "total": historico_temp[k]})

        return {
            "total_ingresos": ingresos,
            "total_egresos": egresos,
            "total_documentos": len(data),
            "ppd_pending_count": ppd_pendientes_count,
            "top_clientes": top_clientes,
            "facturacion_mensual": facturacion_mensual,
            "envio_stats": {"exito": len(data), "pendiente": 0},
            "monedas_options": list(monedas_found), 
            "conceptos_options": [] # Omitido por rendimiento
        }
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error en Dashboard: {str(e)}")

# ... (El endpoint de exportación /export se mantiene igual por ahora para no romper dependencias) ...
@router.get("/export")
async def export_analytics(
    request: Request,
    fecha_inicio: str = Query(None),
    fecha_fin: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    entidad_id = getattr(request.state, "tenant_id", None)
    """
    [ES] Exporta reporte Excel de CFDIs con aislamiento Multi-tenant estricto.
    """
    try:
        from src.database.models import Comprobante
        from fastapi.responses import StreamingResponse
        import openpyxl
        from io import BytesIO
        from sqlalchemy import select

        query = select(Comprobante).where(Comprobante.entidad_id == entidad_id)
        result = await db.execute(query)
        data = result.scalars().all()
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Reporte CFDI"
        
        headers = [
            "UUID", "Serie", "Folio", "Fecha Emisión", "Tipo", 
            "RFC Emisor", "RFC Receptor", 
            "Método Pago", "Forma Pago",
            "Total", "Estatus"
        ]
        ws.append(headers)

        for c in data:
            ws.append([
                str(c.uuid), c.serie or "", c.folio or "", 
                c.fecha_emision.strftime("%Y-%m-%d %H:%M:%S") if c.fecha_emision else "N/A",
                c.tipo_comprobante or "I", c.rfc_emisor, c.rfc_receptor,
                c.metodo_pago or "", c.forma_pago or "",
                float(c.total or 0), c.status or ""
            ])

        stream = BytesIO()

        wb.save(stream)
        stream.seek(0)

        headers_resp = {
            'Content-Disposition': 'attachment; filename="reporte_cfdi_v100.xlsx"',
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        return StreamingResponse(stream, headers=headers_resp, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error en Exportación: {str(e)}")