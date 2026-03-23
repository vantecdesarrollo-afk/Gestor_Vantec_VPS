import subprocess
import glob
import os

print("--- Iniciando Envío Directo Alternativo Factura 804 ---")

folio = "804"
xml_candidates = glob.glob(f"C:\\ITC\\Fappeal\\Planeta\\Outfile\\SAT\\Factura\\**\\{folio}.xml", recursive=True)
pdf_candidates = glob.glob(f"C:\\ITC\\Fappeal\\Planeta\\Outfile\\SAT\\Factura\\**\\{folio}.pdf", recursive=True)

xml_path = xml_candidates[0] if xml_candidates else None
pdf_path = pdf_candidates[0] if pdf_candidates else None

print(f"XML Encontrado Directo: {xml_path}")
print(f"PDF Encontrado Directo: {pdf_path}")

# Si no hay, buscar en storage
if not xml_path:
    xml_candidates = glob.glob(f"C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\storage\\**\\*804*.xml", recursive=True)
    pdf_candidates = glob.glob(f"C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\storage\\**\\*804*.pdf", recursive=True)
    xml_path = xml_candidates[0] if xml_candidates else None
    pdf_path = pdf_candidates[0] if pdf_candidates else None
    print(f"XML Encontrado Alternativo: {xml_path}")
    print(f"PDF Encontrado Alternativo: {pdf_path}")

if not xml_path:
    print("❌ No se encontró XML para la factura 804 en rutas históricas.")
    import sys
    sys.exit(1)

# Usando Credenciales Explicitas de Paso 663
# cfdi.fromc=facturacion@planeta.com.mx
# cfdi.smpt=smtp.office365.com
# cfdi.port=587
# cfdi.userc=ugxs63@psoplaneta.com
# cfdi.passc=ViYrPPeq
# cfdi.ssl=-l

script_path = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\microservices\mailer\mailVantec.py"
destinatarios = "eroblesj@hotmail.com,eroblesj@gmail.com"

temp_html_path = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\microservices\mailer\temp_manual_804.html"
with open(temp_html_path, "w", encoding="utf-8") as f:
    f.write("<html><body>Prueba de Envío Directo Factura 804 de dos correos con adjuntos. Sin DB lookups.</body></html>")

cmd = [
    "python", script_path,
    "-s", f"Prueba Directa Factura 804 correos con adjuntos",
    "-f", "facturacion@planeta.com.mx",
    "-t", destinatarios,
    "-u", "ugxs63@psoplaneta.com",
    "-y", "ViYrPPeq",
    "-z", "smtp.office365.com",
    "-p", "587",
    "-v",
    "-l" # TLS enable explicit
]

cmd.append(temp_html_path)
cmd.append(xml_path)
if pdf_path:
    cmd.append(pdf_path)

print("Corriendo mailVantec RPA Directo...")
process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print("--- STDOUT ---")
print(process.stdout)
print("--- STDERR ---")
print(process.stderr)

if os.path.exists(temp_html_path):
    os.remove(temp_html_path)

if process.returncode == 0:
    print("✅ Correo enviado exitosamente Directo.")
else:
    print("❌ Error al enviar correo Directo.")
