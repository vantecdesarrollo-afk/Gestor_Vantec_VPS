with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\orquestador.py", "r", encoding="utf-8") as f:
    c = f.read()

old_fstring = """        html_content = f"<html><body>{payload.cuerpo.replace('\\\\n', '<br>')}</body></html>\""""

new_fstring = """        cuerpo_formateado = payload.cuerpo.replace('\\n', '<br>')
        html_content = f"<html><body>{cuerpo_formateado}</body></html>\""""

if old_fstring in c:
    c = c.replace(old_fstring, new_fstring)
else:
    # alternate approach just in case spacing
    c = c.replace("html_content = f\"<html><body>{payload.cuerpo.replace('\\\\n', '<br>')}</body></html>\"", "cuerpo_formateado = payload.cuerpo.replace('\\n', '<br>')\n        html_content = f\"<html><body>{cuerpo_formateado}</body></html>\"")

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\orquestador.py", "w", encoding="utf-8") as f:
    f.write(c)

print("Orquestador f-string backslash fixed.")
