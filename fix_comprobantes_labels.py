file_path = "src/api/endpoints/comprobantes.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update lines 41 for GET /
target_lookup = """        # SMART LOOKUP: Mapa de UUID a Folio para vinculados en memoria (O(1))
        uuid_to_folio = {str(comp.uuid).lower(): comp.folio for comp in comprobantes}"""

replacement_lookup = """        # SMART LOOKUP: Mapa de UUID a Folio para vinculados en memoria (O(1))
        uuid_to_folio = {str(comp.uuid).lower(): comp.folio for comp in comprobantes}
        uuid_to_tipo = {str(comp.uuid).lower(): comp.tipo_comprobante for comp in comprobantes}"""

# 2. Update reps_list in GET /
target_reps = """            # 1. Construir lista base
            reps_list = [
                {
                    "uuid": str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(c.uuid).lower() else r.uuid_relacionado),
                    "folio": uuid_to_folio.get(r.uuid_padre.lower() if str(r.uuid_relacionado).lower() == str(c.uuid).lower() else r.uuid_relacionado.lower(), "S/N"),
                    "monto": float(r.monto_pagado or 0),
                    "tipo": r.tipo_relacion
                } for r in c.relaciones if r.tipo_relacion == 'PAGO'
            ]"""

replacement_reps = """            # 1. Construir lista base
            reps_list = [
                {
                    "uuid": str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(c.uuid).lower() else r.uuid_relacionado),
                    "folio": uuid_to_folio.get(str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(c.uuid).lower() else r.uuid_relacionado).lower(), "S/N"),
                    "monto": float(r.monto_pagado or 0),
                    "tipo": r.tipo_relacion,
                    "tipo_documento": "Pago" if uuid_to_tipo.get(str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(c.uuid).lower() else r.uuid_relacionado).lower(), "I") == 'P' else "Factura"
                } for r in c.relaciones if r.tipo_relacion == 'PAGO'
            ]"""

# Update GET /
if target_lookup in content and target_reps in content:
    content = content.replace(target_lookup, replacement_lookup)
    content = content.replace(target_reps, replacement_reps)
    print("✅ GET / endpoint updated.")
else:
    # Try with CRLF
    target_lookup_crlf = target_lookup.replace('\n', '\r\n')
    replacement_lookup_crlf = replacement_lookup.replace('\n', '\r\n')
    target_reps_crlf = target_reps.replace('\n', '\r\n')
    replacement_reps_crlf = replacement_reps.replace('\n', '\r\n')
    if target_lookup_crlf in content and target_reps_crlf in content:
        content = content.replace(target_lookup_crlf, replacement_lookup_crlf)
        content = content.replace(target_reps_crlf, replacement_reps_crlf)
        print("✅ GET / endpoint updated (CRLF).")
    else:
        print("❌ Targets for GET / not found.")

# Save fixes
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
