from fastapi import APIRouter, Depends
from sqlalchemy import select, func, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.session import get_db
from src.database.models_dashboard_opt import DashCfdiDocument
from src.api.endpoints.auth import get_active_entidad
import uuid
from collections import defaultdict

router = APIRouter(prefix="/api/v1/analytics", tags=["Analítica"])

from typing import Optional
from datetime import datetime

@router.get("/dashboard")
async def get_dashboard(
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    moneda: Optional[str] = None,
    concepto: Optional[str] = None,
    db: AsyncSession = Depends(get_db), 
    entidad_id: uuid.UUID = Depends(get_active_entidad)
):
    try:
        query = select(DashCfdiDocument).where(DashCfdiDocument.tenant_id == entidad_id)
        
        if fecha_inicio:
             query = query.where(DashCfdiDocument.fecha_emision >= datetime.strptime(fecha_inicio, "%Y-%m-%d"))
        if fecha_fin:
             query = query.where(DashCfdiDocument.fecha_emision <= datetime.strptime(fecha_fin + " 23:59:59", "%Y-%m-%d %H:%M:%S"))
        if moneda:
             query = query.where(DashCfdiDocument.moneda == moneda)
        if concepto:
             from src.database.models_dashboard_opt import DashCfdiConcept
             query = query.join(DashCfdiConcept).where(DashCfdiConcept.descripcion == concepto)

        result = await db.execute(query)
        data = result.scalars().all()
        
        ingresos = 0.0
        puntos_grafica = defaultdict(float)

        # Downsampling / Agregación temporal (Evitar colapso / ruido blanco)
        dates_sub = {c.fecha_emision.date() for c in data if c.fecha_emision}
        use_month_grouping = len(dates_sub) > 60

        for c in data:
            monto = float(c.total or 0)
            if c.tipo_comprobante in ['I', 'P']:
                ingresos += monto
                if c.fecha_emision:
                    if use_month_grouping:
                         label = c.fecha_emision.strftime("%m/%Y")
                    else:
                         label = c.fecha_emision.strftime("%d/%m")
                    puntos_grafica[label] += monto

        # Ordenar cronológicamente para evitar gráficas caóticas
        if use_month_grouping:
             sorted_points = sorted(puntos_grafica.items(), key=lambda x: datetime.strptime(x[0], "%m/%Y"))
        else:
             sorted_points = sorted(puntos_grafica.items(), key=lambda x: datetime.strptime(x[0], "%d/%m"))

        facturacion_mensual = [{"mes": k, "total": v} for k, v in sorted_points]

        from src.database.models import CfdiRelacionado
        from src.database.models_dashboard_opt import DashCfdiConcept

        # 1. Conceptos (SELECT DISTINCT) sobre Descripciones
        q_concepts_list = select(DashCfdiConcept.descripcion).distinct().join(DashCfdiDocument).where(DashCfdiDocument.tenant_id == entidad_id)
        res_concepts_list = await db.execute(q_concepts_list)
        conceptos_options = [row[0] for row in res_concepts_list.all() if row[0]]

        # 2. Monedas (SELECT DISTINCT)
        q_monedas = select(DashCfdiDocument.moneda).distinct().where(DashCfdiDocument.tenant_id == entidad_id)
        res_monedas = await db.execute(q_monedas)
        monedas_options = [row[0] for row in res_monedas.all() if row[0]]

        # 3. Top Clientes (Sanitizado)
        q_clientes = select(DashCfdiDocument.nombre_receptor, func.sum(DashCfdiDocument.total)).where(DashCfdiDocument.tenant_id == entidad_id).group_by(DashCfdiDocument.nombre_receptor).order_by(func.sum(DashCfdiDocument.total).desc()).limit(5)
        res_clientes = await db.execute(q_clientes)
        top_clientes = [{"cliente": row[0] if row[0] and row[0].strip() else "Cliente Sin Identificar", "total": float(row[1] or 0)} for row in res_clientes.all()]

        # 4. PPD Pendientes Lógica (VCORE-BRIDGE)
        from sqlalchemy import cast, String
        subquery = select(cast(CfdiRelacionado.uuid_relacionado, String))
        q_ppd = select(func.count()).select_from(DashCfdiDocument).where(
            DashCfdiDocument.tenant_id == entidad_id,
            DashCfdiDocument.metodo_pago == 'PPD',
            cast(DashCfdiDocument.uuid_fiscal, String).notin_(subquery)
        )
        res_ppd = await db.execute(q_ppd)
        ppd_pending_count = res_ppd.scalar() or 0

        return {
            "total_ingresos": round(ingresos, 2),
            "total_egresos": 0.0,
            "total_documentos": len(data),
            "facturacion_mensual": facturacion_mensual,
            "conceptos_options": conceptos_options,
            "monedas_options": monedas_options,
            "envio_stats": {"exito": 0, "pendiente": 0},
            "ppd_pending_count": ppd_pending_count,
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
            "top_clientes": []
        }