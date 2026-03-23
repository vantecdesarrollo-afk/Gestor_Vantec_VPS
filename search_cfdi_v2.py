with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\services\parser\cfdi_parser.py", "r", encoding="utf-8") as f:
     lines = f.readlines()
     res = []
     for i, line in enumerate(lines):
          if "Cfdi" in line:
               res.append(f"Línea {i+1}: {line.strip()}")
               
with open("search_output.txt", "w", encoding="utf-8") as f:
     f.write("\n".join(res))
     print("Resultados guardados.")
