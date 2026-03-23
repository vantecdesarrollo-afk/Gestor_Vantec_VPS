import os
import subprocess
import xml.etree.ElementTree as ET

def generate_pdf_from_xml(xml_path: str, dest_pdf: str, uuid_val: str, logo_path: str = None) -> bool:
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        ns = {'cfdi': 'http://www.sat.gob.mx/cfd/4', 'cfdi33': 'http://www.sat.gob.mx/cfd/3'}
        
        emisor = None
        for el in root.iter():
             if el.tag.endswith('Emisor'):
                  emisor = el
                  break
        nombre_emisor = emisor.get('Nombre', '') if emisor is not None else "---"
        
        conceptos_nodes = root.findall('.//cfdi:Concepto', ns) or root.findall('.//cfdi33:Concepto', ns)
        concept_html = "".join([f"<tr><td style='padding:8px;'>{c.get('Descripcion')}</td><td style='text-align:center;'>{c.get('Cantidad')}</td><td style='text-align:right;'>{c.get('ValorUnitario')}</td><td style='text-align:right;'>{c.get('Importe')}</td></tr>" for c in conceptos_nodes])
        total_f = root.get('Total', '') or root.get('total', '')
        
        folio_f = root.get('Folio', '') or root.get('folio', '')
        serie_f = root.get('Serie', '') or root.get('serie', '')
        
        logo_html = ""
        if logo_path:
            abs_logo = os.path.abspath(logo_path.lstrip('/'))
            if os.path.exists(abs_logo):
                abs_logo_uri = "file:///" + abs_logo.replace('\\', '/')
                logo_html = f"<img src='{abs_logo_uri}' style='max-height: 80px; object-fit: contain; margin-bottom: 20px;' alt='Logo Entidad' />"
        
        html = f"""<html><body style='font-family: Inter, Arial, sans-serif; padding: 40px; color: #1E3A5F;'>
        <div style='display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:30px; border-bottom: 2px solid #eee; padding-bottom: 20px;'>
            <div>{logo_html}</div>
            <div style='text-align:right;'>
                <h1 style='margin:0; font-size: 24px; color: #1E3A5F;'>Comprobante CFDI</h1>
                <p style='margin:2px 0; font-size: 14px; font-weight: bold; color: #E11D48;'>Serie: {serie_f}   Folio: {folio_f}</p>
                <p style='margin:0; font-size: 11px; color: #666;'>UUID: {uuid_val}</p>
            </div>
        </div>
        <div style='margin-bottom: 30px; background-color: #f8fafc; padding: 20px; border-radius: 8px;'>
            <p style='margin:0 0 10px 0;'><b>Emisor:</b> {nombre_emisor}</p>
            <p style='margin:0 0 10px 0; font-size: 18px; color: #2FA4E7;'><b>Total:</b> ${total_f}</p>
        </div>
        <table border='0' width='100%' style='border-collapse: collapse; font-size: 14px;'>
          <tr style='background: #1E3A5F; color: white;'>
            <th style='padding: 12px; text-align:left;'>Descripción</th>
            <th style='padding: 12px; text-align:center;'>Cant</th>
            <th style='padding: 12px; text-align:right;'>Precio</th>
            <th style='padding: 12px; text-align:right;'>Importe</th>
          </tr>
          {concept_html}
        </table>
        <p style='font-size: 10px; color: gray; margin-top: 50px; text-align:center;'>Generado de emergencia Gestor Vantec</p>
        </body></html>"""
        
        cwd = os.getcwd()
        tmp_html = os.path.join(cwd, f"{uuid_val}.html")
        with open(tmp_html, "w", encoding='utf-8') as f_h: 
            f_h.write(html)
        
        edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        if not os.path.exists(edge_path):
             edge_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        
        # We must use file:/// uri for the tmp_html so edge understands it
        html_uri = "file:///" + tmp_html.replace('\\', '/')
        subprocess.run([edge_path, "--headless", "--disable-gpu", f"--print-to-pdf={dest_pdf}", "--no-pdf-header-footer", html_uri], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(tmp_html):
            os.remove(tmp_html)
            
        return os.path.exists(dest_pdf)
    except Exception as e:
        print("Error en generate_pdf_from_xml:", e)
        return False
