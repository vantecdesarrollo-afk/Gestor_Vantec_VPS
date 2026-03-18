import os

env_path = r"c:\Test_Antigravity\Gestor_CFDI_Vantec\.env"
tenant_id = None

with open("tenants_list_custom.txt") as f:
    for line in f:
        if "Vantec Consultores" in line or "550e8400" in line:
            # ID: 550e8400-e29b-41d4-a...
            tenant_id = line.split('|')[0].replace('ID: ', '').strip()
            break

if not tenant_id:
    # Hardcode based on my best guess from output or use first line
    with open("tenants_list_custom.txt") as f:
        first_line = f.readline()
        if "ID: " in first_line:
             tenant_id = first_line.split('|')[0].replace('ID: ', '').strip()

if tenant_id:
    # Append to .env
    with open(env_path, "a") as f:
         f.write(f"\nWATCHER_ZONES='{{\"C:\\\\Test_Antigravity\\\\Gestor_CFDI_Vantec\\\\Operacion_CFDI\\\\Upload\": \"{tenant_id}\"}}'\n")
    print(f"Updated .env with tenant_id: {tenant_id}")
else:
    print("Could not find tenant_id")
