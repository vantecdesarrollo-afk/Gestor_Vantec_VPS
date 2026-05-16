import sys
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import os
import uvicorn
import asyncio
from pathlib import Path

# Configuración Dinámica (L6 Protocol)
BASE_PATH = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE_PATH))

class VCoreApiService(win32serviceutil.ServiceFramework):
    _svc_name_ = "VCore_API"
    _svc_display_name_ = "Vantec VCore Dashboard API Service"
    _svc_description_ = "Provee el Dashboard y API REST para el Gestor de CFDI (Puerto 8000)"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.stop_requested = False

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
        # Asegurar entorno y carga de .env
        from dotenv import load_dotenv
        load_dotenv(BASE_PATH / ".env")
        
        # Iniciar uvicorn
        config = uvicorn.Config("src.main:app", 
                               host="0.0.0.0", 
                               port=8000, 
                               log_level="info",
                               workers=1)
        server = uvicorn.Server(config)
        
        # Ejecutar en loop secundario para monitorear el evento de stop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        server_task = loop.create_task(server.serve())
        
        # Bucle de monitoreo de stop
        while not self.stop_requested:
            loop.run_until_complete(asyncio.sleep(1))
            if server.should_exit:
                break
        
        # Shutdown suave
        server.should_exit = True
        loop.run_until_complete(server_task)
        loop.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        win32serviceutil.HandleCommandLine(VCoreApiService)
    else:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(VCoreApiService)
        servicemanager.StartServiceCtrlDispatcher()
