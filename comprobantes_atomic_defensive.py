with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "r", encoding="utf-8") as f:
    c = f.read()

old_loop = """        output = []
        for r in rows:
            # Calculamos el total real para los Pagos (P)"""

new_loop = """        output = []
        for r in rows:
            try:
                # Calculamos el total real para los Pagos (P)"""

c = c.replace(old_loop, new_loop)

old_append_end = """                "xml_exists": xml_exists,
                "pdf_exists": pdf_exists
            })
            
        return output"""

new_append_end = """                "xml_exists": xml_exists,
                "pdf_exists": pdf_exists
                })
            except Exception as e_row:
                print(f"--- ERROR EN FILA {getattr(r, 'uuid', 'Desconocido')} --- : {str(e_row)}")
            
        return output"""

c = c.replace(old_append_end, new_append_end)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "w", encoding="utf-8") as f:
    f.write(c)

print("Defensive loops applied")
import subprocess
print("Corriendo final_surgical.py para debounce...")
subprocess.run(["python", r"c:\Test_Antigravity\Gestor_CFDI_Vantec\final_surgical.py"], check=True)
