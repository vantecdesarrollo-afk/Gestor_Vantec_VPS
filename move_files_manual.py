import os
import shutil

invalid_dir = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\Invalid"
upload_dir = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\Upload"

if not os.path.exists(upload_dir):
     os.makedirs(upload_dir)

files = os.listdir(invalid_dir)
print(f"Archivos encontrados en Invalid: {len(files)}")

for f in files:
     if f.lower().endswith(".xml"):
          src = os.path.join(invalid_dir, f)
          dest = os.path.join(upload_dir, f)
          try:
               shutil.move(src, dest)
               print(f"Movido: {f}")
          except Exception as e:
               print(f"Error moviendo {f}: {e}")
               
print("Proceso manual de movimiento terminado.")
