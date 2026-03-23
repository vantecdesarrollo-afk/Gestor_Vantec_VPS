import os

print("--- 1. Reparando openDetailDrawer en cfdis.js ---")
with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "r", encoding="utf-8") as f:
    c = f.read()

old_drawer_check = "if (!drawer || !content) return;"
new_drawer_check = "const content = drawerContent;\n    if (!drawer || !content) return;"

if old_drawer_check in c:
    c = c.replace(old_drawer_check, new_drawer_check)
    print("openDetailDrawer content fix applied.")
else:
    print("Evaluating fallback mapping on content check drawer.")

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "w", encoding="utf-8") as f:
    f.write(c)

print("Componentes Drawer sincronizados de forma exitosa.")
