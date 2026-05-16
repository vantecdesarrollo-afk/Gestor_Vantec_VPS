import sys, os, time, subprocess, signal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Vanteg VCore Integrated Manager v2.0 (Directiva L6 v4.2)
# Responsable de Autorestart + Hot-Reload + Dashboard Management
# ─────────────────────────────────────────────────────────────────────────

WATCH_FILES = ["watcher.py", "vcore_manager.py"]
RELOAD_DELAY = 2.0 

class VCoreReloader(FileSystemEventHandler):
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback
        self.last_reload = time.time()

    def on_modified(self, event):
        if not event.is_directory:
            rel_path = os.path.relpath(event.src_path, ".")
            if rel_path in WATCH_FILES or rel_path.startswith("src"):
                if time.time() - self.last_reload > RELOAD_DELAY:
                    print(f"HOT-RELOAD: Detectado cambio en {rel_path}. Reiniciando Sistema Integral...")
                    self.last_reload = time.time()
                    self.restart_callback()

def run_manager():
    engine_proc = None
    dashboard_proc = None

    def start_all():
        nonlocal engine_proc, dashboard_proc
        
        # 1. Cleanup Previo
        for p in [engine_proc, dashboard_proc]:
            if p:
                try:
                    p.terminate()
                    p.wait(timeout=5)
                except:
                    try: p.kill()
                    except: pass

        # 2. Iniciar ENGINE (Watcher)
        print("INICIANDO VCORE ENGINE (Watcher)...")
        engine_proc = subprocess.Popen([sys.executable, "watcher.py"], 
                                      env=os.environ,
                                      stdout=sys.stdout,
                                      stderr=sys.stderr,
                                      creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)

        # 3. Iniciar DASHBOARD (FastAPI)
        print("INICIANDO VCORE DASHBOARD (Uvicorn)...")
        # uvicorn src.main:app --host 127.0.0.1 --port 8000
        dashboard_proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8000"],
                                         env=os.environ,
                                         stdout=sys.stdout,
                                         stderr=sys.stderr,
                                         creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)

    # Observer para Hot-Reload
    observer = Observer()
    reloader = VCoreReloader(start_all)
    observer.schedule(reloader, path=".", recursive=True)
    observer.start()

    try:
        start_all()
        while True:
            time.sleep(5)
            # Monitorizar Engine
            if engine_proc.poll() is not None:
                print(f"ALERTA: Motor detenido (Code: {engine_proc.returncode}). Reiniciando Engine...")
                start_all() # Reiniciamos todo para mantener sincronía
                continue
            
            # Monitorizar Dashboard
            if dashboard_proc.poll() is not None:
                print(f"ALERTA: Dashboard detenido (Code: {dashboard_proc.returncode}). Reiniciando Dashboard...")
                start_all()
                continue
                
    except KeyboardInterrupt:
        print("\nDeteniendo Manager...")
        observer.stop()
        for p in [engine_proc, dashboard_proc]:
            if p: p.terminate()
    observer.join()

if __name__ == "__main__":
    print("VANTEC VCORE INTEGRATED MANAGER v2.0")
    print("---------------------------------------")
    run_manager()
