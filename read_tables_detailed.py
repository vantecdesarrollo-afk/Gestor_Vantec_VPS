import os

targets = ["comprobantes", "usuarios", "entidades_fiscales", "cfdi_relacionados", "usuario_entidad_acceso", "bitacora_auditoria"]

if os.path.exists("tables_out.txt"):
    try:
        content = open("tables_out.txt", "r", encoding="utf-16").read()
        lines = content.split("\n")
        with open("tables_detailed.txt", "w", encoding="utf-8") as f:
            current_table = None
            for line in lines:
                if "--- Table" in line:
                    table_name = line.split(" Table ")[1].split(" ---")[0].strip()
                    if table_name in targets:
                        current_table = table_name
                        f.write(line + "\n")
                    else:
                        current_table = None
                elif current_table and line.strip() and not line.startswith("2026-"):
                    f.write(line + "\n")
        print("Detailed summary written.")
    except Exception as e:
        print("Error:", e)
else:
    print("tables_out.txt does not exist")
