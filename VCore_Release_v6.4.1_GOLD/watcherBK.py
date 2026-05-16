import sys, os, time, asyncio, logging, shutil, json, hashlib, re
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, cast, String, text
from src.database.models import Tenant, Comprobante
from src.services.parser.cfdi_parser import process_inbound_file, analyze_pdf_fiscal_data

# ==============================================================================
# 1. CONFIGURACIÓN DE RUTAS Y ENTORNO
# ==============================================================================
load_dotenv()
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_PATH)

env_zones = os.getenv("WATCHER_ZONES")
try:
    WATCHER_CONFIG = json.loads(env_zones) if env_zones else {}
except:
    WATCHER_CONFIG = {}

if not WATCHER_CONFIG:
    UPLOAD_DIR = os.path.join(BASE_PATH, "Operacion_CFDI", "Upload_Universal")
    WATCHER_CONFIG = {UPLOAD_DIR: None}

ORPHANS_DIR = os.path.join(BASE_PATH, "Operacion_CFDI", "Orphans")
INVALID_DIR = os.path.join(BASE_PATH, "Operacion_CFDI", "Invalid_ADN")
DUPLICATES_GLOBAL_DIR = os.path.join(BASE_PATH, "Operacion_CFDI", "duplicates")
LOGS_GLOBAL_DIR = os.path.join(BASE_PATH, "Operacion_CFDI", "logs")

