with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\services\parser\cfdi_parser.py", "r", encoding="utf-8") as f:
     lines = f.readlines()
     for i, line in enumerate(lines):
          if "Cfdi(" in line:
               print(f"Línea {i+1}: {line.strip()}")
          elif "Cfdi" in line:
               print(f"Línea {i+1}: {line.strip()}")
