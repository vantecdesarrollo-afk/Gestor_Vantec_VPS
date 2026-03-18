file_path = "src/api/endpoints/comprobantes.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """    if os.path.isfile(path_str) and path_str.lower().endswith('.pdf') and os.path.exists(path_str):
         ruta_fisica_direct = os.path.abspath(path_str)
         if os.path.exists(ruta_fisica_direct):
              return FileResponse(path=ruta_fisica_direct, filename=f"{uuid}.pdf")"""

replacement = """    if os.path.isfile(path_str) and path_str.lower().endswith('.pdf') and os.path.exists(path_str):
         if uuid.lower() in os.path.basename(path_str).lower():
              ruta_fisica_direct = os.path.abspath(path_str)
              return FileResponse(path=ruta_fisica_direct, filename=f"{uuid}.pdf")"""

if target in content:
    content = content.replace(target, replacement)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ PDF fallback fixed.")
else:
    # Try with \r\n
    target_crlf = target.replace('\n', '\r\n')
    replacement_crlf = replacement.replace('\n', '\r\n')
    if target_crlf in content:
         content = content.replace(target_crlf, replacement_crlf)
         with open(file_path, 'w', encoding='utf-8') as f:
             f.write(content)
         print("✅ PDF fallback fixed (CRLF).")
    else:
         print("❌ Target for PDF fallback not found.")
