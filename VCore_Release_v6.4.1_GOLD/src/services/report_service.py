from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ReportService:
    """
    Servicio Maestro de Reporteo (Sábana Atómica)
    Actualizado: Directiva L6 v5.1 (Blindaje y Retro-compatibilidad)
    Cumplimiento mandatorio de codificación UTF-8-SIG y sanitización de datos.
    """

    async def get_sabana_atomica(self, tenant_id: str, db: AsyncSession, version_filter: str = None):
        """
        Genera el dataset aplanado (One row per concept/payment-impact).
        Directiva L6 v5.1: Blindaje Universal.
        """
        # 🛡️ Blindaje L6 v5.3: Construcción Dinámica para Seguridad Paramétrica
        base_where = "c.entidad_id = :tenant_id"
        v_clause = " AND c.version = :v_filter" if version_filter else ""
        
        # Query Aplanado: Conceptos (Ingresos/Egresos) + Impactos (Pagos)
        query_str = f"""
            -- 1. Capa de Conceptos (Ingresos, Egresos, Traslados, Nómina)
            SELECT 
                c.uuid as parent_uuid,
                c.folio,
                c.fecha_emision,
                c.rfc_emisor,
                c.rfc_receptor,
                c.tipo_comprobante,
                c.moneda,
                1.0 as tipo_cambio,
                COALESCE(con.descripcion, 'Concepto Único / Global') as detalle_linea,
                COALESCE(con.importe, c.total) as importe_linea,
                'CONCEPTO' as naturaleza_linea,
                NULL as uuid_relacionado,
                (COALESCE(con.importe, c.total) * 1.0) as total_auditado_mxn,
                c.version as version_cfdi,
                'N/A' as version_pago,
                CASE WHEN c.xml_path IS NOT NULL THEN 'XML_Original' ELSE 'PDF_Ingested' END as origen_dato,
                c.regimen_fiscal_receptor,
                0 AS parcialidad,
                0 AS saldo_anterior,
                0 AS monto_pagado,
                0 AS saldo_insoluto
            FROM comprobantes c
            LEFT JOIN cfdi_conceptos con ON c.uuid = con.cfdi_id
            WHERE {base_where} AND c.tipo_comprobante != 'P'
            {v_clause}

            UNION ALL

            -- 2. Capa de Impactos de Pago (Complementos de Pago)
            SELECT 
                c.uuid as parent_uuid,
                c.folio,
                c.fecha_emision,
                c.rfc_emisor,
                c.rfc_receptor,
                c.tipo_comprobante,
                c.moneda,
                1.0 as tipo_cambio,
                'Impacto en Factura: ' || rel.uuid_relacionado as detalle_linea,
                rel.monto_pagado as importe_linea,
                'PAGO_IMPACTO' as naturaleza_linea,
                rel.uuid_relacionado as uuid_relacionado,
                (rel.monto_pagado * 1.0) as total_auditado_mxn,
                c.version as version_cfdi,
                CASE WHEN c.version = '3.3' THEN '1.0' ELSE '2.0' END as version_pago,
                CASE WHEN c.xml_path IS NOT NULL THEN 'XML_Original' ELSE 'PDF_Ingested' END as origen_dato,
                c.regimen_fiscal_receptor,
                CAST(rel.num_parcialidad AS integer) as parcialidad,
                rel.saldo_anterior as saldo_anterior,
                rel.monto_pagado as monto_pagado,
                rel.saldo_insoluto as saldo_insoluto
            FROM comprobantes c
            INNER JOIN cfdi_relacionados rel ON c.uuid = rel.cfdi_id
            WHERE {base_where} AND c.tipo_comprobante = 'P'
            {v_clause}
            
            ORDER BY fecha_emision DESC
        """
        
        params = {"tenant_id": tenant_id}
        if version_filter:
            params["v_filter"] = version_filter
            
        result = await db.execute(text(query_str), params)
        dataset = []
        for row in result:
            dataset.append({
                "parent_uuid": str(row.parent_uuid),
                "folio": row.folio,
                "fecha": row.fecha_emision.strftime('%Y-%m-%d %H:%M:%S') if row.fecha_emision else "N/A",
                "rfc_emisor": row.rfc_emisor,
                "rfc_receptor": row.rfc_receptor,
                "tipo": row.tipo_comprobante,
                "moneda": row.moneda,
                "version_cfdi": row.version_cfdi,
                "version_pago": row.version_pago,
                "origen_dato": row.origen_dato,
                "tipo_cambio": float(row.tipo_cambio or 1.0),
                "detalle": row.detalle_linea,
                "importe": float(row.importe_linea or 0),
                "naturaleza": row.naturaleza_linea,
                "uuid_relacionado": row.uuid_relacionado,
                "total_auditado_mxn": round(float(row.total_auditado_mxn or 0), 2),
                "regimen_fiscal_receptor": row.regimen_fiscal_receptor or "N/A",
                "parcialidad": row.parcialidad,
                "saldo_anterior": float(row.saldo_anterior or 0),
                "monto_pagado": float(row.monto_pagado or 0),
                "saldo_insoluto": float(row.saldo_insoluto or 0)
            })
            
        return dataset
