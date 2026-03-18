file_path = "src/api/endpoints/comprobantes.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """        reps_list = [
            {
                "uuid": str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(comp.uuid).lower() else r.uuid_relacionado),
                "monto": float(r.monto_pagado or 0),
                "tipo": r.tipo_relacion
            } for r in comp.relaciones if r.tipo_relacion == 'PAGO'
        ]"""

replacement = """        # Determinar existencia de archivos para el Reenvio
        pdf_exists = False
        xml_exists = False
        if comp.ruta_resguardo:
             path_str = comp.ruta_resguardo
             dirname = path_str if os.path.isdir(path_str) else os.path.dirname(path_str)
             pdf_exists = len(glob.glob(os.path.join(dirname, f"*{uuid}*.pdf"))) > 0
             xml_exists = len(glob.glob(os.path.join(dirname, f"*{uuid}*.xml"))) > 0

        reps_list = [
            {
                "uuid": str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(comp.uuid).lower() else r.uuid_relacionado),
                "monto": float(r.monto_pagado or 0),
                "tipo": r.tipo_relacion
            } for r in comp.relaciones if r.tipo_relacion == 'PAGO'
        ]"""

if target in content:
    content = content.replace(target, replacement)
    print("✅ Existence check added.")
else:
    target_crlf = target.replace('\n', '\r\n')
    replacement_crlf = replacement.replace('\n', '\r\n')
    if target_crlf in content:
        content = content.replace(target_crlf, replacement_crlf)
        print("✅ Existence check added (CRLF).")
    else:
        print("❌ Target for reps_list not found.")

# Return them in payload structure
target_payload = """             "fecha_emision": comp.fecha_emision.isoformat() if comp.fecha_emision else None,
             "descripcion_concepto": descripcion,
             "reps_asociados": reps_list"""

replacement_payload = """             "fecha_emision": comp.fecha_emision.isoformat() if comp.fecha_emision else None,
             "descripcion_concepto": descripcion,
             "pdf_exists": pdf_exists,
             "xml_exists": xml_exists,
             "reps_asociados": reps_list"""

if target_payload in content:
    content = content.replace(target_payload, replacement_payload)
    print("✅ Payload updated.")
else:
    target_payload_crlf = target_payload.replace('\n', '\r\n')
    replacement_payload_crlf = replacement_payload.replace('\n', '\r\n')
    if target_payload_crlf in content:
        content = content.replace(target_payload_crlf, replacement_payload_crlf)
        print("✅ Payload updated (CRLF).")
    else:
         print("❌ Target for payload not found.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
