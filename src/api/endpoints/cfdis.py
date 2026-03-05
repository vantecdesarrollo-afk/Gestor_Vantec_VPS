from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os
import uuid
from datetime import datetime
import defusedxml.ElementTree as ET
import aiofiles
from src.database.session import get_db
from src.database.models import Cfdi
from pydantic import BaseModel
from uuid import UUID

router = APIRouter(prefix="/api/v1/cfdis", tags=["CFDIs"])

# Esquema de salida (Pydantic)
class CfdiRead(BaseModel):
    cfdi_id: UUID
    uuid: str
    rfc_emisor: str
    rfc_receptor: str
    issue_date: datetime
    total: float
    version: str
    status: str
    xml_file_path: str
    pdf_file_path: str | None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[CfdiRead])
async def get_all_cfdis(db: AsyncSession = Depends(get_db)):
    """
    Obtiene todos los CFDIs a los que el tenant autenticado tiene acceso.
    El aislamiento ocurre en PostgreSQL vía RLS.
    """
    result = await db.execute(select(Cfdi))
    return result.scalars().all()

@router.post("/upload", response_model=CfdiRead, status_code=status.HTTP_201_CREATED)
async def upload_cfdi(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint de Carga de XML (Categoría 5 - Vantec).
    
    1. Extrae tenant_id del token (vía middleware).
    2. Parsea el XML de forma segura (XXE Protection).
    3. Almacena el archivo en la ruta lógica: /storage/{tenant_id}/{YYYY}/{MM}/{UUID}.xml
    4. Registra el CFDI en PostgreSQL.
    """
    
    # 1. Seguridad: Obtener tenant_id del contexto de la petición
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="No se pudo identificar el tenant_id en el token."
        )

    # Solo aceptamos XML
    if not file.filename.lower().endswith(".xml"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten archivos XML."
        )

    # 2. Lectura asíncrona del contenido
    content = await file.read()
    
    try:
        # 3. Parseo Seguro (defusedxml)
        root = ET.fromstring(content)
        
        # Manejo dinámico de Namespaces para CFDI 3.3/4.0 y TFD
        namespaces = {
            'cfdi': root.tag.split('}')[0].strip('{'),
            'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
        }
        
        # Extracción de Atributos del Comprobante
        version = root.get('Version') or root.get('version')
        fecha_str = root.get('Fecha') or root.get('fecha')
        total_str = root.get('Total') or root.get('total')
        
        # Extracción de RFCs (Emisor y Receptor)
        emisor = root.find('.//cfdi:Emisor', namespaces)
        rfc_emisor = emisor.get('Rfc') if emisor is not None else None
        
        receptor = root.find('.//cfdi:Receptor', namespaces)
        rfc_receptor = receptor.get('Rfc') if receptor is not None else None
        
        # Extracción del UUID (Timbre Fiscal Digital)
        tfd = root.find('.//tfd:TimbreFiscalDigital', namespaces)
        cfdi_uuid = tfd.get('UUID') if tfd is not None else None
        
        # Validación de campos obligatorios
        if not all([cfdi_uuid, rfc_emisor, rfc_receptor, fecha_str, total_str]):
            raise ValueError("El archivo XML no es un CFDI válido o le faltan atributos clave (UUID, RFCs, etc).")

        # 4. Procesamiento de Fecha y Rutas
        fecha_dt = datetime.fromisoformat(fecha_str)
        year = str(fecha_dt.year)
        month = f"{fecha_dt.month:02d}"
        
        # Estructura: /storage/{tenant_id}/{YYYY}/{MM}
        base_storage = "/storage"
        target_dir = os.path.join(base_storage, str(tenant_id), year, month)
        
        # Crear directorios si no existen
        os.makedirs(target_dir, exist_ok=True)
        
        final_path = os.path.join(target_dir, f"{cfdi_uuid}.xml")

        # 5. Escritura Asíncrona en Disco (Expediente Virtual)
        async with aiofiles.open(final_path, mode='wb') as f:
            await f.write(content)

        # 6. Persistencia en Base de Datos
        new_cfdi = Cfdi(
            tenant_id=tenant_id,
            uuid=cfdi_uuid,
            rfc_emisor=rfc_emisor,
            rfc_receptor=rfc_receptor,
            issue_date=fecha_dt,
            total=float(total_str),
            version=version,
            xml_file_path=final_path,
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
            detail=f"Error al procesar el CFDI: {str(e)}"
        )
