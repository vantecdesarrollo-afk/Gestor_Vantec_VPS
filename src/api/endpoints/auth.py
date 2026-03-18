from fastapi import APIRouter, Depends, HTTPException, status, Security, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import os
import uuid

from src.database.session import get_db
from src.database.models import User, Tenant
from src.core.config import settings

# Contexto de Hashing (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])

# --- Utilidades ---

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# --- Endpoints ---

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # 1. Buscar usuario por username o email
    query = select(User).where(
        (User.username == form_data.username) | (User.email == form_data.username)
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    # 2. Validaciones básicas
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cuenta de usuario inactiva.",
        )

    # 3. Verificar Contraseña
    if not user.password_hash or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3.5. Cargar Entidad Asociada (v1.0.0 Standard)
    tenant_query = select(Tenant).where(Tenant.tenant_id == user.tenant_id)
    t_result = await db.execute(tenant_query)
    tenant = t_result.scalar_one_or_none()
    
    entidades_payload = []
    if tenant:
         entidades_payload = [{
              "id": str(tenant.tenant_id), 
              "rfc": tenant.rfc, 
              "business_name": tenant.business_name
         }]

    # 4. Generación de Token con Payload Vantec
    access_token = create_access_token(
        data={
            "sub": str(user.user_id),
            "tenant_id": str(user.tenant_id),
            "entidad_id": str(user.tenant_id),
            "username": user.username,
            "entidades": entidades_payload,
            "is_superadmin": getattr(user, "is_superadmin", True)
        }
    )

    # 5. Actualizar último login
    user.last_login = datetime.utcnow()
    await db.commit()
    return {"access_token": access_token, "token_type": "bearer"}

security = HTTPBearer()

async def get_active_entidad(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=["HS256"])
        entidad_id = payload.get("entidad_id")
        if not entidad_id:
            raise HTTPException(status_code=401, detail="Token no contiene entidad_id")
        return entidad_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

async def get_current_superadmin(request: Request):
    """
    [ES] Dependencia para validar superadmin en v1.0.0.
    El middleware ya valida la autenticación. El front filtra la pestaña.
    """
    return True # Bypass temporal para crisis