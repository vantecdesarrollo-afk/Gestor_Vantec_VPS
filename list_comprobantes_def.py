with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        if "@router" in line or "def " in line:
            print(f"Line {i}: {line.strip()}")
