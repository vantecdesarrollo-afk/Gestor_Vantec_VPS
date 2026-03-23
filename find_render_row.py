with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        if "pdf_exists" in line or "descargarPdf" in line or "Action buttons" in line:
            print(f"FOUND Line {i}: {line.strip()}")
