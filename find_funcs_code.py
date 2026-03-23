with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        if "downloadCfdi" in line and "function" in line:
            print(f"Line {i}: {line.strip()}")
        if "openDetailDrawer" in line and "function" in line:
            print(f"Line {i}: {line.strip()}")
