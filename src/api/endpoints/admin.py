from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
import uuid
import os

from src.database.session import get_db
from src.database.models import Usuario, EntidadFiscal, UsuarioEntidadAcceso
from src.api.endpoints.auth import get_current_superadmin, get_password_hash
from pydantic import BaseModel, EmailStr

router = APIRouter(tags=["Administración (SuperAdmin)"])

# --- Esquemas Pydantic para Admin ---

class EntidadCreate(BaseModel):
    rfc: str
    razon_social: str
    logo_url: str | None = None

class UsuarioCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_superadmin: bool = False

class AccesoCreate(BaseModel):
    usuario_id: uuid.UUID
    entidad_id: uuid.UUID
    rol: str # 'ADMIN', 'OPERADOR', 'VISOR'

# --- Endpoints de Empresas (EntidadFiscal) ---

@router.get("/entidades")
async def list_entidades(
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(get_current_superadmin)
):
    result = await db.execute(select(EntidadFiscal))
    return result.scalars().all()

import aiofiles

async def save_logo(entidad_id: uuid.UUID, logo_file: UploadFile) -> str:
    """Helper para guardar logo físico."""
    upload_dir = "static/img/logos"
    os.makedirs(upload_dir, exist_ok=True)
    
    ext = os.path.splitext(logo_file.filename)[1] or ".png"
    file_name = f"{entidad_id}_logo{ext}"
    file_path = os.path.join(upload_dir, file_name)
    
    async with aiofiles.open(file_path, "wb") as f:
        content = await logo_file.read()
        await f.write(content)
    
    return f"/static/img/logos/{file_name}"

@router.post("/entidades", status_code=status.HTTP_201_CREATED)
async def create_entidad(
    rfc: str = Form(...),
    razon_social: str = Form(...),
    logo_file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(get_current_superadmin)
):
    new_entidad = EntidadFiscal(rfc=rfc, razon_social=razon_social)
    db.add(new_entidad)
    
    try:
        await db.flush()
        if logo_file:
            new_entidad.logo_url = await save_logo(new_entidad.id, logo_file)

        await db.commit()
        await db.refresh(new_entidad)
        return new_entidad
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al crear: {str(e)}")

from src.database.models import Usuario, EntidadFiscal, UsuarioEntidadAcceso, BitacoraAuditoria

# ... (rest of imports)

@router.put("/entidades/{entidad_id}")
async def update_entidad(
    entidad_id: uuid.UUID,
    rfc: str = Form(...),
    razon_social: str = Form(...),
    is_active: str = Form("true"),
    logo_file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(get_current_superadmin)
):
    query = select(EntidadFiscal).where(EntidadFiscal.id == entidad_id)
    result = await db.execute(query)
    entidad = result.scalar_one_or_none()
    
    if not entidad:
        raise HTTPException(status_code=404, detail="Entidad no encontrada")

    # Conversión segura de booleanos desde Form
    active_bool = is_active.lower() == "true"
    
    entidad.rfc = rfc
    entidad.razon_social = razon_social
    entidad.is_active = active_bool
    
    try:
        if logo_file:
            entidad.logo_url = await save_logo(entidad.id, logo_file)

        # Auditoría
        audit = BitacoraAuditoria(
            usuario_id=admin.id,
            entidad_id=entidad.id,
            accion="ADMIN_UPDATE_ENTITY",
            detalle={"rfc": rfc, "is_active": active_bool}
        )
        db.add(audit)

        await db.commit()
        await db.refresh(entidad)
        return entidad
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al actualizar: {str(e)}")

@router.patch("/entidades/{entidad_id}")
async def patch_entidad(
    entidad_id: uuid.UUID,
    razon_social: str | None = Form(None),
    is_active: str | None = Form(None),
    logo_file: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(get_current_superadmin)
):
    query = select(EntidadFiscal).where(EntidadFiscal.id == entidad_id)
    result = await db.execute(query)
    entidad = result.scalar_one_or_none()
    
    if not entidad:
        raise HTTPException(status_code=404, detail="Entidad no encontrada")

    changes = {}
    if razon_social is not None:
        entidad.razon_social = razon_social
        changes["razon_social"] = razon_social
    
    if is_active is not None:
        active_bool = is_active.lower() == "true"
        print(f"[!] Admin API -> Parchando is_active: {is_active} (Bool: {active_bool})")
        entidad.is_active = active_bool
        changes["is_active"] = active_bool
    
    try:
        if logo_file:
            entidad.logo_url = await save_logo(entidad.id, logo_file)
            changes["logo_updated"] = True

        # Auditoría
        audit = BitacoraAuditoria(
            usuario_id=admin.id,
            entidad_id=entidad.id,
            accion="ADMIN_PATCH_ENTITY",
            detalle=changes
        )
        db.add(audit)

        await db.commit()
        await db.refresh(entidad)
        return entidad
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al parchar: {str(e)}")

# --- Endpoints de Usuarios ---

@router.get("/usuarios")
async def list_usuarios(
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(get_current_superadmin)
):
    result = await db.execute(select(Usuario))
    return result.scalars().all()

@router.post("/usuarios", status_code=status.HTTP_201_CREATED)
async def create_usuario(
    payload: UsuarioCreate,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(get_current_superadmin)
):
    hashed_pwd = get_password_hash(payload.password)
    new_user = Usuario(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed_pwd,
        is_superadmin=payload.is_superadmin
    )
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        return {"id": new_user.id, "email": new_user.email, "status": "Created"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al crear usuario: {str(e)}")

# --- Matriz de Acceso (RBAC) ---

@router.post("/accesos")
async def assign_acceso(
    payload: AccesoCreate,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(get_current_superadmin)
):
    # Upsert logic for access
    query = select(UsuarioEntidadAcceso).where(
        UsuarioEntidadAcceso.usuario_id == payload.usuario_id,
        UsuarioEntidadAcceso.entidad_id == payload.entidad_id
    )
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        existing.rol = payload.rol
    else:
        new_acceso = UsuarioEntidadAcceso(**payload.model_dump())
        db.add(new_acceso)

    try:
        await db.commit()
        return {"status": "Success", "message": f"Rol {payload.rol} asignado correctamente."}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error en matriz de acceso: {str(e)}")

@router.get("/smtp_test/{tenant_id}")
async def smtp_test_endpoint(tenant_id: uuid.UUID):
    return {
        "host": "test_admin",
        "port": 587,
        "username": "test",
        "from_address": "",
        "security_type": "STARTTLS",
        "authentication_type": "LOGIN",
        "has_password": False
    }
