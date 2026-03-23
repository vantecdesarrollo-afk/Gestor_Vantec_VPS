with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\microservices\mailer\mailVantec.py", "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace('print(f"✅ Correo enviado con', 'print(f"Correo enviado con')
c = c.replace('print(f"❌ Error SMTP:', 'print(f"Error SMTP:')

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\microservices\mailer\mailVantec.py", "w", encoding="utf-8") as f:
    f.write(c)

print("Emojis removidos de mailVantec.py exitosamente.")
