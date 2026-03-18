file_path = "src/api/endpoints/comprobantes.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """        # Calibrar Total: Sumar montos vinculados si es tipo 'P' (Pago)
        total_monto_pago = sum(r["monto"] for r in reps_list)
        resolved_total = total_monto_pago if comp.tipo_comprobante and comp.tipo_comprobante.strip().upper() == 'P' and total_monto_pago > 0 else float(comp.total or 0)"""

replacement = """        # Calibrar Total: Sumar montos vinculados si es tipo 'P' (Pago)
        total_monto_pago = sum(r["monto"] for r in reps_list)
        is_rep_computed = len(reps_list) > 0
        resolved_total = total_monto_pago if is_rep_computed and total_monto_pago > 0 else float(comp.total or 0)"""

if target in content:
    content = content.replace(target, replacement)
    print("✅ Resolved total made infallible.")
else:
    target_crlf = target.replace('\n', '\r\n')
    replacement_crlf = replacement.replace('\n', '\r\n')
    if target_crlf in content:
         content = content.replace(target_crlf, replacement_crlf)
         print("✅ Resolved total made infallible (CRLF).")
    else:
         # Try with double spaces if formatting shifted
         print("❌ Target not found in comprobantes.py")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
