import os

print("--- 1. Reparando cfdi_storage.py con Vinculación Histórica Directa ---")
s = """from pathlib import Path
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
    import glob
    import os
    xml_path = None
    pdf_path = None
    
    clean_folio = str(folio).lstrip('0') if folio else ""
    
    # 1. Buscar en Workspace por UUID (Idempotencia Atómica)
    xml_candidates = [
         f"C:\\\\Test_Antigravity\\\\Gestor_CFDI_Vantec\\\\storage\\\\**\\\\{uuid}.xml",
         f"C:\\\\Test_Antigravity\\\\Gestor_CFDI_Vantec\\\\Operacion_CFDI\\\\**\\\\{uuid}.xml"
    ]
    pdf_candidates = [
         f"C:\\\\Test_Antigravity\\\\Gestor_CFDI_Vantec\\\\storage\\\\**\\\\{uuid}.pdf",
         f"C:\\\\Test_Antigravity\\\\Gestor_CFDI_Vantec\\\\Operacion_CFDI\\\\**\\\\{uuid}.pdf"
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

    # 2. Resiliencia Histórica: Si no tiene PDF en el Workspace, buscar en ERP Histórico
    if not pdf_path and folio:
         historical_xml = [
              f"C:\\\\ITC\\\\Fappeal\\\\Planeta\\\\Outfile\\\\SAT\\\\Factura\\\\**\\\\{folio}.xml",
              f"C:\\\\ITC\\\\Fappeal\\\\Planeta\\\\Outfile\\\\SAT\\\\Factura\\\\**\\\\{clean_folio}.xml"
         ]
         for h in historical_xml:
              matches = glob.glob(h, recursive=True)
              if matches:
                   # Si se encuentra el XML histórico, el PDF DEBE estar en la misma carpeta adyacente (Cero Colisión)
                   adj_pdf = matches[0].replace('.xml', '.pdf')
                   if os.path.exists(adj_pdf):
                        pdf_path = adj_pdf
                        # Si además no teníamos XML, usar esta ruta histórica
                        if not xml_path:
                             xml_path = matches[0]
                   break

    return { "xml_path": xml_path, "pdf_path": pdf_path }
"""

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\services\cfdi_storage.py", "w", encoding="utf-8") as f:
    f.write(s)

print("Helper de almacenamiento re-construido con protección anti-colisión.")


print("\n--- 2. Homologando Casteo Boolean en cfdis.js (Frontend) ---")
with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "r", encoding="utf-8") as f:
    c = f.read()

old_cast_pdf = "const pdf_exists = cfdi.pdf_exists === true;"
new_cast_pdf = "const pdf_exists = cfdi.pdf_exists === true || cfdi.pdf_exists === 'true';"

old_cast_xml = "const xml_exists = cfdi.xml_exists === true;"
new_cast_xml = "const xml_exists = cfdi.xml_exists === true || cfdi.xml_exists === 'true';"

if old_cast_pdf in c:
    c = c.replace(old_cast_pdf, new_cast_pdf)
    print("Casteo PDF homologado.")
if old_cast_xml in c:
    c = c.replace(old_cast_xml, new_cast_xml)
    print("Casteo XML homologado.")

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "w", encoding="utf-8") as f:
    f.write(c)

print("Ambos componentes sincronizados.")
