from fastapi import Request, status
from fastapi.responses import JSONResponse
import jwt
from typing import Optional
from src.core.config import settings

async def multi_tenant_middleware(request: Request, call_next):
    """
    Middleware de Categoría 5 para Vantec.
    Garantiza que toda petición lleve un tenant_id válido.
    """
    # 1. Ignorar rutas públicas (como el Login o Docs)
    if request.url.path in ["/api/v1/auth/login", "/docs", "/openapi.json"]:
        return await call_next(request)

    # 2. Extracción del Token
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Falta token de autenticación o formato inválido"}
        )

    token = auth_header.split(" ")[1]

    try:
        # 3. Decodificación y Validación (Usando configuración centralizada)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        tenant_id: Optional[str] = payload.get("tenant_id")
        
        if not tenant_id:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "El token no contiene un tenant_id válido"}
            )

        # 4. Inyección en el estado
        request.state.tenant_id = tenant_id

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
