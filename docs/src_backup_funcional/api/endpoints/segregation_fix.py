from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, func, cast, String, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from src.database.session import get_db
from src.database.models import Comprobante

router = APIRouter(prefix="/api/v1/final-fix", tags=["Final Fix"])

@router.get("/")
@router.get("")
async def get_comprobantes_segregated(
    request: Request,
    limit: int = Query(100),
    offset: int = Query(0),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    # 1. FUERZA BRUTA PARA ENTIDAD
    active_id = getattr(request.state, "entidad_id", None) or request.headers.get("X-Entidad-ID")
    
    if not active_id:
         raise HTTPException(status_code=428, detail="CONTEXTO_RFC_OBLIGATORIO")

    target_str = str(active_id).strip().lower()

    query = select(Comprobante).options(selectinload(Comprobante.relacionados))
    
    # 2. FILTRADO MANDATORIO POR STRING
    query = query.where(cast(Comprobante.entidad_id, String) == target_str)

    if search:
        s = f"%{search}%"
        query = query.where(
            or_(
                Comprobante.folio.ilike(s),
                Comprobante.serie.ilike(s),
                cast(Comprobante.uuid, String).ilike(s)
            )
        )
    
    query = query.order_by(Comprobante.fecha_emision.desc())
    
    count_q = select(func.count()).select_from(query.subquery())
    total_records = await db.scalar(count_q)

    result = await db.execute(query.limit(limit).offset(offset))
    rows = result.scalars().all()

    return {
        "resultados": rows,
        "total_registros_bd": total_records,
        "offset": offset,
        "limit": limit,
        "debug_active_id": str(active_id),
        "debug_target_str": target_str
    }
