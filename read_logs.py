import os

log_dir = r"c:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\logs"

if os.path.exists(log_dir):
    for f in os.listdir(log_dir):
        if f.endswith("_error.log"):
            p = os.path.join(log_dir, f)
            try:
                content = open(p, "r", encoding="utf-8").read()
                print(f"--- File {f} ---")
                print(content)
                print("----------------")
            except Exception as e:
                print(f"Error reading {f}: {e}")
else:
    print(f"Directory {log_dir} does not exist.")
