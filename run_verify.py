import sys
import os
import asyncio

# Agregar raíz al path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("[+] Iniciando ejecución del auditor...")
# Importar y correr el código de verify_all_criticals.py
with open(r"C:\Users\erobl\AppData\Local\Temp\verify_all_criticals.py", 'r', encoding='utf-8') as f:
    code = f.read()
    exec(code)
