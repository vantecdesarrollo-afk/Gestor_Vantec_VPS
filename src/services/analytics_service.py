from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from src.database.models import Comprobante, CfdiRelacionado
from uuid import UUID

class AnalyticsService:
    """
    Servicio de Analítica para el Dashboard de Vantec.
    Servicio de Analítica para el Dashboard de Vantec.
    Garantiza aislamiento por entidad_id.
    """

    async def get_kpis(self, tenant_id: UUID, db: AsyncSession, fecha_inicio: str = None, fecha_fin: str = None):
        """
        Retorna los KPIs principales de la entidad fiscal.
        Blindaje contra nulos y división por cero.
        """
        base_filters = [Comprobante.entidad_id == tenant_id]
        if fecha_inicio:
            base_filters.append(Comprobante.issue_date >= f"{fecha_inicio} 00:00:00")
        if fecha_fin:
            base_filters.append(Comprobante.issue_date <= f"{fecha_fin} 23:59:59")

        # 1. Total de documentos (Solo Válidos)
        count_query = select(func.count(Comprobante.cfdi_id)).where(*base_filters, Comprobante.status == 'VALID')
        total_docs = (await db.execute(count_query)).scalar() or 0

        # 2. Sumatoria monetaria (Ingresos vs Pagos)
        # Ingresos: Tipo 'I' (Ingreso)
        ingresos_query = select(func.sum(Comprobante.total)).where(*base_filters, Comprobante.tipo_comprobante == 'I', Comprobante.status == 'VALID')
        total_ingresos = (await db.execute(ingresos_query)).scalar() or 0.0
        
        # Pagos: Tipo 'P' (Pago / Complemento de Pago)
        pagos_query = select(func.sum(Comprobante.total)).where(*base_filters, Comprobante.tipo_comprobante == 'P', Comprobante.status == 'VALID')
        total_pagos = (await db.execute(pagos_query)).scalar() or 0.0

        # 3. Top 5 Clientes (Solo Ingresos)
        top_clientes_query = (
            select(Comprobante.rfc_receptor, func.sum(Comprobante.total).label("total_monto"))
            .where(*base_filters, Comprobante.tipo_comprobante == 'I')
            .group_by(Comprobante.rfc_receptor)
            .order_by(desc("total_monto"))
            .limit(5)
        )
        top_clientes_result = (await db.execute(top_clientes_query)).all()
        top_clientes = [
            {"rfc_receptor": row.rfc_receptor, "total_monto": float(row.total_monto or 0)}
            for row in top_clientes_result
        ]

        # 4. Estadísticas de Envío (Donut Chart)
        from src.database.models import EmailQueue
        success_count_query = select(func.count(EmailQueue.id)).where(EmailQueue.entidad_id == tenant_id, EmailQueue.estado == 'SENT')
        pending_count_query = select(func.count(EmailQueue.id)).where(EmailQueue.entidad_id == tenant_id, EmailQueue.estado.in_(['PENDING', 'FAILED']))
        
        envios_exito = (await db.execute(success_count_query)).scalar() or 0
        envios_pendientes = (await db.execute(pending_count_query)).scalar() or 0

        # 5. Variación Mensual (Solo Ingresos)
        monthly_query = (
            select(
                func.to_char(Comprobante.issue_date, 'YYYY-MM').label("mes"),
                func.sum(Comprobante.total).label("total")
            )
            .where(*base_filters, Comprobante.tipo_comprobante == 'I')
            .group_by("mes")
            .order_by(desc("mes"))
            .limit(2)
        )
        monthly_result = (await db.execute(monthly_query)).all()
        
        mes_actual_total = 0.0
        mes_anterior_total = 0.0
        variacion = 0.0

        if len(monthly_result) >= 1:
            mes_actual_total = float(monthly_result[0].total or 0.0)
        
        if len(monthly_result) >= 2:
            mes_anterior_total = float(monthly_result[1].total or 0.0)
            if mes_anterior_total > 0:
                variacion = ((mes_actual_total - mes_anterior_total) / mes_anterior_total) * 100

        # 6. Alerta PPD
        exists_subquery = select(1).where(
            func.lower(CfdiRelacionado.uuid_relacionado) == func.lower(Comprobante.uuid),
            CfdiRelacionado.tipo_relacion == 'PAGO'
        ).correlate(Comprobante)
        
        ppd_pending_query = select(func.count(Comprobante.cfdi_id)).where(
            Comprobante.entidad_id == tenant_id,
            Comprobante.metodo_pago == 'PPD',
            Comprobante.tipo_comprobante == 'I',
            ~exists_subquery.exists()
        )
        
        res_ppd = await db.execute(ppd_pending_query)
        ppd_pending_count = res_ppd.scalar() or 0

        return {
            "total_documentos": int(total_docs or 0),
            "monto_total": float(total_ingresos or 0.0), # Mantenemos por compatibilidad UI actual
            "total_ingresos": float(total_ingresos or 0.0),
            "total_pagos": float(total_pagos or 0.0),
            "envio_stats": {
                "exito": envios_exito,
                "pendiente": envios_pendientes
            },
            "variacion_mensual": round(float(variacion), 2),
            "top_clientes": top_clientes or [],
            "ppd_pending_count": ppd_pending_count,
            "facturacion_mensual": [
                {"mes": row.mes, "total": float(row.total or 0.0)} 
                for row in reversed(monthly_result)
            ] if monthly_result else []
        }
