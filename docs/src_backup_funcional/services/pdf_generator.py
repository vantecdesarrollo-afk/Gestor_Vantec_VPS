import os
import logging
logger = logging.getLogger(__name__)

def generate_pdf_from_xml(xml_path: str, dest_pdf: str, uuid_val: str, logo_path: str = None) -> bool:
    # SUPRIMIDO (DIRECTIVA VCORE): "Matar el Template".
    # Eliminada la generación automática de PDFs para evitar renders genéricos.
    logger.warning("Intento de generación dinámica de PDF bloqueado. El sistema ahora exige binarios originales (SSoT).")
    return False
