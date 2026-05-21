from fastapi import Request, status
from fastapi.responses import JSONResponse
import jwt
import os
from datetime import datetime
from typing import Optional
from src.core.config import settings

async def multi_tenant_middleware(request: Request, call_next):
    """
    Middleware de Categoría 5 para Vantec.
    Garantiza que toda petición lleve un tenant_id válido y auto-repara su entorno.
    """
    
    # [VCORE L6] AUTO-REPARACIÓN DE INFRAESTRUCTURA
    # Si la carpeta tmp no existe (debido a limpieza o build), se crea al vuelo.
    DEBUG_DIR = "tmp"
    DEBUG_FILE = os.path.join(DEBUG_DIR, "middleware_debug.txt")
    
    if not os.path.exists(DEBUG_DIR):
        try:
            os.makedirs(DEBUG_DIR, exist_ok=True)
        except Exception as e:
            print(f"⚠️ Alerta VCore: No se pudo crear el directorio de logs: {e}")

    # 1. Rutas de Identidad y Gestión Global (Neutrales)
    NOT_AUTHENTICATED_ROUTES = [
        "/api/v1/auth/login",
        "/api/v1/auth/recovery",
        "/api/v1/debug/users",
        "/docs",
        "/openapi.json",
        "/api/v1/ingesta/upload_cfdi"
    ]
    
    if not request.url.path.startswith("/api/"):
        return await call_next(request)
        
    is_neutral = any(request.url.path == path or request.url.path.startswith(path) for path in NOT_AUTHENTICATED_ROUTES)
    
    # --- RUTA NEUTRAL (Bypass de Token para Auth/Soporte) ---
    if is_neutral:
        return await call_next(request)

    # 2. Extracción del Token (Solo para rutas operativas)
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Falta token de autenticación o formato inválido"}
        )

    token = auth_header.split(" ")[1]

    try:
        # 3. Decodificación y Validación
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # --- Lógica de Contexto VCORE L3 (Modo Neutral Admin) ---
        is_superadmin = payload.get("is_superadmin") is True
        
        # Rutas autenticadas que no requieren contexto de tenant
        TENANT_NEUTRAL_ROUTES = [
            "/api/v1/auth/refresh",
            "/api/v1/auth/me"
        ]
        is_tenant_neutral = any(request.url.path == path or request.url.path.startswith(path) for path in TENANT_NEUTRAL_ROUTES)
        
        if is_tenant_neutral:
            request.state.tenant_id = None
            request.state.entidad_id = None
            request.state.is_superadmin = is_superadmin
            return await call_next(request)
        
        # Permitir bypass de Entidad-ID para SuperAdmins en rutas de gestión global
        GLOBAL_MANAGEMENT_PATHS = ["/api/v1/analytics/dashboard", "/api/v1/admin"]
        is_global_req = any(request.url.path.startswith(path) for path in GLOBAL_MANAGEMENT_PATHS)

        tenant_id: Optional[str] = request.headers.get("X-Entidad-ID") or request.query_params.get("entidad_id")
        
        # [VCORE L6] REGISTRO SEGURO (TRY-EXCEPT WRAPPER)
        try:
            with open(DEBUG_FILE, "a", encoding="utf-8") as f:
                f.write(f"--- [MIDDLEWARE DEBUG] at {datetime.now()} ---\n")
                f.write(f"Path: {request.url.path} | Method: {request.method}\n")
                f.write(f"X-Entidad-ID Header: {request.headers.get('X-Entidad-ID')}\n")
                f.write(f"Extracted tenant_id: {tenant_id}\n")
                f.write(f"Is SuperAdmin: {is_superadmin} | Is Global Req: {is_global_req}\n")
        except Exception:
            # Si el log falla, el sistema NO debe caer. Continuamos la ejecución.
            pass

        if not tenant_id or tenant_id in ["null", "undefined", ""]:
            # Fallback 1: Si es ruta SMTP, extraer del path del endpoint
            if request.url.path.startswith("/api/v1/smtp/"):
                parts = [p for p in request.url.path.split("/") if p]
                if len(parts) >= 4:
                    tenant_id = parts[3] # parts[0]='api', parts[1]='v1', parts[2]='smtp', parts[3]=tenant_id

            # Fallback 2: Payload de JWT
            if not tenant_id or tenant_id in ["null", "undefined", ""]:
                tenant_id = payload.get("tenant_id") or payload.get("entidad_id")
            
            try:
                with open(DEBUG_FILE, "a", encoding="utf-8") as f:
                    f.write(f"Fallback/Extracted tenant_id: {tenant_id}\n")
            except: pass
        
        if not tenant_id:
            # Bypass quirúrgico SOLO para rutas de gestión global (Dashboard/Audit)
            if is_superadmin and is_global_req:
                try:
                    with open(DEBUG_FILE, "a", encoding="utf-8") as f:
                        f.write("Bypassing Entity Check for SuperAdmin (Global Req)\n")
                except: pass
                
                request.state.tenant_id = None
                request.state.entidad_id = None
                request.state.is_superadmin = is_superadmin
                return await call_next(request)
                
            try:
                with open(DEBUG_FILE, "a", encoding="utf-8") as f:
                    f.write("REJECTING: Contexto de RFC obligatorio (Status 428)\n")
            except: pass

            return JSONResponse(
                status_code=428, # Precondition Required
                content={"detail": "CONTEXTO_RFC_OBLIGATORIO"}
            )

        # 4. Inyección en el estado
        try:
            with open(DEBUG_FILE, "a", encoding="utf-8") as f:
                f.write(f"Injecting into state: entidad_id={tenant_id}\n")
        except: pass

        request.state.tenant_id = tenant_id
        request.state.entidad_id = tenant_id
        request.state.is_superadmin = is_superadmin

    except jwt.ExpiredSignatureError:
        return JSONResponse(status_code=401, content={"detail": "Token expirado"})
    except jwt.InvalidTokenError:
        return JSONResponse(status_code=401, content={"detail": "Token inválido"})

    # Continuar con la petición
    return await call_next(request)