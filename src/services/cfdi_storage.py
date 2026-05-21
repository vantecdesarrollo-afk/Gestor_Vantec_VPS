from pathlib import Path, PureWindowsPath
from src.core.config import settings
from datetime import datetime
import os

def normalize_vcore_path(path_str: str) -> str:
    """
    Normaliza rutas absolutas o relativas de Windows a Linux en el VPS.
    Extrae de forma limpia el nombre del archivo y estructura de directorios,
    y los mapea contra las raíces correctas en el contenedor de producción.
    """
    if not path_str:
        return ""
        
    import re
    from pathlib import PureWindowsPath
    
    # Reemplazar backslashes por slashes estándar
    path_normalized = path_str.replace('\\', '/')
    
    # 1. Si el archivo ya existe tal cual, retornarlo de inmediato
    if os.path.exists(path_normalized) and os.path.isfile(path_normalized):
        return path_normalized

    # Usar PureWindowsPath para un parseo robusto independiente del SO actual
    win_path = PureWindowsPath(path_str)
    
    # Obtener partes de la ruta
    parts = list(win_path.parts)
    parts_lower = [p.lower() for p in parts]
    
    # Resolver ruta del proyecto (/app en producción)
    app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Caso 1: Ruta bajo 'Operacion_CFDI' (resguardo fiscal estándar)
    if 'operacion_cfdi' in parts_lower:
        idx = parts_lower.index('operacion_cfdi')
        relative_parts = parts[idx+1:]
        resolved = os.path.join(app_root, "Operacion_CFDI", *relative_parts)
        if os.path.exists(resolved):
            return resolved
        return resolved

    # Caso 2: Ruta bajo 'storage' (múltiples PDFs o resguardo legacy)
    if 'storage' in parts_lower:
        idx = parts_lower.index('storage')
        relative_parts = parts[idx+1:]
        
        # settings.STORAGE_PATH es la ruta real montada (/storage)
        from src.core.config import settings
        storage_root = str(settings.STORAGE_PATH)
        resolved = os.path.join(storage_root, *relative_parts)
        if os.path.exists(resolved):
            return resolved
        return resolved
        
    # Caso 3: Fallback de reconstrucción dinámica por componentes
    # Si la ruta tiene formato Windows (contiene ':' o '\'), extraemos los componentes clave
    if '\\' in path_str or (len(parts) > 0 and ':' in parts[0]):
        filename = win_path.name
        
        # Patrones para buscar RFC, Año, Mes y UUID de Entidad
        rfc_pattern = re.compile(r'^[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}$', re.IGNORECASE)
        year_pattern = re.compile(r'^\d{4}$')
        month_pattern = re.compile(r'^\d{2}$')
        day_pattern = re.compile(r'^\d{2}$')
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
        
        rfc_part = None
        year_part = None
        month_part = None
        day_part = None
        uuid_part = None
        
        for part in parts:
            if rfc_pattern.match(part):
                rfc_part = part
            elif year_pattern.match(part) and 2000 <= int(part) <= 2100:
                year_part = part
            elif month_pattern.match(part) and 1 <= int(part) <= 12:
                month_part = part
            elif day_pattern.match(part) and 1 <= int(part) <= 31:
                day_part = part
            elif uuid_pattern.match(part):
                uuid_part = part
                
        # Si es un XML, suele ir en Operacion_CFDI/Files/{RFC}/{YEAR}/{MONTH}/{filename}
        if filename.lower().endswith('.xml') and rfc_part and year_part and month_part:
            resolved = os.path.join(app_root, "Operacion_CFDI", "Files", rfc_part, year_part, month_part, filename)
            return resolved
            
        # Si es un PDF y tenemos la estructura de storage, reconstruirla en STORAGE_PATH
        if filename.lower().endswith('.pdf') and uuid_part and rfc_part and year_part and month_part:
            from src.core.config import settings
            storage_root = str(settings.STORAGE_PATH)
            if day_part:
                resolved = os.path.join(storage_root, uuid_part, rfc_part, year_part, month_part, day_part, filename)
            else:
                resolved = os.path.join(storage_root, uuid_part, rfc_part, year_part, month_part, filename)
            return resolved
            
        # Fallback de último recurso: STORAGE_PATH / filename
        from src.core.config import settings
        storage_root = str(settings.STORAGE_PATH)
        return os.path.join(storage_root, filename)
        
    return path_normalized

def construir_ruta_archivo(tenant_id: str, rfc_emisor: str, fecha_emision: datetime, uuid: str, formato: str) -> Path:
    formato = formato.lstrip('.')
    year = str(fecha_emision.year)
    month = f"{fecha_emision.month:02d}"
    day = f"{fecha_emision.day:02d}"
    relative_path = Path(str(tenant_id)) / rfc_emisor / year / month / day / f"{uuid}.{formato}"
    return settings.VANTEC_CFDI_ROOT / relative_path

def get_cfdi_vault_path(tenant_id: str, rfc_emisor: str, fecha_emision: datetime) -> str:
    year = str(fecha_emision.year)
    month = f"{fecha_emision.month:02d}"
    day = f"{fecha_emision.day:02d}"
    relative_path = Path(str(tenant_id)) / rfc_emisor / year / month / day
    return str(settings.VANTEC_CFDI_ROOT / relative_path)

def find_cfdi_attachments(uuid: str, serie: str = "", folio: str = "", tipo: str = "") -> dict:
    """
    Versión Optimizada V-Core: Evita glob recursivo (**) que causa congelamiento.
    Confía en rutas SSoT fijas o búsquedas limitadas.
    """
    xml_path = None
    pdf_path = None
    
    # 1. Rutas Estándar Vantec
    # Buscamos en las localizaciones donde el sistema los guarda por defecto.
    # Operacion_CFDI/Files/[RFC]/[YEAR]/[MONTH]/uuid.xml
    
    # Nota: Como no tenemos el RFC/FECHA aquí fácilmente, lo ideal es que 
    # comprobantes.py NO use esta función para el listado masivo,
    # sino que use los campos xml_path/pdf_path de la base de datos.
    
    # Fallback rápido si el archivo está en la raíz de storage (casos legacy)
    app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    legacy_roots = [
        os.path.join(app_root, "storage"),
        os.path.join(app_root, "Operacion_CFDI", "Upload_Universal"),
        os.path.join(app_root, "Operacion_CFDI", "logs", "duplicates")
    ]
    
    for root in legacy_roots:
        if not os.path.exists(root): continue
        # Verificamos solo el nivel base para evitar el freeze
        p_xml = os.path.join(root, f"{uuid}.xml")
        p_pdf = os.path.join(root, f"{uuid}.pdf")
        if os.path.exists(p_xml): xml_path = p_xml
        if os.path.exists(p_pdf): pdf_path = p_pdf
        
        if xml_path and pdf_path: break

    return {"xml_path": xml_path, "pdf_path": pdf_path}
