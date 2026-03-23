import os

root_dir = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI"
found_pdfs = []

for root, dirs, files in os.walk(root_dir):
    for file in files:
         if file.lower().endswith(".pdf"):
              found_pdfs.append(os.path.join(root, file))

with open("/tmp/pdfs_found.txt", "w") as f:
    f.write(f"Found {len(found_pdfs)} PDFs\n\n")
    for p in found_pdfs[:20]: # show top 20
         f.write(f"{p}\n")

print(f"Sub-search done, found {len(found_pdfs)}")
