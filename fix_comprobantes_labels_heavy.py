file_path = "src/api/endpoints/comprobantes.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """        # SMART LOOKUP: Mapa de UUID a Folio para vinculados en memoria (O(1))
        uuid_to_folio = {str(comp.uuid).lower(): comp.folio for comp in comprobantes}
        uuid_to_tipo = {str(comp.uuid).lower(): comp.tipo_comprobante for comp in comprobantes}"""

replacement = """        # SMART LOOKUP: Mapa de UUID a Folio para vinculados en memoria (O(1))
        uuid_to_folio = {str(comp.uuid).lower(): comp.folio for comp in comprobantes}
        
        # BULK QUERY: para tipo_comprobante de documentos vinculados (crucial para paginacion)
        linked_uuids = []
        for c in comprobantes:
            for r in c.relaciones:
                l_u = r.uuid_padre if str(r.uuid_relacionado).lower() == str(c.uuid).lower() else r.uuid_relacionado
                linked_uuids.append(l_u)
        
        from sqlalchemy import in_
        # uuid_to_tipo query
        if linked_uuids:
             q_types = select(Comprobante.uuid, Comprobante.tipo_comprobante).where(Comprobante.uuid.in_(linked_uuids))
             res_types = await db.execute(q_types)
             uuid_to_tipo_bulk = {str(u).lower(): t for u, t in res_types}
        else:
             uuid_to_tipo_bulk = {}"""

# Update also the list comprehension inside GET / mapping to use uuid_to_tipo_bulk
target_reps = """            # 1. Construir lista base
            reps_list = [
                {
                    "uuid": str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(c.uuid).lower() else r.uuid_relacionado),
                    "folio": uuid_to_folio.get(str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(c.uuid).lower() else r.uuid_relacionado).lower(), "S/N"),
                    "monto": float(r.monto_pagado or 0),
                    "tipo": r.tipo_relacion,
                    "tipo_documento": "Pago" if uuid_to_tipo.get(str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(c.uuid).lower() else r.uuid_relacionado).lower(), "I") == 'P' else "Factura"
                } for r in c.relaciones if r.tipo_relacion == 'PAGO'
            ]"""

replacement_reps = """            # 1. Construir lista base
            reps_list = [
                {
                    "uuid": str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(c.uuid).lower() else r.uuid_relacionado),
                    "folio": uuid_to_folio.get(str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(c.uuid).lower() else r.uuid_relacionado).lower(), "S/N"),
                    "monto": float(r.monto_pagado or 0),
                    "tipo": r.tipo_relacion,
                    "tipo_documento": "Pago" if uuid_to_tipo_bulk.get(str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(c.uuid).lower() else r.uuid_relacionado).lower(), "I") == 'P' else "Factura"
                } for r in c.relaciones if r.tipo_relacion == 'PAGO'
            ]"""

if target_lookup := target in content and target_reps in content:
     content = content.replace(target, replacement)
     content = content.replace(target_reps, replacement_reps)
     print("✅ Bulk query implementation patched.")
else:
     # Try with CRLF
     target_crlf = target.replace('\n', '\r\n')
     replacement_crlf = replacement.replace('\n', '\r\n')
     target_reps_crlf = target_reps.replace('\n', '\r\n')
     replacement_reps_crlf = replacement_reps.replace('\n', '\r\n')
     if target_crlf in content and target_reps_crlf in content:
         content = content.replace(target_crlf, replacement_crlf)
         content = content.replace(target_reps_crlf, replacement_reps_crlf)
         print("✅ Bulk query implementation patched (CRLF).")
     else:
         print("❌ Target not found.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
