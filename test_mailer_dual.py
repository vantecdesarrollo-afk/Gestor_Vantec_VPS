import subprocess
import os

def main():
    script = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\microservices\mailer\mailVantec.py"
    xml_path = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\Files\VCO1307234VA\2026\01\24A75E3B-261F-455A-9D04-B30BE95865BD.xml"
    
    # 1. Crear HTML temporal
    tmp_html = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\temp_body_dual_test.html"
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write("<html><body><h3>Prueba de envío de dos correos</h3><p>Mensaje de Diagnóstico de VCore Gestor CFDI.</p></body></html>")
        
    cmd = [
        "python", script,
        "-s", "Prueba de dos correos",
        "-f", "facturacion@planeta.com.mx",
        "-t", "eroblesj@hotmail.com, eroblesj@gmail.com",
        "-u", "ugxs63@psoplaneta.com",
        "-y", "ViYrPPeq",
        "-z", "smtp.office365.com",
        "-p", "587",
        "-v",
        tmp_html,
        xml_path
    ]
    
    print("Ejecutando MailVantec Dual Test...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(f"RETURN CODE: {res.returncode}")
    print(f"STDOUT: {res.stdout}")
    print(f"STDERR: {res.stderr}")

if __name__ == "__main__":
    main()
