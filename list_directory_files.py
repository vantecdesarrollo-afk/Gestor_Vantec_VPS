import os
import glob

path = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\storage\tenants\e6f64bb0-3971-4cc8-b883-cd183eca77d7\2025\10"

print(f"\n--- CONTENIDO DIRECTORIO: {path} ---")
if os.path.isdir(path):
    files = glob.glob(os.path.join(path, "*.xml"))
    for f in files:
         print(os.path.basename(f))
else:
    print("❌ Directorio no existe")
print("--- END ---")
