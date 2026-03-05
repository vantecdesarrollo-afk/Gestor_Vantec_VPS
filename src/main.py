from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from src.api.middleware import multi_tenant_middleware
from src.api.endpoints import cfdis, auth
import uvicorn

app = FastAPI(title="Gestor CFDI Vantec", version="5.0.0")

# Esquina de Seguridad para Swagger UI (Solo documentación)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Registro de Middleware Multi-tenant (RLS)
app.middleware("http")(multi_tenant_middleware)

# Registro de Endpoints
app.include_router(auth.router)
app.include_router(cfdis.router, dependencies=[Depends(oauth2_scheme)])

@app.get("/")
async def root():
    return {"message": "Gestor CFDI Vantec - API de Categoría 5 activa"}

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
