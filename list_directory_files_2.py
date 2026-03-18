import os
import glob

path = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\storage\tenants\e6f64bb0-3971-4cc8-b883-cd183eca77d7\2025\10"

with open("dir_output.txt", "w", encoding="utf-8") as f:
    f.write(f"\n--- CONTENIDO DIRECTORIO: {path} ---\n")
    if os.path.isdir(path):
        files = glob.glob(os.path.join(path, "*.xml"))
        for fl in files:
             f.write(f"{os.path.basename(fl)}\n")
    else:
        f.write("❌ Directorio no existe\n")
print("✅ Written to dir_output.txt")
