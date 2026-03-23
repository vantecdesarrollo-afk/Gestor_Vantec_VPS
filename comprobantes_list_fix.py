with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Replace block 129-140 manually by indices where it matches exactly
start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "if not xml_exists or not pdf_exists:" in line and "import glob" in lines[i+1]:
         start_idx = i
         break

if start_idx != -1:
    # Find end of that if block
    for j in range(start_idx, start_idx+15):
         if "pdf_exists = True" in lines[j] and "Si existe el XML" in lines[j-1]:
              end_idx = j + 1
              break

if start_idx != -1 and end_idx != -1:
    print(f"Overwriting from line {start_idx+1} to {end_idx+1}...")
    
    replacement_lines = [
        "                if not xml_exists or not pdf_exists:\n",
        "                     from src.services.cfdi_storage import find_cfdi_attachments\n",
        "                     att = find_cfdi_attachments(str(r.uuid), r.serie or \"\", r.folio or \"\", r.tipo_comprobante or \"I\")\n",
        "                     if not xml_exists and att[\"xml_path\"]:\n",
        "                          xml_exists = True\n",
        "                     if not pdf_exists and att[\"pdf_path\"]:\n",
        "                          pdf_exists = True\n"
    ]
    
    new_lines = lines[:start_idx] + replacement_lines + lines[end_idx:]
    
    with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "w", encoding="utf-8") as f:
         f.write("".join(new_lines))
    print("List view verification fixed with Tipo filter.")
else:
    print("Failed to match old list verification content style.")
