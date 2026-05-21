from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import uuid

from src.database.session import get_db
from src.database.models import EntidadSMTPConfig, Tenant
from fastapi import Request
import jwt
from src.core.config import settings

async def get_current_superadmin(request: Request):
    """
    [ES] Dependencia para validar superadmin en v1.0.0 o administradores locales de empresa.
    El middleware ya valida la autenticación. El front filtra la pestaña.
    """
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        token = request.cookies.get("access_token")
        
    if not token:
        raise HTTPException(status_code=401, detail="Token ausente en pasarela SMTP")
        
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # 1. Si es SuperAdmin, acceso completo
        if payload.get("is_superadmin") is True:
            return True
            
        # 2. Si no es SuperAdmin, verificar si es ADMIN del tenant_id en la ruta
        tenant_id = request.path_params.get("tenant_id")
        if tenant_id:
            entidades = payload.get("entidades", [])
            for e in entidades:
                if str(e.get("id")).lower() == str(tenant_id).lower() and e.get("rol") == "ADMIN":
                    return True
                    
        raise HTTPException(status_code=403, detail="Requiere rol SuperAdmin o Administrador de la empresa")
    except HTTPException as he:
        raise he
    except Exception:
        raise HTTPException(status_code=401, detail="Fallo de autenticación en SMTP")


router = APIRouter(prefix="/api/v1/smtp", tags=["Configuración SMTP"])

class SmtpConfigResponse(BaseModel):
    host: str
    port: int
    username: str
    from_address: str | None = None
    security_type: str
    authentication_type: str
    has_password: bool

class SmtpConfigUpdate(BaseModel):
    host: str
    port: int
    username: str
    from_address: str | None = None
    password: str | None = None
    security_type: str = "STARTTLS"
    authentication_type: str = "LOGIN"

@router.get("/{tenant_id}", response_model=SmtpConfigResponse)
async def get_smtp_config(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_superadmin)
):
    try:
        query = select(EntidadSMTPConfig).where(EntidadSMTPConfig.entidad_id == tenant_id)
        result = await db.execute(query)
        config = result.scalars().first()
        
        if not config:
            # Devolver estructura vacía para hidratar formulario sin romper
            return {
                "host": "",
                "port": 587,
                "username": "",
                "from_address": "",
                "security_type": "STARTTLS",
                "authentication_type": "LOGIN",
                "has_password": False
            }
            
        print("[GET_SMTP_DEBUG] Devolviendo config existente.")
        return {
            "host": config.host or "",
            "port": config.port or 587,
            "username": config.username or "",
            "from_address": config.from_address or "",
            "security_type": config.security_type or "STARTTLS",
            "authentication_type": config.authentication_type or "LOGIN",
            "has_password": bool(config.password_encrypted)
        }
    except Exception as e:
        import traceback
        print("\n[GET_SMTP_ERROR] EXCEPCIÓN DETECTADA:")
        traceback.print_exc()
        raise e

@router.post("/{tenant_id}")
async def save_smtp_config(
    tenant_id: uuid.UUID,
    payload: SmtpConfigUpdate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_superadmin)
):
    # Verificar que el tenant exista
    tenant_query = select(Tenant).where(Tenant.tenant_id == tenant_id)
    tenant_result = await db.execute(tenant_query)
    tenant = tenant_result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    query = select(EntidadSMTPConfig).where(EntidadSMTPConfig.entidad_id == tenant_id)

    result = await db.execute(query)
    config = result.scalars().first()
    
    if config:
        # Actualizar
        config.host = payload.host
        config.port = payload.port
        config.username = payload.username
        config.from_address = payload.from_address
        config.security_type = payload.security_type
        config.authentication_type = payload.authentication_type
        
        # Regla: Solo actualizar password si viene uno válido
        if payload.password and payload.password.strip():
            config.password_encrypted = payload.password
    else:
        # Crear
        if not payload.password or not payload.password.strip():
            raise HTTPException(status_code=400, detail="La contraseña es requerida para la primera configuración.")
            
        config = EntidadSMTPConfig(
            entidad_id=tenant_id,
            host=payload.host,
            port=payload.port,
            username=payload.username,
            from_address=payload.from_address,
            password_encrypted=payload.password,
            security_type=payload.security_type,
            authentication_type=payload.authentication_type
        )
        db.add(config)
        
    try:
        await db.commit()
        return {"status": "success", "message": "Configuración SMTP guardada correctamente"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar config SMTP: {str(e)}")

import smtplib

@router.post("/{tenant_id}/test")
async def test_smtp_config(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_superadmin)
):
    query = select(EntidadSMTPConfig).where(EntidadSMTPConfig.entidad_id == tenant_id)
    result = await db.execute(query)
    config = result.scalars().first()
    
    if not config:
         raise HTTPException(status_code=404, detail="Configuración SMTP no encontrada")

    try:
         if config.security_type == 'SSL':
              server = smtplib.SMTP_SSL(config.host, config.port, timeout=10)
         else:
              server = smtplib.SMTP(config.host, config.port, timeout=10)
              if config.security_type == 'STARTTLS':
                   server.starttls()

         if config.authentication_type != 'NONE' and config.password_encrypted:
              server.login(config.username, config.password_encrypted)

         server.quit()
         return {"status": "success", "message": "Conexión SMTP exitosa (250 OK)"}
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Falla SMTP: {str(e)}")