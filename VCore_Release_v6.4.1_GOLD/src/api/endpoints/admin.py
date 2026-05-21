from fastapi import APIRouter, Depends, Form, HTTPException, File, UploadFile
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import os
import shutil
from datetime import datetime
from src.database.session import get_db
from src.database.models import User, Tenant, FinancialAnomalyLog
from src.api.endpoints.auth import get_current_user

router = APIRouter(prefix="/api/v1/admin", tags=["Administración"])

import re

def validate_password_strength(password: str):
    """
    Min 8 chars, 1 uppercase, 1 number, 1 special char.
    """
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres.")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos una mayúscula.")
    if not re.search(r"[0-9]", password):
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos un número.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos un carácter especial.")

@router.get("/entidades")
async def list_entidades(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tenant))
    entidades = result.scalars().all()
    return [{
        "id": str(e.tenant_id),
        "rfc": e.rfc,
        "razon_social": e.business_name,
        "is_active": e.is_active,
        "logo_path": e.logo_path if (not e.logo_path or e.logo_path.startswith("/") or e.logo_path.startswith("http")) else f"/static/logos/{e.logo_path}"
    } for e in entidades]

@router.post("/entidades")
async def create_entidad(
    rfc: str = Form(...),
    razon_social: str = Form(...),
    logo_file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    existing = await db.execute(select(Tenant).where(Tenant.rfc == rfc))
    if existing.scalar_one_or_none():
         raise HTTPException(status_code=400, detail="El RFC ya está registrado")

    logo_path = None
    if logo_file and logo_file.filename:
         os.makedirs("static/logos", exist_ok=True)
         filename = f"{uuid.uuid4()}_{logo_file.filename}"
         logo_path = f"/static/logos/{filename}"
         with open(f"static/logos/{filename}", "wb") as buffer:
              shutil.copyfileobj(logo_file.file, buffer)

    nuevo_tenant = Tenant(
        rfc=rfc,
        business_name=razon_social,
        logo_path=logo_path,
        is_active=True
    )
    db.add(nuevo_tenant)
    await db.commit()
    await db.refresh(nuevo_tenant)
    
    return {"status": "success", "message": "Empresa creada exitosamente", "id": str(nuevo_tenant.tenant_id)}

from src.schemas.user import UserUpdate, UserResponse
from fastapi import HTTPException

@router.get("/usuarios")
async def list_usuarios(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(User)
    
    # AISLAMIENTO L6: Un Admin local no puede ver a un Super Admin (Directiva v84.1)
    if not current_user.is_superadmin:
        query = query.where(User.is_superadmin == False)
        
    result = await db.execute(query)
    users = result.scalars().all()
    return [{
        "id": str(u.user_id),
        "username": u.username,
        "email": u.email,
        "is_active": u.is_active, 
        "is_superadmin": u.is_superadmin,
        "rol": u.rol or "VISOR"
    } for u in users]

@router.put("/usuarios/{user_id}", response_model=UserResponse)
async def update_usuario(
    user_id: uuid.UUID, 
    user_data: UserUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
         raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # PROTECCIÓN DE MUTACIÓN L6: Solo un SuperAdmin toca a otro SuperAdmin
    if user.is_superadmin and not current_user.is_superadmin:
         raise HTTPException(status_code=403, detail="VCore Security: No tiene autoridad sobre perfiles globales")

    if user_data.is_superadmin is True and not current_user.is_superadmin:
         raise HTTPException(status_code=403, detail="VCore Security: No puede promover usuarios a Super Admin")

    if user_data.username is not None:
         user.username = user_data.username
    if user_data.email is not None:
         user.email = str(user_data.email) if user_data.email else None
    if user_data.is_active is not None:
         user.is_active = user_data.is_active
    if user_data.is_superadmin is not None:
         user.is_superadmin = user_data.is_superadmin
    if user_data.rol is not None:
         user.rol = str(user_data.rol).upper()

    await db.commit()
    await db.refresh(user)
    
    return {
        "id": str(user.user_id),
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_superadmin": user.is_superadmin,
        "rol": user.rol
    }

from src.api.endpoints.auth import get_password_hash

from pydantic import BaseModel, EmailStr

class UsuarioCreate(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None
    is_superadmin: bool = False
    rol: Optional[str] = "VISOR"

@router.post("/usuarios")
async def create_usuario(
    payload: UsuarioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # PROTECCIÓN DE CREACIÓN L6: Un Admin local no puede crear SuperAdmins
    if payload.is_superadmin and not current_user.is_superadmin:
         raise HTTPException(status_code=403, detail="VCore Security: No tiene permisos para crear perfiles globales")

    existing = await db.execute(select(User).where(User.username == payload.username))
    if existing.scalar_one_or_none():
         raise HTTPException(status_code=400, detail="El usuario ya existe")

    validate_password_strength(payload.password)

    new_user = User(
        user_id=uuid.uuid4(),
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        email=str(payload.email) if payload.email else None,
        is_superadmin=payload.is_superadmin,
        rol=str(payload.rol).upper() if payload.rol else "VISOR",
        is_active=True
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return {"status": "success", "message": "Usuario creado", "id": str(new_user.user_id)}

from src.database.models import SysUserRole

@router.patch("/entidades/{entidad_id}")
async def update_entidad(
    entidad_id: uuid.UUID,
    rfc: Optional[str] = Form(None),
    razon_social: Optional[str] = Form(None),
    is_active: Optional[str] = Form(None),
    logo_file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Tenant).where(Tenant.tenant_id == entidad_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
         raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    if rfc:
         tenant.rfc = rfc
    if razon_social:
         tenant.business_name = razon_social
    if is_active is not None:
         tenant.is_active = is_active.lower() == 'true'
         
    if logo_file and logo_file.filename:
         os.makedirs("static/logos", exist_ok=True)
         filename = f"{uuid.uuid4()}_{logo_file.filename}"
         tenant.logo_path = f"/static/logos/{filename}"
         with open(f"static/logos/{filename}", "wb") as buffer:
              shutil.copyfileobj(logo_file.file, buffer)

    await db.commit()
    return {"status": "success", "message": "Empresa actualizada"}

class AccessCreate(BaseModel):
    usuario_id: uuid.UUID
    entidad_id: uuid.UUID
    rol: str

@router.post("/accesos")
async def save_access(
    payload: AccessCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # BLINDAJE L6: Validación de Autoridad (Directiva v84.2)
    if not current_user.is_superadmin:
        # Verificar si el solicitante es ADMIN en la entidad destino
        auth_query = select(SysUserRole).where(
            SysUserRole.usuario_id == current_user.user_id,
            SysUserRole.entidad_id == payload.entidad_id,
            SysUserRole.rol == 'ADMIN'
        )
        auth_res = await db.execute(auth_query)
        if not auth_res.scalars().first():
             raise HTTPException(status_code=403, detail="No tiene autoridad administrativa sobre esta entidad")

    # Verificar que usuario y tenant existan
    user_res = await db.execute(select(User).where(User.user_id == payload.usuario_id))
    if not user_res.scalar_one_or_none():
         raise HTTPException(status_code=404, detail="Usuario no encontrado")
         
    tenant_res = await db.execute(select(Tenant).where(Tenant.tenant_id == payload.entidad_id))
    if not tenant_res.scalar_one_or_none():
         raise HTTPException(status_code=404, detail="Empresa no encontrada")

    # Verificar si ya existe el acceso para actualizarlo o crearlo
    existing = await db.execute(select(SysUserRole).where(
        SysUserRole.usuario_id == payload.usuario_id,
        SysUserRole.entidad_id == payload.entidad_id
    ))
    access = existing.scalars().first()
    
    if access:
         access.rol = payload.rol
    else:
         access = SysUserRole(
             usuario_id=payload.usuario_id,
             entidad_id=payload.entidad_id,
             rol=payload.rol
         )
         db.add(access)

    await db.commit()
    return {"status": "success", "message": "Permiso vinculado correctamente"}

@router.get("/audit/financial-anomalies")
async def list_financial_anomalies(
     entidad_id: Optional[uuid.UUID] = None,
     db: AsyncSession = Depends(get_db)
):
    from src.database.models import Comprobante
    
    # Query con Join para obtener datos humanos
    # Usamos outerjoin por si el documento fue borrado o es una inconsistencia de UUID
    from sqlalchemy.orm import aliased
    comp = aliased(Comprobante)
    
    query = (
        select(FinancialAnomalyLog, comp.folio, comp.nombre_receptor, comp.rfc_receptor)
        .outerjoin(comp, FinancialAnomalyLog.uuid_documento == comp.uuid)
        .order_by(FinancialAnomalyLog.fecha_deteccion.desc())
    )
    
    if entidad_id:
         query = query.where(FinancialAnomalyLog.entidad_id == entidad_id)
    
    result = await db.execute(query)
    rows = result.all()
    
    def humanize_anomaly(tipo, detail):
        if "GHOST" in tipo or "ORPHAN" in tipo:
            return f"Documento recuperado exitosamente (SSoT Sync)"
        if "DUPLICATE" in tipo:
            return f"Alerta: Intento de duplicidad bloqueado"
        if "ADN_FAILURE" in tipo:
            return f"Error de ADN Fiscal: {detail}"
        return detail

    return [{
         "id": r[0].id,
         "entidad_id": str(r[0].entidad_id),
         "uuid_documento": str(r[0].uuid_documento),
         "folio": r[1] or "S/N",
         "cliente": r[2] or "N/A",
         "rfc": r[3] or "N/A",
         "tipo_anomalia": r[0].tipo_anomalia,
         "detalle_humano": humanize_anomaly(r[0].tipo_anomalia, r[0].detalle),
         "fecha": r[0].fecha_deteccion.strftime("%Y-%m-%d %H:%M:%S") if r[0].fecha_deteccion else "---",
         "estatus": r[0].estatus_anomalia
    } for r in rows]

from src.api.endpoints.auth import get_current_superadmin

@router.get("/audit/logs")
async def read_audit_log(
    entidad_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_superadmin) 
):
    """
    Soporte Modo Neutral: Lee [FECHA]_watcher_global.log por defecto.
    Si se pasa entidad_id, lee el log particular de esa empresa del día.
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    try:
        if not entidad_id:
             # Modo Neutral: Log Global Diario (Huérfanos / Invalid ADN)
             log_filename = f"{date_str}_watcher_global.log"
             log_path = os.path.join("Operacion_CFDI", "logs", log_filename)
        else:
             # Modo Empresa: Log Particular Diario (Duplicados VCORE)
             res = await db.execute(select(Tenant).where(Tenant.tenant_id == entidad_id))
             tenant = res.scalar_one_or_none()
             if not tenant: 
                  raise HTTPException(status_code=404, detail="Empresa no encontrada")
             log_filename = f"{date_str}_empresa_audit.log"
             log_path = os.path.join("Operacion_CFDI", "Files", tenant.rfc, "logs", log_filename)

        if not os.path.exists(log_path):
             return {"filename": os.path.basename(log_path), "content": f"Sin registros de auditoría para el día {date_str}."}
             
        with open(log_path, "r", encoding="utf-8") as f:
             lines = f.readlines()
             content = "".join(lines[-500:])
        
        return {"filename": os.path.basename(log_path), "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error leyendo log diario: {str(e)}")