with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "r", encoding="utf-8") as f:
    c = f.read()

fallback_logic = """        if alt_comp and alt_comp.pdf_file_path and os.path.exists(alt_comp.pdf_file_path):
            actual_path = alt_comp.pdf_file_path
        else:
            # Fallback Generación On-the-Fly wkhtmltopdf
            xml_path = None
            if comp and comp.ruta_resguardo:
                 if os.path.exists(comp.ruta_resguardo): xml_path = comp.ruta_resguardo
                 elif os.path.exists(comp.ruta_resguardo.replace('.pdf', '.xml')): xml_path = comp.ruta_resguardo.replace('.pdf', '.xml')
            
            if not xml_path or not os.path.exists(xml_path):
                 import glob
                 xml_matches = glob.glob(f"**/{uuid}.xml", recursive=True)
                 if xml_matches: xml_path = xml_matches[0]
            
            if not xml_path and alt_comp and os.path.exists(alt_comp.xml_file_path):
                 xml_path = alt_comp.xml_file_path
                 
            if xml_path and os.path.exists(xml_path):
                 try:
                      pdf_kit_path = os.getenv("WKHTMLTOPDF_PATH", r"C:\\Test_Antigravity\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
                      dest_pdf = xml_path.replace('.xml', '.pdf')
                      
                      import xml.etree.ElementTree as ET
                      import subprocess
                      tree = ET.parse(xml_path)
                      root = tree.getroot()
                      ns = {'cfdi': 'http://www.sat.gob.mx/cfd/4', 'cfdi33': 'http://www.sat.gob.mx/cfd/3'}
                      
                      emisor = root.find('.//cfdi:Emisor', ns) or root.find('.//cfdi33:Emisor', ns)
                      nombre_emisor = emisor.get('Nombre', '') if emisor is not None else "---"
                      conceptos_nodes = root.findall('.//cfdi:Concepto', ns) or root.findall('.//cfdi33:Concepto', ns)
                      concept_html = "".join([f"<tr><td>{c.get('Descripcion')}</td><td>{c.get('Cantidad')}</td><td>{c.get('ValorUnitario')}</td><td>{c.get('Importe')}</td></tr>" for c in conceptos_nodes])
                      total_f = root.get('Total', '') or root.get('total', '')
                      
                      html = f\"\"\"<html><body style='font-family: Arial; padding: 20px;'>
                      <h2>CFDI Auxiliar - Vista Previa</h2><p><b>UUID:</b> {uuid}</p><p><b>Emisor:</b> {nombre_emisor}</p><p><b>Total:</b> {total_f}</p>
                      <table border='1' width='100%' style='border-collapse: collapse; margin-top: 20px;'>
                        <tr style='background: #f2f2f2;'><th>Descripción</th><th>Cant</th><th>Precio</th><th>Importe</th></tr>{concept_html}
                      </table><p style='font-size: 10px; color: gray; margin-top: 40px;'>Generado de emergencia Gestor Vantec</p></body></html>\"\"\"
                      
                      tmp_html = f"C:\\\\Test_Antigravity\\\\Gestor_CFDI_Vantec\\\\{uuid}.html"
                      with open(tmp_html, "w", encoding='utf-8') as f_h: f_h.write(html)
                      
                      subprocess.run([pdf_kit_path, tmp_html, dest_pdf], check=True)
                      if os.path.exists(dest_pdf):
                           return FileResponse(path=dest_pdf, filename=f"{uuid}.pdf")
                 except Exception as e_pdf:
                      print(f"Error generando PDF: {str(e_pdf)}")

            raise HTTPException(status_code=404, detail="Archivo PDF no encontrado en rutas de resguardo")"""

c = c.replace(
    """        if alt_comp and alt_comp.pdf_file_path and os.path.exists(alt_comp.pdf_file_path):
            actual_path = alt_comp.pdf_file_path
        else:
            raise HTTPException(status_code=404, detail="Archivo PDF no encontrado en rutas de resguardo")""",
    fallback_logic
)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "w", encoding="utf-8") as f:
    f.write(c)

print("Pre-rendering Applied")
