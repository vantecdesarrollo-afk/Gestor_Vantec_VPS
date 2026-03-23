from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os
import uuid
from datetime import datetime
import defusedxml.ElementTree as ET
import aiofiles
from pydantic import BaseModel
from uuid import UUID

# Importaciones locales
from src.database.session import get_db
from src.database.models import Cfdi # Importación directa desde el modelo limpio

router = APIRouter(prefix="/api/v1/cfdis", tags=["CFDIs"])

# Esquema de salida (Pydantic) alineado al modelo de base de datos
class CfdiRead(BaseModel):
    cfdi_id: UUID
    uuid: str
    rfc_emisor: str | None
    rfc_receptor: str | None
    issue_date: datetime | None
    total: float | None
    version: str | None
    status: str | None
    xml_file_path: str | None
    pdf_file_path: str | None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[CfdiRead])
async def get_all_cfdis(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Obtiene todos los CFDIs aislados por tenant.
    """
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token inválido: No se encontró tenant_id en contexto."
        )
    result = await db.execute(select(Cfdi).where(Cfdi.tenant_id == tenant_id))
    return result.scalars().all()

@router.post("/upload", response_model=CfdiRead, status_code=status.HTTP_201_CREATED)
async def upload_cfdi(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # 1. Obtener tenant_id del estado (inyectado por el middleware)
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token inválido: No se encontró tenant_id."
        )

    if not file.filename.lower().endswith(".xml"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten archivos XML."
        )

    content = await file.read()
    
    try:
        # 2. Parseo Seguro
        root = ET.fromstring(content)
        
        # Namespaces dinámicos
        ns_url = root.tag.split('}')[0].strip('{')
        namespaces = {
            'cfdi': ns_url,
            'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
        }
        
        # Extracción de datos
        version = root.get('Version') or root.get('version')
        fecha_str = root.get('Fecha') or root.get('fecha')
        total_str = root.get('Total') or root.get('total')
        
        emisor = root.find('.//cfdi:Emisor', namespaces)
        rfc_emisor = emisor.get('Rfc') if emisor is not None else None
        
        receptor = root.find('.//cfdi:Receptor', namespaces)
        rfc_receptor = receptor.get('Rfc') if receptor is not None else None
        
        tfd = root.find('.//tfd:TimbreFiscalDigital', namespaces)
        cfdi_uuid = tfd.get('UUID') if tfd is not None else None
        
        if not cfdi_uuid:
            raise ValueError("El XML no tiene un UUID válido (Timbre Fiscal).")

        # 3. Preparar rutas de almacenamiento
        fecha_dt = datetime.fromisoformat(fecha_str) if fecha_str else datetime.now()
        storage_path = f"static/storage/{tenant_id}/{fecha_dt.year}/{fecha_dt.month:02d}"
        os.makedirs(storage_path, exist_ok=True)
        
        final_file_path = os.path.join(storage_path, f"{cfdi_uuid}.xml")

        # 4. Guardar archivo
        async with aiofiles.open(final_file_path, mode='wb') as f:
            await f.write(content)

        # 5. Guardar en DB (Usando los nombres del modelo Cfdi)
        new_cfdi = Cfdi(
            tenant_id=tenant_id,
            uuid=cfdi_uuid,
            rfc_emisor=rfc_emisor,
            rfc_receptor=rfc_receptor,
            issue_date=fecha_dt,
            total=float(total_str) if total_str else 0.0,
            version=version,
            xml_file_path=final_file_path,
            status="VALID"
        )
        
        db.add(new_cfdi)
        await db.commit()
        await db.refresh(new_cfdi)
        
        return new_cfdi

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error procesando CFDI: {str(e)}"
        )