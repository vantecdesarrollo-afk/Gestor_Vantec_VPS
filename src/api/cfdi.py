from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.session import get_db
from src.models.cfdi import CfdiMetadata
from src.schemas.cfdi import CfdiCreate
from src.services.cfdi_storage import construir_ruta_archivo
import os

router = APIRouter(prefix="/api/v1/cfdi", tags=["Gestión CFDI"])

@router.post("/registrar", response_model=CfdiCreate, status_code=status.HTTP_201_CREATED)
async def registrar_cfdi(
    cfdi_data: CfdiCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Registra los metadatos de un CFDI en la base de datos.
    Evita duplicados por UUID.
    """
    # Verificar si ya existe el UUID
    query = select(CfdiMetadata).where(CfdiMetadata.uuid == cfdi_data.uuid)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El CFDI con UUID {cfdi_data.uuid} ya está registrado."
        )

    # Crear el nuevo registro
    new_cfdi = CfdiMetadata(**cfdi_data.dict())
    
    db.add(new_cfdi)
    try:
        await db.commit()
        await db.refresh(new_cfdi)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar en la base de datos: {str(e)}"
        )
    
    return new_cfdi

@router.get("/descargar/{uuid}/{formato}")
async def descargar_cfdi(
    uuid: str,
    formato: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Consulta el CFDI por UUID, construye su ruta jerárquica y retorna el archivo.
    """
    # Consultar metadatos en la DB
    query = select(CfdiMetadata).where(CfdiMetadata.uuid == uuid)
    result = await db.execute(query)
    cfdi = result.scalar_one_or_none()
    
    if not cfdi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el CFDI con UUID {uuid}."
        )

    # Construir la ruta física
    file_path = construir_ruta_archivo(
        tenant_id=str(cfdi.tenant_id),
        rfc_emisor=cfdi.rfc_emisor,
        fecha_emision=cfdi.fecha_emision,
        uuid=cfdi.uuid,
        formato=formato
    )

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El archivo físico {formato.upper()} no existe para el UUID {uuid}."
        )

    return FileResponse(
        path=file_path,
        filename=f"{uuid}.{formato}",
        media_type="application/octet-stream"
    )
