import os
import shutil

invalid_dir = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\Invalid"
upload_dir = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\Upload"

log = []
if not os.path.exists(upload_dir):
     os.makedirs(upload_dir)

files = os.listdir(invalid_dir)
log.append(f"Archivos encontrados en Invalid: {len(files)}")

for f in files:
     if f.lower().endswith(".xml"):
          src = os.path.join(invalid_dir, f)
          dest = os.path.join(upload_dir, f)
          try:
               shutil.move(src, dest)
               log.append(f"Movido: {f}")
          except Exception as e:
               log.append(f"Error moviendo {f}: {e}")
               
log.append("Proceso manual de movimiento terminado.")

with open("move_log.txt", "w", encoding="utf-8") as f_log:
     f_log.write("\n".join(log))
     print("Log guardado en move_log.txt")
