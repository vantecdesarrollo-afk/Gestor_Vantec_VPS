import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
# Si usas JWT, podrías importar aquí tu decodificador
# from src.core.security import decode_token 

class MultiTenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Intentamos extraer el ID del Header (Sin default inseguro)
        raw_entidad_id = request.headers.get("X-Entidad-ID")
        
        entidad_uuid = None
        if raw_entidad_id:
            try:
                entidad_uuid = uuid.UUID(raw_entidad_id)
            except (ValueError, TypeError):
                entidad_uuid = None

        # 2. Inyectamos el objeto UUID (o None) en el estado de la petición
        request.state.entidad_id = entidad_uuid
        
        # 3. Continuar con el proceso de la API
        response = await call_next(request)
        
        # 4. Devolvemos el id en la respuesta para auditoría técnica (si existe)
        if entidad_uuid:
            response.headers["X-Entidad-ID"] = str(entidad_uuid)
        
        return response