for d in [ORPHANS_DIR, INVALID_DIR, DUPLICATES_GLOBAL_DIR, LOGS_GLOBAL_DIR]:
    os.makedirs(d, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - 🛡️ VANTEC VCORE - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

db_url = os.getenv("DATABASE_URL")
engine = create_async_engine(db_url)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

processing_files = set()
ingestion_lock = asyncio.Lock()

# ==============================================================================
# 2. FUNCIONES DE SOPORTE Y SEGURIDAD MD5
# ==============================================================================
async def wait_for_file_readiness(file_path, timeout=5):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with open(file_path, "rb"): return True
        except: 
            await asyncio.sleep(0.5)
    return False

async def handle_pair_anomaly(file_path, reason, tenant_rfc=None):
    """Enruta el archivo a su cuarentena (aislada por Tenant si es posible) y registra el evento"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.basename(file_path)

    # 🛡️ AISLAMIENTO L6: Segregación a la carpeta de la Entidad
    if reason == 'DUPLICADO' and tenant_rfc:
        target_dir = os.path.join(BASE_PATH, "Operacion_CFDI", "Files", tenant_rfc, "logs", "duplicates")
        log_path = os.path.join(BASE_PATH, "Operacion_CFDI", "Files", tenant_rfc, "logs", f"{date_str}_empresa_audit.log")
    else:
        # Fallbacks Globales
        if reason == 'HUÉRFANO': target_dir = ORPHANS_DIR
        elif reason == 'DUPLICADO': target_dir = DUPLICATES_GLOBAL_DIR
        else: target_dir = INVALID_DIR
        log_path = os.path.join(LOGS_GLOBAL_DIR, f"{date_str}_watcher_global.log")

    os.makedirs(target_dir, exist_ok=True)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    safe_dest = os.path.join(target_dir, filename)
    
    try:
        if os.path.exists(safe_dest):
            os.remove(safe_dest)
        shutil.move(file_path, safe_dest)
        
        contexto = f" (Entidad: {tenant_rfc})" if tenant_rfc else " (Global)"
        logger.warning(f"⚠️ ARCHIVO MOVIDO A {reason}{contexto}: {filename}")
        
        # 📝 Generar Log físico de Auditoría
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ⚠️ {reason}: {filename} interceptado y segregado.\n")
            
    except Exception as e:
        pass

def get_md5_hash(file_path):
    """Genera huella digital para garantizar idempotencia."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""): hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None

class GlobalIngestHandler(FileSystemEventHandler):
    def __init__(self, loop, upload_zones):
        self.loop = loop
        self.upload_zones = upload_zones

    def on_created(self, event):
        if not event.is_directory:
            ctx_id = self.upload_zones.get(os.path.dirname(event.src_path))
            asyncio.run_coroutine_threadsafe(safe_process_file(event.src_path, ctx_id), self.loop)

# ==============================================================================
# 3. MOTOR CENTRAL DE INGESTA (SMART SYNC + GHOST HEALER)
# ==============================================================================
async def safe_process_file(file_path, ctx_id=None):
    if not os.path.exists(file_path) or file_path in processing_files: 
        return
    
    processing_files.add(file_path)
    if not await wait_for_file_readiness(file_path):
        processing_files.discard(file_path)
        return

    async with ingestion_lock:
        try:
            async with AsyncSessionLocal() as db:
                filename = os.path.basename(file_path)
                file_basename = os.path.splitext(filename)[0]

                # --- 1. PROCESAMIENTO DE XML ---
                if file_path.lower().endswith(".xml"):
                    await process_inbound_file(xml_path=file_path, failed_dir=INVALID_DIR, log_dir=LOGS_GLOBAL_DIR, db=db, entidad_id=ctx_id)
                    
                    # 👻 GATILLO DEL GHOST HEALER
                    for orphan_file in os.listdir(ORPHANS_DIR):
                        orphan_path = os.path.join(ORPHANS_DIR, orphan_file)
                        if orphan_path.lower().endswith(".pdf"):
                            logger.info(f"👻 GHOST HEALER: Evaluando rescate de {orphan_file}...")
                            asyncio.create_task(safe_process_file(orphan_path, ctx_id))

                # --- 2. PROCESAMIENTO DE PDF (MULTI-PDF + IDEMPOTENCIA) ---
                elif file_path.lower().endswith(".pdf"):
                    doc_uuid = None
                    
                    if len(file_basename) == 36 and file_basename.count('-') == 4:
                        doc_uuid = file_basename
                    
                    if not doc_uuid:
                        pdf_data = await analyze_pdf_fiscal_data(file_path)
                        doc_uuid = pdf_data.get("uuid")

                    if doc_uuid:
                        comp = None
                        for attempt in range(5):
                            res = await db.execute(select(Comprobante).where(func.lower(cast(Comprobante.uuid, String)) == doc_uuid.lower()))
                            comp = res.scalars().first()
                            if comp: break
                            await asyncio.sleep(1)

                        if comp:
                            if comp.tipo_comprobante == 'I' and 'pago' in filename.lower():
                                logger.info(f"🔄 REDIRECCIÓN INTELIGENTE: Buscando REP para {doc_uuid}")
                                query = text("""
                                    SELECT c.uuid FROM comprobantes c 
                                    JOIN cfdi_relacionados r ON c.uuid = r.cfdi_id 
                                    WHERE lower(r.uuid_relacionado) = lower(:parent_uuid) 
                                    AND c.tipo_comprobante = 'P' LIMIT 1
                                """)
                                result = await db.execute(query, {"parent_uuid": str(doc_uuid)})
                                real_pago_uuid = result.scalar()
                                
                                if real_pago_uuid:
                                    res_pago = await db.execute(select(Comprobante).where(Comprobante.uuid == real_pago_uuid))
                                    comp = res_pago.scalars().first()
                                    doc_uuid = str(real_pago_uuid)
                                else:
                                    await handle_pair_anomaly(file_path, 'INVALID_ADN')
                                    return

                            from src.services.cfdi_storage import construir_ruta_archivo
                            base_dest_path = str(construir_ruta_archivo(str(comp.entidad_id), comp.rfc_emisor, comp.fecha_emision, str(comp.uuid), 'pdf'))
                            os.makedirs(os.path.dirname(base_dest_path), exist_ok=True)
                            
                            # 🛡️ FILTRO MD5 (Idempotencia binaria)
                            new_pdf_md5 = get_md5_hash(file_path)
                            existing_paths = [p.strip() for p in (comp.pdf_path or "").split('|') if p.strip() and os.path.exists(p.strip())]
                            
                            is_duplicate = False
                            for ep in existing_paths:
                                if get_md5_hash(ep) == new_pdf_md5:
                                    is_duplicate = True
                                    break
                            
                            if is_duplicate:
                                logger.warning(f"🛡️ IDEMPOTENCIA: Clon binario detectado (MD5 Idéntico): {filename}")
                                tenant_rfc = None
                                try:
                                    res_tenant = await db.execute(select(Tenant.rfc).where(Tenant.tenant_id == comp.entidad_id))
                                    tenant_rfc = res_tenant.scalar()
                                except: pass
                                # En lugar de solo borrarlo, lo documentamos en el log de la empresa
                                await handle_pair_anomaly(file_path, 'DUPLICADO', tenant_rfc)
                                return
                                
                            # 🔄 LÓGICA MULTI-PDF
                            final_dest_path = base_dest_path
                            counter = 1
                            base_dir = os.path.dirname(base_dest_path)
                            base_name = os.path.splitext(os.path.basename(base_dest_path))[0]
                            
                            while os.path.exists(final_dest_path):
                                final_dest_path = os.path.join(base_dir, f"{base_name}_{counter}.pdf")
                                counter += 1
                                
                            shutil.move(file_path, final_dest_path)
                            
                            existing_paths.append(final_dest_path)
                            comp.pdf_path = "|".join(sorted(list(set(existing_paths))))
                            await db.commit()
                            logger.info(f"✅ PDF VINCULADO: {comp.folio or 'S/N'} -> {os.path.basename(final_dest_path)}")
                        else: 
                            await handle_pair_anomaly(file_path, 'HUÉRFANO')
                    else: 
                        await handle_pair_anomaly(file_path, 'INVALID_ADN')

        except Exception as e:
            error_msg = str(e)
            logger.error(f"💀 ERROR EN INGESTA: {error_msg}")
            
            # 🛡️ INTERCEPTOR L6: SEGREGACIÓN DE LOGS POR EMPRESA
            if "Duplicado" in error_msg or "duplicado" in error_msg.lower():
                tenant_rfc = None
                # Extraemos el UUID del mensaje de error
                match = re.search(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', error_msg)
                if match:
                    dup_uuid = match.group(0)
                    try:
                        # Buscamos de quién es este UUID en la Base de Datos
                        res = await db.execute(
                            select(Tenant.rfc)
                            .join(Comprobante, Comprobante.entidad_id == Tenant.tenant_id)
                            .where(func.lower(cast(Comprobante.uuid, String)) == dup_uuid.lower())
                        )
                        tenant_rfc = res.scalar()
                    except: pass
                
                await handle_pair_anomaly(file_path, 'DUPLICADO', tenant_rfc)
            else:
                await handle_pair_anomaly(file_path, 'INVALID_ADN')
        finally:
            processing_files.discard(file_path)

# ==============================================================================
# 4. INICIO DEL WATCHER (CON APAGADO ELEGANTE L6)
# ==============================================================================
async def main():
    observer = None
    try:
        loop = asyncio.get_running_loop()
        logger.info("⚙️ INICIANDO ESCANEO DE ZONAS DINÁMICAS...")
        
        observer = Observer()
        handler = GlobalIngestHandler(loop, WATCHER_CONFIG)
        
        for zone_path, zid in WATCHER_CONFIG.items():
            if not os.path.exists(zone_path):
                os.makedirs(zone_path, exist_ok=True)
                
            observer.schedule(handler, zone_path, recursive=False)
            logger.info(f"📡 MONITOREANDO: {zone_path}")
            
            for f in os.listdir(zone_path):
                file_path = os.path.join(zone_path, f)
                if os.path.isfile(file_path):
                    await safe_process_file(file_path, zid)
            
        logger.info("🛡️ VANTEC VCORE WATCHER v3.7.6 (SMART SYNC + GHOST HEALER) ONLINE")
        observer.start()
        
        while True: 
            await asyncio.sleep(1)
            
    except asyncio.CancelledError:
        # Captura el Ctrl+C para iniciar el apagado elegante
        pass
    except Exception as e:
        logger.critical(f"🛑 FALLO CRÍTICO EN EL MOTOR: {e}")
    finally:
        if observer and observer.is_alive():
            observer.stop()
            observer.join()
        
        # 🛡️ CIERRE ORDENADO DE BASE DE DATOS (Evita el error de Garbage Collector)
        await engine.dispose()
        logger.info("🔌 BÓVEDA CERRADA: Conexiones a Base de Datos terminadas correctamente.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 WATCHER DETENIDO POR EL USUARIO.")
    except RuntimeError as e:
        if str(e) == "Event loop is closed":
            pass