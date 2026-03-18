import sys
import os

# Set PYTHONPATH
sys.path.append(os.getcwd())

try:
    from src.database.models import Base
    from sqlalchemy import create_mock_engine
    from sqlalchemy.orm import sessionmaker
    
    # Just importing and accessing the mapper should trigger the error if it exists
    from src.database.models import EntidadFiscal, PlantillaCorreo
    
    print("[+] Modelos cargados exitosamente.")
    print(f"[+] EntidadFiscal has plantillas_correo relationship: {'plantillas_correo' in EntidadFiscal.__mapper__.relationships}")
    
except Exception as e:
    print(f"[-] Error fatal de ORM: {e}")
    sys.exit(1)
