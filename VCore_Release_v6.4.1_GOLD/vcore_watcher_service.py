import sys
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import os
import asyncio
from pathlib import Path

# Configuración Dinámica (L6 Protocol)
BASE_PATH = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE_PATH))

class VCoreWatcherService(win32serviceutil.ServiceFramework):
    _svc_name_ = "VCore_Watcher"
    _svc_display_name_ = "Vantec VCore Engine (Watcher)"
    _svc_description_ = "Implementa el motor de triaje fiscal L6 para ingesta de documentos"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_requested = False
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.stop_requested = True

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                             servicemanager.PYS_SERVICE_STARTED,
                             (self._svc_name_, ''))
        self.main()

    def main(self):
        # Importar el watcher y ejecutar su loop de asyncio
        from watcher import main as watcher_main
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Iniciar watcher en segundo plano
        watcher_task = loop.create_task(watcher_main())
        
        # Bucle de monitoreo de stop
        while not self.stop_requested:
            # Esperar a que el evento de stop se active o 1 segundo de sleep
            rc = win32event.WaitForSingleObject(self.stop_event, 1000)
            if rc == win32event.WAIT_OBJECT_0:
                break
                
        # Detener suavemente el watcher (si el watcher tuviera una forma de cancelar, se haría aquí)
        # Como watcher.main() es un loop infinito, la detención del proceso de servicio lo forzará.
        # Pero podemos intentar cancelar la task
        watcher_task.cancel()
        try:
            loop.run_until_complete(watcher_task)
        except asyncio.CancelledError:
            pass
        loop.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        win32serviceutil.HandleCommandLine(VCoreWatcherService)
    else:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(VCoreWatcherService)
        servicemanager.StartServiceCtrlDispatcher()
