from pathlib import Path
from src.core.config import settings
from datetime import datetime
import os

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
