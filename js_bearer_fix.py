with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "r", encoding="utf-8") as f:
    c = f.read()

# exact match with tabs/spaces
c = c.replace(
    """headers: { 'Content-Type': 'application/json', 'Authorization': Bearer  },""",
    """headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },"""
)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "w", encoding="utf-8") as f:
    f.write(c)

print("JS Bearer Fix Applied")
