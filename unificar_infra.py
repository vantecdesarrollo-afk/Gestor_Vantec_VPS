import os
import shutil

def estandarizar_infraestructura():
    base_dir = r"C:\Test_Antigravity\Gestor_CFDI_Vantec"
    license_legacy = r"C:\Vantec\Gestor_CFDI\license"
    license_nueva = os.path.join(base_dir, "license")
    
    carpetas_basura = ["failed", "logs_ingesta", "processing"]

    print("⚙️ Iniciando estandarización Vantec Core...")

    # 1. Migrar Licenciamiento
    if os.path.exists(license_legacy):
        shutil.copytree(license_legacy, license_nueva, dirs_exist_ok=True)
        print(f"✅ Licenciamiento unificado en: {license_nueva}")
    else:
        print("⚠️ Carpeta de licencia legacy no encontrada. Verifica la ruta.")

    # 2. Limpieza Quirúrgica
    for carpeta in carpetas_basura:
        ruta = os.path.join(base_dir, carpeta)
        if os.path.exists(ruta):
            shutil.rmtree(ruta)
            print(f"✅ Basura eliminada: {carpeta}")

    print("🚀 Infraestructura limpia y unificada.")

if __name__ == "__main__":
    estandarizar_infraestructura()