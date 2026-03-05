from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import os

from src.database.session import get_db
from src.database.models import User
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
    """
    Endpoint de Login Multi-tenant (Protocolo Vantec).
    
    Intercambia credenciales (username/password) por un Token JWT.
    El token resultante contiene el tenant_id crítico para el RLS.
    """
    
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

    # 3. Verificar Contraseña (Híbrido LOCAL vs LDAP podría ir aquí)
    if not user.password_hash or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Generación de Token con Payload Vantec
    # El tenant_id es REQUERIDO por el Middleware Multi-tenant
    access_token = create_access_token(
        data={
            "sub": str(user.user_id),
            "tenant_id": str(user.tenant_id),
            "username": user.username
        }
    )

    # 5. Actualizar último login (opcional pero recomendado)
    user.last_login = datetime.utcnow()
    await db.commit()

    return {"access_token": access_token, "token_type": "bearer"}
