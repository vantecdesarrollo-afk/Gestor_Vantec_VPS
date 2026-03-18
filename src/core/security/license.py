import jwt
import os
import uuid
import logging
from fastapi import HTTPException, status, Request
from pathlib import Path

logger = logging.getLogger(__name__)

# Llave pública de Vantec (Solo validación, jamás incluir la privada aquí)
VANTEC_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnT1ApR6ArPehpTyXn6OM
1GHbOcDzaEdph2+VFLN031N6Q1oN8hPl4/IEYwg1G5sDAiUSR8Lq98R83k0KnTwh
nfqhoXNe5dkaZr5N0plsWM68L5lONUNCLEBTAxBrJMwiIOyNBqlT9MDnh4vd1L2Z
ZGcZn4gpopI0zvPt5JrE90CNMI/4pYr7RwlrWJ8sLavopwcJ6uDcxnU5/VXrTkqL
E8FOOBlkPLTCVd9tvFHLT6EnFiOwNmP8C4hUkynAKOmPllRLwQe3eWbzimP1g5pC
UEHWEejeevS66hoGwhhp5HWUJKKiLuzRQiO6UWfMd+p33jffXm3DIdCW1+RrSWBl
7QIDAQAB
-----END PUBLIC KEY-----"""

def get_license_dir() -> Path:
    """Detecta si estamos en Windows (Local) o Linux (Docker) para la ruta de la licencia"""
    if os.name == 'nt':
        return Path(r"C:\Vantec\Gestor_CFDI\license")
    return Path("/app/storage/license")

def get_machine_id() -> str:
    """
    Obtiene el ID único de la máquina anfitriona.
    """
    try:
        # Prioridad: Leer archivo inyectado por el instalador .bat en C:\Vantec\... o Docker
        machine_id_path = get_license_dir() / "machine_id.txt"
        if machine_id_path.exists():
            return machine_id_path.read_text().strip()
            
        # Fallback si no existe el archivo .txt
        return ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
                         for ele in range(0,8*6,8)][::-1])
    except Exception as e:
        logger.error(f"Error leyendo Machine ID: {e}")
        return "UNKNOWN_MACHINE"

async def verify_license(request: Request):
    """
    Dependency global para validar la licencia de Vantec Consultores.
    Integrar en fastapi como Depends(verify_license).
    """
    require_license = os.getenv("REQUIRE_LICENSE", "True").lower() in ("true", "1", "t")
    
    if not require_license:
        return True # Bypass para QA interno

    current_machine_id = get_machine_id()
    license_dir = get_license_dir()
    license_path = license_dir / "vantec_license.jwt"
    
    if not license_path.exists():
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Licencia Vantec no encontrada. Por favor contacte a su proveedor. (Machine ID: {current_machine_id})"
        )

    token = license_path.read_text().strip()

    try:
        # PyJWT valida automáticamente la firma y la fecha 'exp'
        payload = jwt.decode(token, VANTEC_PUBLIC_KEY, algorithms=["RS256"])
        
        # Validación de piratería / clonación de contenedores
        licensed_machine_id = payload.get("machine_id")
        if licensed_machine_id != current_machine_id:
            logger.error(f"Alerta de Piratería: Licencia para {licensed_machine_id}, ejecutada en {current_machine_id}")
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Licencia inválida para este hardware (Violación de términos detectada). (Machine ID: {current_machine_id})"
            )
            
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"La licencia de su Gestor CFDI ha expirado. Proceda con la renovación. (Machine ID: {current_machine_id})"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Firma de licencia corrupta o inválida. (Machine ID: {current_machine_id})"
        )