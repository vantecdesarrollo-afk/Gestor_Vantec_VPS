file_path = "src/api/endpoints/comprobantes.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """        from sqlalchemy import in_
        # uuid_to_tipo query"""

replacement = """        # uuid_to_tipo query"""

if target in content:
    content = content.replace(target, replacement)
    print("✅ Invalid import removed.")
else:
     target_crlf = target.replace('\n', '\r\n')
     if target_crlf in content:
         content = content.replace(target_crlf, replacement)
         print("✅ Invalid import removed (CRLF).")
     else:
         print("❌ Target for import not found.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
