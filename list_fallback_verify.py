with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "r", encoding="utf-8") as f:
    c = f.read()

verify_lines = """            # --- VERIFICACIÓN DE ARCHIVOS ---
            ruta_xml = r.ruta_resguardo or ""
            xml_exists = os.path.exists(ruta_xml) and os.path.isfile(ruta_xml) if ruta_xml else False
            pdf_exists = os.path.exists(ruta_xml.replace('.xml', '.pdf')) if ruta_xml and ruta_xml.endswith('.xml') else False"""

fallback_verify = """            # --- VERIFICACIÓN DE ARCHIVOS ---
            ruta_xml = r.ruta_resguardo or ""
            xml_exists = os.path.exists(ruta_xml) and os.path.isfile(ruta_xml) if ruta_xml else False
            pdf_exists = os.path.exists(ruta_xml.replace('.xml', '.pdf')) if ruta_xml and ruta_xml.endswith('.xml') else False

            if not xml_exists or not pdf_exists:
                 import glob
                 if not xml_exists:
                      xml_matches = glob.glob(f"storage/**/{r.uuid}.xml", recursive=True) or glob.glob(f"Operacion_CFDI/**/{r.uuid}.xml", recursive=True)
                      xml_exists = bool(xml_matches)
                 if not pdf_exists:
                      pdf_matches = glob.glob(f"storage/**/{r.uuid}.pdf", recursive=True) or glob.glob(f"Operacion_CFDI/**/{r.uuid}.pdf", recursive=True)
                      pdf_exists = bool(pdf_matches)
                      if not pdf_exists and xml_exists:
                           # Si existe el XML, el modulo fallback lo genera al descargar, de cara al frontend EXISTE.
                           pdf_exists = True"""

c = c.replace(verify_lines, fallback_verify)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "w", encoding="utf-8") as f:
    f.write(c)

print("List Verification Fallback Applied")
