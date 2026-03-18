from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from src.api.middleware import multi_tenant_middleware
from fastapi.staticfiles import StaticFiles
from src.api.endpoints import cfdis, auth, gui, analytics, smtp, orquestador, comprobantes, admin

app = FastAPI(title="Gestor CFDI Vantec", version="5.0.0")

# Montar Estáticos antes de los routers
app.mount("/static", StaticFiles(directory="static"), name="static")

# Esquina de Seguridad para Swagger UI (Solo documentación)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Registro de Middleware Multi-tenant (RLS)
app.middleware("http")(multi_tenant_middleware)

# Registro de Endpoints
app.include_router(auth.router)
app.include_router(cfdis.router, dependencies=[Depends(oauth2_scheme)])
app.include_router(comprobantes.router, prefix="/api/v1/comprobantes", tags=["CFDIs"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Administración"])
app.include_router(analytics.router, dependencies=[Depends(oauth2_scheme)])
app.include_router(smtp.router, dependencies=[Depends(oauth2_scheme)])
app.include_router(orquestador.router, dependencies=[Depends(oauth2_scheme)])
app.include_router(gui.router) # Enrutamiento de Vistas HTML


@app.get("/")
async def root():
    return {"message": "Gestor CFDI Vantec - API de Categoría 5 activa"}

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
