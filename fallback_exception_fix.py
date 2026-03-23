with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "r", encoding="utf-8") as f:
    c = f.read()

# exact match with tabs/spaces
c = c.replace(
    """                 except Exception as e_pdf:
                      raise HTTPException(status_code=500, detail=f"Fallo en generación automática de PDF: {str(e_pdf)}")""",
    """                 except Exception as e_pdf:
                      if "WinError 2" in str(e_pdf):
                           raise HTTPException(status_code=500, detail="El PDF no existe en disco y wkhtmltopdf no está instalado en el servidor para generarlo.")
                      raise HTTPException(status_code=500, detail=f"Fallo en generación automática de PDF: {str(e_pdf)}")"""
)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "w", encoding="utf-8") as f:
    f.write(c)

print("Exceptions strings updated")
