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
from src.api.endpoints import auth, gui, analytics, smtp, orquestador, segregation_fix, admin, comprobantes

app = FastAPI(title="Gestor CFDI Vantec", version="6.2.5")

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

@app.get("/")
async def root():
    return {"status": "online", "base_path": BASE_DIR}