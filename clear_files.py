import shutil
import os

paths = [
    r"c:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\Files",
    r"c:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\Invalid",
    r"c:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\Upload"
]

for p in paths:
    if os.path.exists(p):
        print(f"Clearing {p}...")
        for f in os.listdir(p):
            fp = os.path.join(p, f)
            try:
                if os.path.isfile(fp): os.remove(fp)
                elif os.path.isdir(fp): shutil.rmtree(fp)
            except Exception as e:
                print(f"Error deleting {fp}: {e}")
print("Finished clearing.")
