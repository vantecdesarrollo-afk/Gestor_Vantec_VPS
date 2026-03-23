with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "r", encoding="utf-8") as f:
    c = f.read()

old_block = """                     if not xml_exists and att["xml_path"]:
                          xml_exists = True
                     if not pdf_exists and att["pdf_path"]:
                          pdf_exists = True"""

new_block = """                     if not xml_exists and att["xml_path"]:
                          xml_exists = True
                     if not pdf_exists and att["pdf_path"]:
                          pdf_exists = True
                          
                     # Idempotencia y Resiliencia (Libro 1): Si existe XML, la API genera el PDF On-the-Fly de emergencia
                     if not pdf_exists and xml_exists:
                          pdf_exists = True"""

c = c.replace(old_block, new_block)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "w", encoding="utf-8") as f:
    f.write(c)

print("Resilience On-the-Fly fallback restored correctly.")
