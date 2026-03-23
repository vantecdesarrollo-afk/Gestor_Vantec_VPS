from fastapi import APIRouter, Depends, Form, HTTPException, File, UploadFile
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import os
import shutil
from src.database.session import get_db
from src.database.models import User, Tenant

router = APIRouter(tags=["Administración"])

@router.get("/entidades")
async def list_entidades(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tenant))
    entidades = result.scalars().all()
    return [{
        "id": str(e.tenant_id),
        "rfc": e.rfc,
        "razon_social": e.business_name,
        "is_active": e.is_active,
        "logo_path": e.logo_path or ""
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
async def list_usuarios(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [{
        "id": str(u.user_id),
        "username": u.username,
        "email": u.email,
        "is_active": u.is_active, 
        "is_superadmin": u.is_superadmin
    } for u in users]

@router.put("/usuarios/{user_id}", response_model=UserResponse)
async def update_usuario(
    user_id: uuid.UUID, 
    user_data: UserUpdate, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
         raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user_data.username is not None:
         user.username = user_data.username
    if user_data.email is not None:
         user.email = str(user_data.email) if user_data.email else None
    if user_data.is_active is not None:
         user.is_active = user_data.is_active
    if user_data.is_superadmin is not None:
         user.is_superadmin = user_data.is_superadmin

    await db.commit()
    await db.refresh(user)
    
    return {
        "id": str(user.user_id),
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_superadmin": user.is_superadmin
    }

from fastapi import Form
from typing import Optional
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

from pydantic import BaseModel

class AccessCreate(BaseModel):
    usuario_id: uuid.UUID
    entidad_id: uuid.UUID
    rol: str

@router.post("/accesos")
async def save_access(payload: AccessCreate, db: AsyncSession = Depends(get_db)):
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