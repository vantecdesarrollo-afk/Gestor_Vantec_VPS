with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "r", encoding="utf-8") as f:
    c = f.read()

# Fix XML falling back with recursive
c = c.replace(
    'search_paths = [f"storage/*/{uuid}.xml", f"Operacion_CFDI/Upload/*/{uuid}.xml", f"Operacion_CFDI/Upload/{uuid}.xml", f"storage/{uuid}.xml"]\n        for pattern in search_paths:\n            matches = glob.glob(pattern)',
    'search_paths = [f"storage/**/{uuid}.xml", f"Operacion_CFDI/**/{uuid}.xml", f"**/{uuid}.xml"]\n        for pattern in search_paths:\n            matches = glob.glob(pattern, recursive=True)'
)

# Fix PDF falling back with recursive
c = c.replace(
    'search_paths = [f"storage/*/{uuid}.pdf", f"Operacion_CFDI/Upload/*/{uuid}.pdf", f"Operacion_CFDI/Upload/{uuid}.pdf", f"storage/{uuid}.pdf"]\n        for pattern in search_paths:\n            matches = glob.glob(pattern)',
    'search_paths = [f"storage/**/{uuid}.pdf", f"Operacion_CFDI/**/{uuid}.pdf", f"**/{uuid}.pdf"]\n        for pattern in search_paths:\n            matches = glob.glob(pattern, recursive=True)'
)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "w", encoding="utf-8") as f:
    f.write(c)

print("Recursive fallback applied successfully")
