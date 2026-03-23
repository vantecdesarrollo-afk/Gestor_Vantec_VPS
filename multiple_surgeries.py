import os

# --- Fix 1 & 2: comprobantes.py ---
with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "r", encoding="utf-8") as f:
    c = f.read()

# Fix 1: Detail fallback TipoDeComprobante from XML
import_lines = "                    import xml.etree.ElementTree as ET"
detail_fix = """                    import xml.etree.ElementTree as ET
                    tipo_comp = "I"
                    if hasattr(alt_comp, 'xml_file_path') and os.path.exists(alt_comp.xml_file_path):
                        try:
                            import defusedxml.ElementTree as DET
                            root = DET.parse(alt_comp.xml_file_path).getroot()
                            tipo_comp = root.get('TipoDeComprobante') or root.get('tipoDeComprobante') or "I"
                        except Exception: pass
                    return {
                        "uuid": alt_comp.uuid,
                        "serie": getattr(alt_comp, "serie", ""),
                        "folio": getattr(alt_comp, "folio", ""),
                        "tipo_comprobante": tipo_comp, 
                        "metodo_pago": getattr(alt_comp, "metodo_pago", "---"),
                        "forma_pago": getattr(alt_comp, "forma_pago", "---"),"""

c = c.replace(
"""                    return {
                        "uuid": alt_comp.uuid,
                        "serie": getattr(alt_comp, "serie", ""),
                        "folio": getattr(alt_comp, "folio", ""),
                        "tipo_comprobante": getattr(alt_comp, "tipo_comprobante", "I"),
                        "metodo_pago": getattr(alt_comp, "metodo_pago", "---"),
                        "forma_pago": getattr(alt_comp, "forma_pago", "---"),""",
detail_fix
)

# Fix 2: Bubble subprocess error to Frontend in PDF endpoint
c = c.replace(
"""                 except Exception as e_pdf:
                      print(f"Error generando PDF: {str(e_pdf)}")

            raise HTTPException(status_code=404, detail="Archivo PDF no encontrado en rutas de resguardo")""",
"""                 except Exception as e_pdf:
                      raise HTTPException(status_code=500, detail=f"Fallo en generación automática de PDF: {str(e_pdf)}")

            raise HTTPException(status_code=404, detail="Archivo PDF no encontrado en rutas de resguardo y fallo la generación")"""
)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "w", encoding="utf-8") as f:
    f.write(c)

# --- Fix 3: mailVantec.py ---
with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\microservices\mailer\mailVantec.py", "r", encoding="utf-8") as f:
    m = f.read()

m = m.replace(
"""        else:
            log_error(f"Adjunto no encontrado y omitido: {archivo}")""",
"""        else:
            log_error(f"Adjunto no encontrado: {archivo}")
            sys.exit(1)"""
)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\microservices\mailer\mailVantec.py", "w", encoding="utf-8") as f:
    f.write(m)

print("Multiple Surgeries Done")
