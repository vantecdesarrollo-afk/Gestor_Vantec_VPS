import os

filepath = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py"
content = open(filepath, "r", encoding="utf-8").read()

# Replace exception string
content = content.replace(
    'raise HTTPException(status_code=404, detail="Archivo PDF no encontrado en repositorio")',
    'raise HTTPException(status_code=404, detail=f"Archivo PDF no encontrado en disco: {os.path.abspath(dirname)}")'
)

# Apply abspath verification wrapper
content = content.replace(
    'return FileResponse(path=files[0], filename=f"{uuid}.pdf")',
    'ruta_fisica = os.path.abspath(files[0])\n        if os.path.exists(ruta_fisica):\n            return FileResponse(path=ruta_fisica, filename=f"{uuid}.pdf")'
)

# Apply abspath standard serving wrapper
content = content.replace(
    'return FileResponse(path=path_str, filename=f"{uuid}.pdf")',
    'ruta_fisica_direct = os.path.abspath(path_str)\n         if os.path.exists(ruta_fisica_direct):\n              return FileResponse(path=ruta_fisica_direct, filename=f"{uuid}.pdf")'
)

open(filepath, "w", encoding="utf-8").write(content)
print("Hotfix applied!")
