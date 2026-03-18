file_path = "src/api/endpoints/comprobantes.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target_debug = """        return {
             "id": str(comp.uuid),
             "uuid": str(comp.uuid),
             "debug_tipo": str(comp.tipo_comprobante),
             "debug_total_monto_pago": total_monto_pago,
             "debug_reps_list_count": len(reps_list),
             "serie": comp.serie,"""

replacement_clean = """        return {
             "id": str(comp.uuid),
             "uuid": str(comp.uuid),
             "serie": comp.serie,"""

if target_debug in content:
    content = content.replace(target_debug, replacement_clean)
    print("✅ Debug tags removed.")
else:
    target_debug_crlf = target_debug.replace('\n', '\r\n')
    replacement_clean_crlf = replacement_clean.replace('\n', '\r\n')
    if target_debug_crlf in content:
        content = content.replace(target_debug_crlf, replacement_clean_crlf)
        print("✅ Debug tags removed (CRLF).")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
