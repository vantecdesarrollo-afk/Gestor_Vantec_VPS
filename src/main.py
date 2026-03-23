from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from src.api.middleware import multi_tenant_middleware
from src.api.endpoints import cfdis, auth, gui, analytics, smtp, orquestador, comprobantes, admin

app = FastAPI(title="Gestor CFDI Vantec", version="5.0.0")

# 1. Montar Estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Seguridad para Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# 3. Middleware Multi-tenant (RLS)
app.middleware("http")(multi_tenant_middleware)

# 4. Registro de Endpoints
# NOTA: No agregues 'prefix' aquí si ya está definido dentro del archivo del router
app.include_router(auth.router)
app.include_router(cfdis.router, dependencies=[Depends(oauth2_scheme)])
app.include_router(comprobantes.router, dependencies=[Depends(oauth2_scheme)]) # Prefijo ya viene de comprobantes.py
app.include_router(analytics.router, dependencies=[Depends(oauth2_scheme)])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Administración"])
app.include_router(smtp.router, dependencies=[Depends(oauth2_scheme)])
app.include_router(orquestador.router, dependencies=[Depends(oauth2_scheme)])

# 5. Enrutamiento de Vistas HTML (GUI)
app.include_router(gui.router)

@app.get("/")
async def root():
    return {"message": "Vantec API v5.0.0 is running"}