import asyncio
import os
import sys

sys.path.insert(0, r"C:\Test_Antigravity\Gestor_CFDI_Vantec")

from src.database.session import AsyncSessionLocal
from src.database.models import Cfdi, EntidadSMTPConfig
from sqlalchemy import select

async def trigger_email():
    async with AsyncSessionLocal() as db:
        print("Buscando Factura 804...")
        # find cfdi 804
        result = await db.execute(select(Cfdi).where(Cfdi.folio == '804'))
        cfdi = result.scalar_one_or_none()
        
        if not cfdi:
            print("Factura 804 no encontrada en DB.")
            return

        print(f"Factura 804 encontrada: UUID {cfdi.uuid}")
        
        # Trigger same code logic from orquestador.py manually
        from src.services.cfdi_storage import find_cfdi_attachments
        att = find_cfdi_attachments(cfdi.uuid, getattr(cfdi, 'serie', ""), getattr(cfdi, 'folio', ""), getattr(cfdi, 'tipo_comprobante', "I"))
        xml_path = att["xml_path"] or cfdi.xml_file_path
        pdf_path = att["pdf_path"] or cfdi.pdf_file_path

        print(f"XML: {xml_path}")
        print(f"PDF: {pdf_path}")
        
        # load smtp
        smtp_res = await db.execute(select(EntidadSMTPConfig).where(EntidadSMTPConfig.entidad_id == cfdi.tenant_id))
        smtp_config = smtp_res.scalar_one_or_none()
        
        if not smtp_config:
            print("Configuración SMTP no encontrada.")
            return

        import subprocess
        script_path = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\microservices\mailer\mailVantec.py"
        
        destinatarios = "eroblesj@hotmail.com,eroblesj@gmail.com"
        # create temp html
        temp_html_path = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\microservices\mailer\temp_manual_804.html"
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write("<html><body>Prueba de Envío Factura 804 de dos correos con adjuntos.</body></html>")

        cmd = [
            "python", script_path,
            "-s", f"Prueba Factura 804 correos con adjuntos",
            "-f", smtp_config.from_address or smtp_config.username,
            "-t", destinatarios,
            "-u", smtp_config.username,
            "-y", smtp_config.password_encrypted,
            "-z", smtp_config.host,
            "-p", str(smtp_config.port),
            "-v"
        ]
        
        if smtp_config.security_type in ["STARTTLS", "TLS"]:
            cmd.append("-l")

        cmd.append(temp_html_path)
        cmd.append(xml_path)
        if pdf_path:
            cmd.append(pdf_path)

        print("Corriendo mailVantec RPA...")
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(process.stdout)
        print(process.stderr)

        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)

        if process.returncode == 0:
            print("✅ Correo enviado exitosamente.")
        else:
            print("❌ Error al enviar correo.")

if __name__ == "__main__":
    asyncio.run(trigger_email())
