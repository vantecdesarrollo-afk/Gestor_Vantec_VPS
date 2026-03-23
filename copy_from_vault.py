import os
import shutil

src_dir = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\Files"
dest_dir = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\Upload"

if not os.path.exists(dest_dir):
     os.makedirs(dest_dir)

count = 0
for root, dirs, files in os.walk(src_dir):
     for f in files:
          if f.lower().endswith(".xml"):
               src = os.path.join(root, f)
               dest = os.path.join(dest_dir, f)
               try:
                    shutil.copy2(src, dest)
                    count += 1
               except Exception as e:
                    print(f"Error copiando {f}: {e}")
                    
print(f"✅ Copiados {count} archivos de la bóveda a Upload.")
print("Proceso manual de copia terminado.")
