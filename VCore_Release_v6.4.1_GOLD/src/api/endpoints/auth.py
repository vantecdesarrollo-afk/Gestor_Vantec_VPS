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

from pydantic import BaseModel, EmailStr
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
    
    # 2. Cargar Entidades Asociadas (Acceso Multi-tenant / Matriz de Acceso)
    from src.database.models import SysUserRole
    entidades_json = []

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
        # Standard user: Buscar en la Matriz de Acceso obligatoriamente
        role_res = await db.execute(
            select(Tenant, SysUserRole.rol)
            .join(SysUserRole, SysUserRole.entidad_id == Tenant.tenant_id)
            .where(SysUserRole.usuario_id == user.user_id)
        )
        roles_data = role_res.all()
        
        if not roles_data:
             # Si no tiene roles y no es superadmin, rechazar acceso
             raise HTTPException(status_code=403, detail="Acceso denegado: El usuario no tiene empresas asignadas en la matriz.")

        for tenant, role_str in roles_data:
             entidades_json.append({
                  "id": str(tenant.tenant_id),
                  "rfc": tenant.rfc,
                  "razon_social": tenant.business_name,
                  "rol": str(role_str).upper(),
                  "logo_url": tenant.logo_path or ""
             })

    # Generar token con la lista completa de entidades autorizadas
    access_token = create_access_token(
        data={
            "sub": str(user.user_id), 
            "username": user.username,
            "is_superadmin": is_superadmin,
            "entidades": entidades_json
        }
    )
    
    # 3. Auditoría L6: Log de Acceso Admin
    if is_superadmin:
        import os
        from datetime import datetime as dt_sys
        log_dir = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\logs"
        os.makedirs(log_dir, exist_ok=True)
        today_str = dt_sys.now().strftime("%Y-%m-%d")
        timestamp = dt_sys.now().strftime("%Y-%m-%d %H:%M:%S")
        log_path = os.path.join(log_dir, f"{today_str}_watcher_global.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] | INFO | AUDIT_LOGIN | USER: {user.username} | TIPO: SUPER_ADMIN | ACCIÓN: Acceso exitoso al sistema.\n")

    
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
             # Standard user: Buscar en la Matriz de Acceso
             role_res = await db.execute(
                 select(Tenant, SysUserRole.rol)
                 .join(SysUserRole, SysUserRole.entidad_id == Tenant.tenant_id)
                 .where(SysUserRole.usuario_id == user.user_id)
             )
             entidades_json = []
             for tenant, role_str in role_res.all():
                  entidades_json.append({"id": str(tenant.tenant_id), "rfc": tenant.rfc, "razon_social": tenant.business_name, "rol": str(role_str).upper(), "logo_url": tenant.logo_path or ""})
                  
        access_token = create_access_token(data={"sub": str(user.user_id), "username": user.username, "is_superadmin": is_superadmin, "entidades": entidades_json})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Error refreshing token: " + str(e))

