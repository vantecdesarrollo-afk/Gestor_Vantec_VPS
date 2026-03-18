file_path = "src/api/endpoints/comprobantes.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target_json = """        return {
             "id": str(comp.uuid),
             "uuid": str(comp.uuid),
             "serie": comp.serie,"""

replacement_json = """        return {
             "id": str(comp.uuid),
             "uuid": str(comp.uuid),
             "debug_tipo": str(comp.tipo_comprobante),
             "debug_total_monto_pago": total_monto_pago,
             "debug_reps_list_count": len(reps_list),
             "serie": comp.serie,"""

if target_json in content:
    content = content.replace(target_json, replacement_json)
    print("✅ Debug flags injected into return payload.")
else:
    target_crlf = target_json.replace('\n', '\r\n')
    replacement_crlf = replacement_json.replace('\n', '\r\n')
    if target_crlf in content:
        content = content.replace(target_crlf, replacement_json.replace('\n', '\r\n'))
        print("✅ Debug flags injected into return payload (CRLF).")
    else:
        print("❌ Target not found.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
