with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Remove duplicated block between line 298 and 305
new_lines = lines[:298] + lines[306:]

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "w", encoding="utf-8") as f:
    f.write("".join(new_lines))

print("Duplicate syntax error fixed")
