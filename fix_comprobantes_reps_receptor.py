file_path = "src/api/endpoints/comprobantes.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Build uuid_to_receptor lookup above reps_list
target_lookup = """        # BULK QUERY: para tipo_comprobante de documentos vinculados (crucial para paginacion)
        linked_uuids = []"""

replacement_lookup = """        # SMART LOOKUP: Mapa de UUID a Receptor
        uuid_to_receptor = {str(comp.uuid).lower(): comp.rfc_receptor for comp in comprobantes}
        
        # BULK QUERY: para tipo_comprobante de documentos vinculados (crucial para paginacion)
        linked_uuids = []"""

# 2. Update reps_list to include rfc_receptor
target_reps = """            # 1. Construir lista base
            reps_list = [
                {
                    "uuid": str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(c.uuid).lower() else r.uuid_relacionado),
                    "folio": uuid_to_folio.get(str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(c.uuid).lower() else r.uuid_relacionado).lower(), "S/N"),
                    "monto": float(r.monto_pagado or 0),
                    "tipo": r.tipo_relacion,
                    "tipo_documento": "Pago" if uuid_to_tipo_bulk.get(str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(c.uuid).lower() else r.uuid_relacionado).lower(), "I") == 'P' else "Factura"
                } for r in c.relaciones if r.tipo_relacion == 'PAGO'
            ]"""

replacement_reps = """            # 1. Construir lista base
            reps_list = [
                {
                    "uuid": str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(c.uuid).lower() else r.uuid_relacionado),
                    "folio": uuid_to_folio.get(str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(c.uuid).lower() else r.uuid_relacionado).lower(), "S/N"),
                    "monto": float(r.monto_pagado or 0),
                    "tipo": r.tipo_relacion,
                    "tipo_documento": "Pago" if uuid_to_tipo_bulk.get(str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(c.uuid).lower() else r.uuid_relacionado).lower(), "I") == 'P' else "Factura",
                    "rfc_receptor": uuid_to_receptor.get(str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(c.uuid).lower() else r.uuid_relacionado).lower(), "")
                } for r in c.relaciones if r.tipo_relacion == 'PAGO'
            ]"""

if target_lookup in content and target_reps in content:
    content = content.replace(target_lookup, replacement_lookup)
    content = content.replace(target_reps, replacement_reps)
    print("✅ Backend reps_list updated with rfc_receptor.")
else:
    # Try with CRLF
    target_lookup_crlf = target_lookup.replace('\n', '\r\n')
    replacement_lookup_crlf = replacement_lookup.replace('\n', '\r\n')
    target_reps_crlf = target_reps.replace('\n', '\r\n')
    replacement_reps_crlf = replacement_reps.replace('\n', '\r\n')
    if target_lookup_crlf in content and target_reps_crlf in content:
        content = content.replace(target_lookup_crlf, replacement_lookup_crlf)
        content = content.replace(target_reps_crlf, replacement_reps_crlf)
        print("✅ Backend reps_list updated with rfc_receptor (CRLF).")
    else:
        print("❌ Targets for backend lookup not found.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
