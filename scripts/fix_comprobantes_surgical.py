path = r'c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# lines is 0-indexed.
# Line 204 is lines[203], which should be: "                if not xml_exists or not pdf_exists:\n"
# We need to insert the chunk after line 209 (lines[208])

target_index = 203
print("TARGET LINE:", lines[target_index])

insertion = """                     if not xml_exists or not pdf_exists:
                          f_att = async_fallback_map.get(uuid_lower, {})
                          if not xml_exists and f_att.get("xml_path") and os.path.exists(f_att["xml_path"]): xml_exists = True
                          if not pdf_exists and f_att.get("pdf_path") and os.path.exists(f_att["pdf_path"]): pdf_exists = True
"""

# Replace exact lines from 204 to 209 if matching
if "if not xml_exists or not pdf_exists:" in lines[203]:
    lines.insert(209, insertion)
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("SUCCESS")
else:
    print("MISMATCH")
