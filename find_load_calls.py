with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        if "loadCfdis" in line:
            print(f"FOUND in line {i}: {line.strip()}")
