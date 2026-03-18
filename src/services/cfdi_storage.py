from pathlib import Path
from src.core.config import settings
from datetime import datetime

def construir_ruta_archivo(tenant_id: str, rfc_emisor: str, fecha_emision: datetime, uuid: str, formato: str) -> Path:
    """
    Construye la ruta topográfica jerárquica para el almacenamiento de archivos CFDI.
    Formato: /{tenant_id}/{rfc_emisor}/{año}/{mes}/{dia}/{uuid}.{formato}
    """
    # Asegurar que el formato no tenga el punto inicial
    formato = formato.lstrip('.')
    
    # Extraer componentes de la fecha
    year = str(fecha_emision.year)
    month = f"{fecha_emision.month:02d}"
    day = f"{fecha_emision.day:02d}"
    
    # Construir la ruta relativa
    relative_path = Path(str(tenant_id)) / rfc_emisor / year / month / day / f"{uuid}.{formato}"
    
    # Unir con la raíz de almacenamiento definida en la configuración
    return settings.VANTEC_CFDI_ROOT / relative_path
