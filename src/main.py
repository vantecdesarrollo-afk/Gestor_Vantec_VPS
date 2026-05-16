import os
import sys
import time
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# --- [VCORE L6] MOTOR DE RUTAS UNIVERSALES ---
# Detectamos la ubicación de este archivo (C:\...\src\main.py)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Subimos un nivel para llegar a la raíz (donde vive /static y .env)
BASE_DIR = os.path.dirname(CURRENT_DIR) 

# Definición de rutas relativas alineadas al instalador
LICENSE_DIR = os.path.join(CURRENT_DIR, "license") # /src/license
MACHINE_ID_FILE = os.path.join(LICENSE_DIR, "machine_id.txt")
STATIC_DIR = os.path.join(BASE_DIR, "static") # /static en la raíz

# --- INICIO BLINDAJE L3 VANTEC ---
from src.core.license_core import VantecSystemState

def auditar_licencia():
    if not os.path.exists(LICENSE_DIR):
        os.makedirs(LICENSE_DIR, exist_ok=True)
    
    # Buscamos licencia comercial
    jwt_files = [f for f in os.listdir(LICENSE_DIR) if f.endswith(".jwt")] if os.path.exists(LICENSE_DIR) else []
    
    if jwt_files:
        VantecSystemState.LICENSE_TIER = "pro"
        return

    # Si no hay licencia, verificamos/generamos periodo de gracia
    if not os.path.exists(MACHINE_ID_FILE):
        try:
            import subprocess
            cmd = "powershell -NoProfile -Command \"(Get-WmiObject -Class Win32_ComputerSystemProduct).UUID\""
            uuid = subprocess.check_output(cmd).decode().strip()
            with open(MACHINE_ID_FILE, "w") as f:
                f.write(uuid)
        except:
            sys.exit(1)

    fecha_instalacion = os.path.getctime(MACHINE_ID_FILE)
    dias_transcurridos = (time.time() - fecha_instalacion) / (24 * 3600)
    VantecSystemState.IS_DEMO = True
    VantecSystemState.DAYS_LEFT = int(45 - dias_transcurridos)
    
    if dias_transcurridos > 45:
        print("⛔ BLOQUEO: Periodo de gracia terminado.")
        sys.exit(1)

auditar_licencia()
# --- FIN BLINDAJE L3 ---

from src.api.middleware import multi_tenant_middleware
from src.api.endpoints import auth, gui, analytics, smtp, orquestador, segregation_fix, admin, comprobantes, ingesta_vps

app = FastAPI(title="Gestor CFDI Vantec", version="6.2.5")

from sqlalchemy import select
from src.database.models import User
from src.database.session import AsyncSessionLocal
import uuid

async def seed_core_database(db_session):
    query = select(User).where(User.is_superadmin == True)
    result = await db_session.execute(query)
    existing_admin = result.scalar_one_or_none()
    if not existing_admin:
        seed_user = User(
            user_id=uuid.UUID('9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d'),
            tenant_id=None,
            username="admin",
            password_hash="$2b$12$Ecx7V68MabH6U7KzLOnw9unW.a6AhyMv6GgMsdvJnZpW0tNfVIGe2",
            email="admin@vcore.com",
            is_active=True,
            is_superadmin=True,
            rol="ADMIN"
        )
        db_session.add(seed_user)
        await db_session.commit()
        print("[SEEDING] Base de datos inaugurada exitosamente con el Usuario Semilla Global.")
    else:
        print("[SEEDING] La base de datos ya cuenta con usuarios administradores registrados. Saltando siembra.")

@app.on_event("startup")
async def startup_event():
    import asyncio
    max_retries = 10
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            async with AsyncSessionLocal() as session:
                await seed_core_database(session)
            print("[STARTUP] Conexión a la base de datos exitosa y Auto-Seeding validado.")
            break
        except Exception as e:
            print(f"[STARTUP] Intento {attempt + 1}/{max_retries} fallido. Esperando a que PostgreSQL inicie... Error: {e}")
            await asyncio.sleep(retry_delay)
    else:
        print("[STARTUP] CRÍTICO: No se pudo conectar a la base de datos tras múltiples intentos.")

# --- MONTAJE DE ESTÁTICOS (RUTA UNIVERSAL) ---
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
else:
    # Crea la carpeta si no existe para evitar el error 404 de arranque
    os.makedirs(STATIC_DIR, exist_ok=True)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# --- MIDDLEWARE Y ENRUTADORES ---
app.middleware("http")(multi_tenant_middleware)
app.include_router(auth.router)
app.include_router(comprobantes.router, prefix="/api/v1/comprobantes")
app.include_router(segregation_fix.router)
app.include_router(analytics.router)
app.include_router(admin.router, prefix="/api/v1/admin")
app.include_router(smtp.router)
app.include_router(orquestador.router)
app.include_router(gui.router)
app.include_router(ingesta_vps.router, prefix="/api/v1/ingesta")

@app.get("/")
async def root():
    return {"status": "online", "base_path": BASE_DIR}