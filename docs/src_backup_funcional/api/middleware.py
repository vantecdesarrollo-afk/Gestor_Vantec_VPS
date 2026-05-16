from fastapi import Request, status
from fastapi.responses import JSONResponse
import jwt
from datetime import datetime
from typing import Optional
from src.core.config import settings

async def multi_tenant_middleware(request: Request, call_next):
    """
    Middleware de Categoría 5 para Vantec.
    Garantiza que toda petición lleve un tenant_id válido.
    """
    # 1. Rutas de Identidad y Gestión Global (Neutrales)
    NEUTRAL_PATHS = ["/api/v1/auth/", "/api/v1/admin/", "/api/v1/smtp/", "/api/orquestador/"]
    
    if not request.url.path.startswith("/api/"):
        return await call_next(request)
        
    is_neutral = any(request.url.path.startswith(path) for path in NEUTRAL_PATHS)
    
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
        
        # Permitir bypass de Entidad-ID para SuperAdmins en rutas de gestión global
        GLOBAL_MANAGEMENT_PATHS = ["/api/v1/analytics/dashboard", "/api/v1/admin/audit/logs"]
        is_global_req = any(request.url.path.startswith(path) for path in GLOBAL_MANAGEMENT_PATHS)

        tenant_id: Optional[str] = request.headers.get("X-Entidad-ID") or request.query_params.get("entidad_id")
        
        with open("tmp/middleware_debug.txt", "a") as f:
            f.write(f"--- [MIDDLEWARE DEBUG] at {datetime.now()} ---\n")
            f.write(f"Path: {request.url.path} | Method: {request.method}\n")
            f.write(f"X-Entidad-ID Header: {request.headers.get('X-Entidad-ID')}\n")
            f.write(f"Extracted tenant_id: {tenant_id}\n")
            f.write(f"Is SuperAdmin: {is_superadmin} | Is Global Req: {is_global_req}\n")

        if not tenant_id or tenant_id in ["null", "undefined", ""]:
            tenant_id = payload.get("tenant_id") or payload.get("entidad_id")
            with open("tmp/middleware_debug.txt", "a") as f:
                f.write(f"Fallback to Payload tenant_id: {tenant_id}\n")
        
        if not tenant_id:
            # Bypass quirúrgico SOLO para rutas de gestión global (Dashboard/Audit)
            # El Explorador ya NO es neutral para SuperAdmin por orden de Auditoría.
            if is_superadmin and is_global_req:
                with open("tmp/middleware_debug.txt", "a") as f:
                    f.write("Bypassing Entity Check for SuperAdmin (Global Req)\n")
                request.state.tenant_id = None
                request.state.entidad_id = None
                request.state.is_superadmin = is_superadmin
                return await call_next(request)
                
            with open("tmp/middleware_debug.txt", "a") as f:
                f.write("REJECTING: Contexto de RFC obligatorio (Status 428)\n")
            return JSONResponse(
                status_code=428, # Precondition Required
                content={"detail": "CONTEXTO_RFC_OBLIGATORIO"}
            )

        # 4. Inyección en el estado
        with open("tmp/middleware_debug.txt", "a") as f:
            f.write(f"Injecting into state: entidad_id={tenant_id}\n")
        request.state.tenant_id = tenant_id
        request.state.entidad_id = tenant_id
        request.state.is_superadmin = is_superadmin

    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Token expirado"}
        )
    except jwt.InvalidTokenError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Token inválido"}
        )

    # Continuar con la petición
    return await call_next(request)
