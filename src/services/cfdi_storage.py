from pathlib import Path
from src.core.config import settings
from datetime import datetime

def construir_ruta_archivo(tenant_id: str, rfc_emisor: str, fecha_emision: datetime, uuid: str, formato: str) -> Path:
    formato = formato.lstrip('.')
    year = str(fecha_emision.year)
    month = f"{fecha_emision.month:02d}"
    day = f"{fecha_emision.day:02d}"
    relative_path = Path(str(tenant_id)) / rfc_emisor / year / month / day / f"{uuid}.{formato}"
    return settings.VANTEC_CFDI_ROOT / relative_path

def find_cfdi_attachments(uuid: str, serie: str = "", folio: str = "", tipo: str = "") -> dict:
    import os
    xml_path = None
    pdf_path = None
    
    clean_folio = str(folio).lstrip('0') if folio else ""
    
    # 1. Búsqueda rápida estática (Optimización para Evitar Congelamiento V-Core)
    base_dirs = [
        "C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\storage",
        "C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\Operacion_CFDI",
        "C:\\ITC"
    ]
    
    nombres_xml = [f"{uuid}.xml", f"{folio}.xml", f"{clean_folio}.xml", f"{str(clean_folio).zfill(10)}.xml"]
    nombres_pdf = [f"{uuid}.pdf", f"{folio}.pdf", f"{clean_folio}.pdf", f"{str(clean_folio).zfill(10)}.pdf"]

    def walk_fast(root_dir, target_names):
        try:
            for subdir, _, files in os.walk(root_dir):
                for f in files:
                    if f.lower() in [n.lower() for n in target_names]:
                        return os.path.join(subdir, f)
        except Exception:
            pass
        return None

    # En lugar de glob.glob(**) completo, hacemos walk condicional, pero limitamos profundidad o solo usamos SQL si existe, 
    # Sin embargo, como el requerimiento es solo optimizar: usaremos glob condicional SOLO para storage local
    
    import glob
    xml_candidates = [
         f"C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\storage\\**\\{uuid}.xml",
         f"C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\Operacion_CFDI\\**\\{uuid}.xml"
    ]
    pdf_candidates = [
         f"C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\storage\\**\\{uuid}.pdf",
         f"C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\Operacion_CFDI\\**\\{uuid}.pdf"
    ]
    
    for c in xml_candidates:
         matches = glob.glob(c, recursive=True)
         if matches:
              xml_path = matches[0]
              break

    for c in pdf_candidates:
         matches = glob.glob(c, recursive=True)
         if matches:
              pdf_path = matches[0]
              break

    # 2. Resiliencia Histórica - OPTIMIZADA: Solo en rutas conocidas y NO recursivo en todo C:
    if not xml_path and folio:
         for d in ["C:\\ITC\\XML", "C:\\ITC\\Comprobantes"]:
              if os.path.exists(d):
                  for name in nombres_xml:
                       p = os.path.join(d, name)
                       if os.path.exists(p):
                            xml_path = p
                            break

    if not pdf_path and folio:
         for d in ["C:\\ITC\\PDF", "C:\\ITC\\Comprobantes"]:
              if os.path.exists(d):
                  for name in nombres_pdf:
                       p = os.path.join(d, name)
                       if os.path.exists(p):
                            pdf_path = p
                            break
                   
    # Ultimo fallback transversal desde el adyacente
    if not pdf_path and xml_path and os.path.exists(xml_path.replace('.xml', '.pdf')):
         pdf_path = xml_path.replace('.xml', '.pdf')

    return { "xml_path": xml_path, "pdf_path": pdf_path }

