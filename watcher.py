import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import json, time, asyncio, uuid, logging, shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.services.parser.cfdi_parser import process_inbound_file

logging.basicConfig(level=logging.INFO, format='%(asctime)s - 🛡️ VANTEC WATCHER - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()

DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "prueba01")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "gestor_cfdi")

engine = create_async_engine(f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class CfdiHandler(FileSystemEventHandler):
    def __init__(self, entidad_id, loop, inbound_path):
        self.entidad_id = uuid.UUID(entidad_id)
        self.loop = loop
        self.inbound_dir = inbound_path
        base_ops = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI"
        self.processing_dir = os.path.join(base_ops, "Pending")
        self.failed_dir = os.path.join(base_ops, "Invalid")
        self.log_dir = os.path.join(base_ops, "logs")
        os.makedirs(self.processing_dir, exist_ok=True)
        os.makedirs(self.failed_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        self.queue = asyncio.Queue()
        asyncio.run_coroutine_threadsafe(self.worker(), self.loop)

    def on_created(self, event):
        if not event.is_directory:
            if event.src_path.lower().endswith(".xml"):
                self.loop.call_soon_threadsafe(self.queue.put_nowait, event.src_path)
            elif event.src_path.lower().endswith(".pdf"):
                asyncio.run_coroutine_threadsafe(self.process_pdf_async(event.src_path), self.loop)

    async def worker(self):
        batch_size = 50
        while True:
            batch = []
            try:
                first_item = await self.queue.get()
                batch.append(first_item)
                
                for _ in range(batch_size - 1):
                    try:
                        item = self.queue.get_nowait()
                        batch.append(item)
                    except asyncio.QueueEmpty:
                        break
                
                logger.info(f"🚀 Iniciando Batch concurrente de {len(batch)} documentos...")
                tasks = []
                for file_path in batch:
                    tasks.append(self.process_file_async(file_path))
                
                await asyncio.gather(*tasks, return_exceptions=True)
                
                for _ in batch:
                    self.queue.task_done()
                
                logger.info(f"✅ Batch completado. Liberando memoria para el siguiente ciclo...")
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Error en worker batch: {e}")

    async def bootstrap_scan(self, path):
        logger.info(f"🔄 Iniciando bootstrap_scan en {path}")
        if not os.path.exists(path): return
        files = os.listdir(path)
        logger.info(f"🔎 Se encontraron {len(files)} archivos para ingesta inicial en {path}")
        for f in files:
            if f.lower().endswith(".xml"): 
                await self.queue.put(os.path.join(path, f))
            elif f.lower().endswith(".pdf"): 
                await self.process_pdf_async(os.path.join(path, f))

    async def process_pdf_async(self, file_path):
        await asyncio.sleep(5)
        if os.path.exists(file_path): logger.warning(f"⚠️ PDF omitido: {file_path}")

    async def process_file_async(self, file_path):
        if not os.path.exists(file_path): return
        async with AsyncSessionLocal() as db:
            base_path, _ = os.path.splitext(file_path)
            ruta_pdf = base_path + ".pdf" if os.path.exists(base_path + ".pdf") else None
            if not ruta_pdf:
                try:
                    import defusedxml.ElementTree as ET
                    root = ET.parse(file_path).getroot()
                    ser = root.get('Serie') or root.get('serie') or ""
                    fol = root.get('Folio') or root.get('folio') or ""
                    fol_cl = str(fol).lstrip('0') if fol else ""
                    dp = os.path.dirname(file_path)
                    bn = os.path.splitext(os.path.basename(file_path))[0]
                    cands = [
                        os.path.join(dp, f"{ser}{fol}.pdf"),
                        os.path.join(dp, f"{ser}-{fol}.pdf"),
                        os.path.join(dp, f"{ser}{fol_cl}.pdf"),
                        os.path.join(dp, f"{ser}-{fol_cl}.pdf"),
                        os.path.join(dp, f"{fol_cl}.pdf"),
                        os.path.join(dp, f"{bn}.pdf")
                    ]
                    for c in cands:
                        if os.path.exists(c):
                            ruta_pdf = c
                            break
                except Exception: pass

            fn = os.path.basename(file_path)
            p_xml = os.path.join(self.processing_dir, fn)
            p_pdf = os.path.join(self.processing_dir, os.path.basename(ruta_pdf)) if ruta_pdf else None

            try:
                shutil.move(file_path, p_xml)
                if ruta_pdf and os.path.exists(ruta_pdf): shutil.move(ruta_pdf, p_pdf)
                await process_inbound_file(p_xml, self.failed_dir, self.log_dir, db, self.entidad_id)
                if p_pdf and os.path.exists(p_pdf):
                    # Guardar para traslado, no borrar
                    logger.info(f"PDF resguardado en procesamiento: {p_pdf}")
            except Exception as e:
                self._move_to_error(p_xml, str(e), p_pdf)

    def _move_to_error(self, f_path, e_str="Error", p_path=None):
        if not os.path.exists(f_path): return
        fn = os.path.basename(f_path)
        try:
            if os.path.exists(f_path): shutil.move(f_path, os.path.join(self.failed_dir, fn))
            if p_path and os.path.exists(p_path): shutil.move(p_path, os.path.join(self.failed_dir, os.path.basename(p_path)))
            with open(os.path.join(self.log_dir, f"{os.path.splitext(fn)[0]}_error.log"), "w", encoding='utf-8') as f:
                f.write(f"Error en {fn}\nDetalle: {e_str}\n")
        except Exception as e: logger.error(f"🚨 Error moviendo a failed: {e}")

async def main():
    zones = json.loads(os.getenv("WATCHER_ZONES", "{}"))
    if not zones: return
    loop = asyncio.get_running_loop()
    observer = Observer()
    for path, ent_id in zones.items():
        os.makedirs(path, exist_ok=True)
        h = CfdiHandler(ent_id, loop, path)
        observer.schedule(h, path, recursive=False)
        await h.bootstrap_scan(path)
    observer.start()
    try:
        while True: await asyncio.sleep(1)
    except KeyboardInterrupt: observer.stop()
    observer.join()

if __name__ == "__main__": asyncio.run(main())