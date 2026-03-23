import os

print("--- 1. Limpiando Forzado Artificial en comprobantes.py ---")
with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "Idempotencia y Resiliencia" in line:
        print(f"Encontrado forzado artificial en línea {i+1}, removiendo...")
        # Remover 3 líneas: comentario e IF de 2 lineas
        lines[i] = ""
        lines[i+1] = ""
        lines[i+2] = ""
        break

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "w", encoding="utf-8") as f:
    f.write("".join(lines))


print("\n--- 2. Re-escribiendo find_cfdi_attachments completo en cfdi_storage.py ---")
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
    
    # 1. Workspace UUID (Idempotencia Atómica)
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
              
    if not xml_path:
         # Fallback histórico solo para XML
         historical_xml = [
              f"C:\\\\ITC\\\\Fappeal\\\\Planeta\\\\Outfile\\\\SAT\\\\Factura\\\\**\\\\{folio}.xml",
              f"C:\\\\ITC\\\\Fappeal\\\\Planeta\\\\Outfile\\\\SAT\\\\Factura\\\\**\\\\{clean_folio}.xml"
         ]
         for h in historical_xml:
              matches = glob.glob(h, recursive=True)
              if matches:
                   xml_path = matches[0]
                   break

    for c in pdf_candidates:
         matches = glob.glob(c, recursive=True)
         if matches:
              pdf_path = matches[0]
              break

    # 3. Solución Adyacente Atómica: Evita colisiones de wildcard en PDFs
    if xml_path and not pdf_path:
         adj_pdf = xml_path.replace('.xml', '.pdf')
         if os.path.exists(adj_pdf):
              pdf_path = adj_pdf

    return { "xml_path": xml_path, "pdf_path": pdf_path }
"""

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\services\cfdi_storage.py", "w", encoding="utf-8") as f:
    f.write(s)

print("Helper find_cfdi_attachments sobreescrito con lógica Adyacente Atómica de forma exitosa.")
print("Comprobantes.py forzado limpiado.")
