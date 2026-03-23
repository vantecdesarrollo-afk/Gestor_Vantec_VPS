from fastapi import APIRouter, Depends, HTTPException, status, Security, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import jwt
import uuid
from passlib.context import CryptContext
from src.database.session import get_db
from src.database.models import User, Tenant
from src.core.config import settings

# 1. Configuración de Seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"]) # ESTA LÍNEA FALTABA
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# 2. Endpoints
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    if not getattr(user, "is_active", True):
        raise HTTPException(status_code=403, detail="Cuenta suspendida o inactiva")
    
    # 1. Determinar si es Superadmin
    is_superadmin = getattr(user, "is_superadmin", False)
    
    # 2. Cargar Entidades Asociadas (Si es superadmin, listar todas)
    entidades = []
    from src.database.models import SysUserRole
    if is_superadmin:
        e_res = await db.execute(select(Tenant))
        entidades = e_res.scalars().all()
        entidades_json = [{
             "id": str(e.tenant_id),
             "rfc": e.rfc,
             "razon_social": e.business_name,
             "rol": "ADMIN",
             "logo_url": e.logo_path or ""
        } for e in entidades]
    else:
        # standard user: solo su tenant_id
        e_res = await db.execute(select(Tenant).where(Tenant.tenant_id == user.tenant_id))
        entidades = e_res.scalars().all()
        entidades_json = []
        for e in entidades:
             role_res = await db.execute(select(SysUserRole.rol).where(SysUserRole.usuario_id == user.user_id, SysUserRole.entidad_id == e.tenant_id))
             role_str = role_res.scalar() or "VISOR"
             entidades_json.append({
                  "id": str(e.tenant_id),
                  "rfc": e.rfc,
                  "razon_social": e.business_name,
                  "rol": role_str.upper(),
                  "logo_url": e.logo_path or ""
             })

    # Generar token con los IDs correctos del modelo User
    access_token = create_access_token(
        data={
            "sub": str(user.user_id), 
            "username": user.username,
            "entidad_id": str(user.tenant_id), 
            "tenant_id": str(user.tenant_id),
            "is_superadmin": is_superadmin,
            "entidades": entidades_json
        }
    )
    
    user.last_login = datetime.utcnow()
    await db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: AsyncSession = Depends(get_db)):
    try:
        from src.database.models import SysUserRole
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id: raise HTTPException(status_code=401)
        
        result = await db.execute(select(User).where(User.user_id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()
        if not user or not getattr(user, "is_active", True): raise HTTPException(status_code=403)
             
        is_superadmin = getattr(user, "is_superadmin", False)
        if is_superadmin:
            e_res = await db.execute(select(Tenant))
            entidades_json = [{"id": str(e.tenant_id), "rfc": e.rfc, "razon_social": e.business_name, "rol": "ADMIN", "logo_url": e.logo_path or ""} for e in e_res.scalars().all()]
        else:
            e_res = await db.execute(select(SysUserRole).where(SysUserRole.usuario_id == user.user_id))
            entidades_json = []
            for role in e_res.scalars().all():
                 t_res = await db.execute(select(Tenant).where(Tenant.tenant_id == role.entidad_id))
                 t = t_res.scalar_one_or_none()
                 if t:
                     entidades_json.append({"id": str(t.tenant_id), "rfc": t.rfc, "razon_social": t.business_name, "rol": role.rol.upper(), "logo_url": t.logo_path or ""})
                 
        access_token = create_access_token(data={"sub": str(user.user_id), "username": user.username, "entidad_id": str(user.tenant_id), "tenant_id": str(user.tenant_id), "is_superadmin": is_superadmin, "entidades": entidades_json})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Error refreshing token: " + str(e))


# 3. Dependencias de Seguridad
async def get_active_entidad(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id:
            res = await db.execute(select(User).where(User.user_id == uuid.UUID(user_id)))
            user = res.scalar_one_or_none()
            if user and not getattr(user, "is_active", True):
                raise HTTPException(status_code=403, detail="Cuenta suspendida o inactiva")

        # AISLAMIENTO ESTRUCTURAL MULTI-TENANT
        req_entidad = request.headers.get("X-Entidad-ID")
        entidad_id = None

        if req_entidad:
            is_superadmin = payload.get("is_superadmin", False)
            entidades_autorizadas = payload.get("entidades", [])
            
            if is_superadmin or any(e.get("id") == req_entidad for e in entidades_autorizadas):
                entidad_id = req_entidad
            else:
                raise HTTPException(status_code=403, detail="Brecha de Seguridad: El usuario no tiene rol en este Tenant.")
        else:
            entidad_id = payload.get("entidad_id")
            
        if not entidad_id:
            raise HTTPException(status_code=401, detail="Token o petición sin entidad_id")
            
        return uuid.UUID(entidad_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada")

async def get_current_superadmin(
    credentials: HTTPAuthorizationCredentials = Security(security), 
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        
        # Buscar usando User.user_id
        res = await db.execute(select(User).where(User.user_id == uuid.UUID(user_id)))
        user = res.scalar_one_or_none()
        
        if not user or not user.is_superadmin:
            raise HTTPException(status_code=403, detail="Acceso denegado: Se requiere SuperAdmin")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="No autorizado")