import os
import sys
import time
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger("uvicorn.error")

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
            import platform
            import uuid as native_uuid
            
            if platform.system() == "Windows":
                cmd = "powershell -NoProfile -Command \"(Get-WmiObject -Class Win32_ComputerSystemProduct).UUID\""
                sys_uuid = subprocess.check_output(cmd).decode().strip()
            else:
                # En VPS/Linux/Docker usamos un UUID derivado del nodo de red o aleatorio
                sys_uuid = str(native_uuid.uuid1())
                
            with open(MACHINE_ID_FILE, "w") as f:
                f.write(sys_uuid)
        except Exception as e:
            # En caso de cualquier error crítico en la lectura de red o disco en Docker, generamos uno aleatorio
            import uuid as fallback_uuid
            with open(MACHINE_ID_FILE, "w") as f:
                f.write(str(fallback_uuid.uuid4()))

    fecha_instalacion = os.path.getctime(MACHINE_ID_FILE)
    dias_transcurridos = (time.time() - fecha_instalacion) / (24 * 3600)
    VantecSystemState.IS_DEMO = True
    VantecSystemState.DAYS_LEFT = int(45 - dias_transcurridos)
    
    if dias_transcurridos > 45:
        print("⚠️ ALERTA: Periodo de gracia terminado (Modo VPS).")
        # sys.exit(1) # Desactivado temporalmente para evitar 502 Bad Gateway en despliegue.

try:
    auditar_licencia()
except Exception as e:
    print(f"⚠️ ERROR EN AUDITORÍA DE LICENCIA: {e}")
# --- FIN BLINDAJE L3 ---

from src.api.middleware import multi_tenant_middleware
try:
    from src.api.endpoints import auth, gui, analytics, smtp, orquestador, segregation_fix, admin, comprobantes, ingesta_vps
except Exception as e:
    print(f"⚠️ ERROR IMPORTANDO ENDPOINTS: {e}")
    auth = gui = analytics = smtp = orquestador = segregation_fix = admin = comprobantes = ingesta_vps = None

from sqlalchemy import select
from src.database.models import User
from src.database.session import AsyncSessionLocal
import uuid
from contextlib import asynccontextmanager

async def seed_core_database(db_session):
    query = select(User).where(User.is_superadmin == True)
    result = await db_session.execute(query)
    existing_admin = result.scalar_one_or_none()
    if not existing_admin:
        seed_user = User(
            user_id=uuid.UUID('9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d'),
            tenant_id=None,
            username="admin",
            password_hash="$2b$12$kk8QFO.LgKzqKmCt3UFQDenx4ZiEwHhZeWoKhHXA3Ld2MGkFJ9Gom",
            email="admin@vcore.com",
            is_active=True,
            is_superadmin=True,
            rol="ADMIN"
        )
        db_session.add(seed_user)
        await db_session.commit()
        print("[SEEDING] Base de datos inaugurada exitosamente con el Usuario Semilla Global.")
    else:
        # Forzar actualización de contraseña si es el admin por defecto
        existing_admin.password_hash = "$2b$12$kk8QFO.LgKzqKmCt3UFQDenx4ZiEwHhZeWoKhHXA3Ld2MGkFJ9Gom"
        await db_session.commit()
        print("[SEEDING] Credenciales del administrador sincronizadas.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[LIFESPAN] Iniciando VCore VPS Backend...")
    import asyncio
    
    async def run_seeding():
        try:
            print("[LIFESPAN] Ejecutando auto-seeding en segundo plano...")
            async with AsyncSessionLocal() as session:
                # Limitar a 5 segundos el intento de conexión y sembrado para evitar colgar el proceso
                await asyncio.wait_for(seed_core_database(session), timeout=5.0)
        except asyncio.TimeoutError:
            logger.error("⚠️ [STARTUP WARNING] Timeout de 5 segundos en auto-seeding: la base de datos no respondió a tiempo.")
            print("El sistema continuará en funcionamiento para permitir diagnóstico de red y base de datos.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"⚠️ [STARTUP WARNING] Error en auto-seeding de base de datos: {str(e)}")
            print("El sistema continuará en funcionamiento para permitir diagnóstico de red y base de datos.")
            
    asyncio.create_task(run_seeding())
    yield
    print("[LIFESPAN] Apagando VCore VPS Backend...")

app = FastAPI(title="Gestor CFDI Vantec", version="6.2.5", lifespan=lifespan)

# --- MONTAJE DE ESTÁTICOS (RUTA UNIVERSAL) ---
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
else:
    # Crea la carpeta si no existe para evitar el error 404 de arranque
    os.makedirs(STATIC_DIR, exist_ok=True)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# --- MIDDLEWARE Y ENRUTADORES ---
app.middleware("http")(multi_tenant_middleware)
if auth: app.include_router(auth.router)
if comprobantes: app.include_router(comprobantes.router, prefix="/api/v1/comprobantes")
if segregation_fix: app.include_router(segregation_fix.router)
if analytics: app.include_router(analytics.router)
if admin: app.include_router(admin.router, prefix="/api/v1/admin")
if smtp: app.include_router(smtp.router)
if orquestador: app.include_router(orquestador.router)
if gui: app.include_router(gui.router)
if ingesta_vps: app.include_router(ingesta_vps.router, prefix="/api/v1/ingesta")

@app.get("/api/v1/debug/users")
async def debug_users():
    from sqlalchemy import text
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(text("SELECT user_id, username, is_superadmin FROM public.users"))
            users = [{"id": str(r[0]), "username": r[1], "is_superadmin": r[2]} for r in result.all()]
            return {"count": len(users), "users": users}
        except Exception as e:
            return {"error": str(e)}

@app.get("/debug_users_no_api")
async def debug_users_direct():
    from sqlalchemy import text
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(text("SELECT user_id, username, is_superadmin FROM public.users"))
            users = [{"id": str(r[0]), "username": r[1], "is_superadmin": r[2]} for r in result.all()]
            return {"count": len(users), "users": users}
        except Exception as e:
            return {"error": str(e)}

@app.get("/ping")
async def ping():
    return "pong"

@app.get("/")
async def root():
    from src.core.config import settings
    # Enmascarar password para seguridad
    db_url = settings.DATABASE_URL
    if "@" in db_url:
        db_url = db_url.split("@")[0].split(":")[0] + ":****@" + db_url.split("@")[1]
    return {
        "status": "online", 
        "base_path": str(BASE_DIR),
        "db_info": db_url,
        "build_id": "2026-05-16_13:40"
    }