@router.get("/me")
async def get_me(credentials: HTTPAuthorizationCredentials = Security(security), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id: raise HTTPException(status_code=401)
        
        result = await db.execute(select(User).where(User.user_id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()
        if not user: raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return {
            "id": str(user.user_id),
            "username": user.username,
            "email": user.email,
            "is_superadmin": getattr(user, "is_superadmin", False),
            "entidades": payload.get("entidades", [])
        }
    except Exception:
        raise HTTPException(status_code=401, detail="No autorizado")


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

        if req_entidad and req_entidad not in ["null", "undefined", ""]:
            is_superadmin = payload.get("is_superadmin", False)
            entidades_autorizadas = payload.get("entidades", [])
            
            if is_superadmin or any(str(e.get("id")).lower() == str(req_entidad).lower() for e in entidades_autorizadas):
                entidad_id = req_entidad
            else:
                raise HTTPException(status_code=403, detail="Brecha de Seguridad: El usuario no tiene rol en este Tenant.")
            if not entidad_id:
                raise HTTPException(status_code=428, detail="CONTEXTO_RFC_OBLIGATORIO")
        else:
            entidad_id = payload.get("tenant_id") or payload.get("entidad_id")
            
        if not entidad_id:
             is_superadmin = payload.get("is_superadmin", False)
             if is_superadmin:
                  return None # Modo Neutral SuperAdmin
             raise HTTPException(status_code=428, detail="CONTEXTO_RFC_OBLIGATORIO")
             
        return uuid.UUID(entidad_id)
    except HTTPException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        # Si es un error de UUID o algo interno de contexto, no queremos 401 (logout)
        # Solo regresamos 401 si realmente la sesión está mal (JWT)
        raise HTTPException(status_code=500, detail="Error interno al validar contexto: " + str(e))

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security), 
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        
        res = await db.execute(select(User).where(User.user_id == uuid.UUID(user_id)))
        user = res.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        if not getattr(user, "is_active", True):
            raise HTTPException(status_code=403, detail="Cuenta inactiva")
            
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="No autorizado")

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

# 4. Recuperación de Contraseña (L6 v3.5)
class RecoveryRequest(BaseModel):
    email: str 

class ResetPasswordRequest(BaseModel):
    token: str
    password: str

@router.post("/recovery")
async def request_recovery(payload: RecoveryRequest, db: AsyncSession = Depends(get_db)):
    # 1. Buscar usuario por email
    from src.database.models import User, AuthRecoveryToken, EntidadSMTPConfig
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    
    if not user:
        # Por seguridad no revelamos si existe el usuario
        return {"message": "Si el correo está registrado, recibirá instrucciones en breve."}
    
    # 2. Generar Token Atómico
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    recovery_token = AuthRecoveryToken(
        user_id=user.user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(recovery_token)
    await db.commit()
    
    # 3. Enviar Correo (Motor SMTP real)
    smtp_query = select(EntidadSMTPConfig).where(EntidadSMTPConfig.entidad_id == user.tenant_id)
    smtp_res = await db.execute(smtp_query)
    smtp_config = smtp_res.scalar_one_or_none()
    
    # Fallback si el tenant no tiene config propia
    if not smtp_config:
        fallback_query = select(EntidadSMTPConfig).limit(1)
        fallback_res = await db.execute(fallback_query)
        smtp_config = fallback_res.scalar_one_or_none()

    if smtp_config:
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_config.from_address or smtp_config.username
            msg['To'] = user.email
            msg['Subject'] = "🔒 Recuperación de Contraseña - Vantec Core"
            
            body = f"""Hola {user.username},

Ha solicitado restablecer su contraseña en Vantec Core.
Use el siguiente enlace para establecer una nueva (válido por 1 hora):

http://localhost:8000/reset-password?token={token}

Si no solicitó esto, por favor ignore este mensaje.

Atentamente,
Equipo de Seguridad Vantec
"""
            msg.attach(MIMEText(body, 'plain'))
            
            if smtp_config.security_type == 'SSL':
                server = smtplib.SMTP_SSL(smtp_config.host, smtp_config.port, timeout=10)
            else:
                server = smtplib.SMTP(smtp_config.host, smtp_config.port, timeout=10)
                if smtp_config.security_type == 'STARTTLS':
                    server.starttls()
            
            if smtp_config.authentication_type != 'NONE':
                server.login(smtp_config.username, smtp_config.password_encrypted)
            
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"[RECOVERY_ERROR] Fallo al enviar correo via SMTP ({smtp_config.host}): {str(e)}")
            
    return {"message": "Si el correo está registrado, recibirá instrucciones en breve."}

@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    from src.database.models import AuthRecoveryToken, User
    
    # 1. Validar Token
    query = select(AuthRecoveryToken).where(
        AuthRecoveryToken.token == payload.token,
        AuthRecoveryToken.is_used == False,
        AuthRecoveryToken.expires_at > datetime.utcnow()
    )
    result = await db.execute(query)
    token_record = result.scalar_one_or_none()
    
    if not token_record:
        raise HTTPException(status_code=400, detail="Token inválido, expirado o ya utilizado.")
    
    # 2. Actualizar Password (BCrypt vía get_password_hash)
    user_query = select(User).where(User.user_id == token_record.user_id)
    user_res = await db.execute(user_query)
    user = user_res.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    user.password_hash = get_password_hash(payload.password)
    token_record.is_used = True
    
    await db.commit()
    return {"status": "success", "message": "Contraseña actualizada correctamente"}