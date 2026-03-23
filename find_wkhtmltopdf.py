import os
import glob

print("--- Buscando wkhtmltopdf.exe ---")

candidates = [
    r"C:\Test_Antigravity\wkhtmltopdf\bin\wkhtmltopdf.exe",
    r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
    r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
    r"C:\wkhtmltopdf\bin\wkhtmltopdf.exe"
]

found = False
for c in candidates:
    if os.path.exists(c):
        print(f"✅ ¡ENCONTRADO!: {c}")
        found = True

if not found:
    print("No se encontró en rutas estáticas comunes. Buscando de forma iterativa en C:\\ ...")
    # limit search to avoid timeout
    for root_dir in [r"C:\Test_Antigravity", r"C:\Vcore", r"C:\ITC"]:
        if os.path.exists(root_dir):
            matches = glob.glob(f"{root_dir}\\**\\wkhtmltopdf.exe", recursive=True)
            if matches:
                 print(f"✅ ¡ENCONTRADO ITERATIVO!: {matches[0]}")
                 found = True

if not found:
    print("❌ wkhtmltopdf.exe no encontrado en el sistema.")
