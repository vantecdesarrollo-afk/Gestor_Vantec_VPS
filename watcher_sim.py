import shutil
import os
import subprocess
import time

def main():
    src_dir = r"C:\ITC\Fappeal\Planeta\Outfile\SAT\Factura\0-2K"
    upload_dir = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\Upload"
    
    os.makedirs(upload_dir, exist_ok=True)
    
    files_to_copy = ["819.xml", "819.pdf"]
    
    print("Copiando archivos a Upload...")
    for f in files_to_copy:
         src = os.path.join(src_dir, f)
         dest = os.path.join(upload_dir, f)
         if os.path.exists(src):
              shutil.copy(src, dest)
              print(f"Copiado: {f}")
         else:
              print(f"No encontrado en origen: {src}")

    # Ejecutar watcher temporalmente para procesar
    print("Ejecutando watcher.py para absorber archivos...")
    try:
         process = subprocess.Popen(["python", "watcher.py"], cwd=r"C:\Test_Antigravity\Gestor_CFDI_Vantec")
         time.sleep(10) # wait 10 seconds for absorption
         process.terminate()
         print("Watcher apagado tras absorción")
    except Exception as e:
         print(f"Error ejecutando watcher: {str(e)}")

if __name__ == "__main__":
    main()
