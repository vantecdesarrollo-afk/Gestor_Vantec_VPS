from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from src.api.middleware import multi_tenant_middleware
from src.api.endpoints import auth, gui, analytics, smtp, orquestador, segregation_fix, admin, comprobantes

app = FastAPI(title="Gestor CFDI Vantec", version="5.0.0")

# 1. Montar Estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Seguridad para Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# 3. Middleware Multi-tenant (RLS)
app.middleware("http")(multi_tenant_middleware)

# 4. Registro de Endpoints
app.include_router(auth.router)
app.include_router(comprobantes.router, prefix="/api/v1/comprobantes")
app.include_router(comprobantes.router, prefix="/api/v1/hardened-explorer")
app.include_router(comprobantes.router, prefix="/api/analytics")
app.include_router(segregation_fix.router)
app.include_router(analytics.router)
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Administración"])
app.include_router(smtp.router)
app.include_router(orquestador.router)

# 5. Enrutamiento de Vistas HTML (GUI)
app.include_router(gui.router)

@app.get("/")
async def root():
    return {"message": "Vantec API v5.0.0 is running"}