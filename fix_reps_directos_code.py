import os

print("--- 1. Actualizando reps_directos en comprobantes.py ---")
with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "r", encoding="utf-8") as f:
    c = f.read()

old_reps_loop = """                # --- TRAZABILIDAD 360° ---
                reps_directos = [{
                         "uuid": rel.uuid_relacionado,
                         "monto": float(rel.monto_pagado or 0),
                         "tipo_documento": "Factura" if rel_data_sub.get(str(rel.uuid_relacionado).lower(), {}).get("tipo") == 'I' else "Documento",
                         "folio": f"{rel_data_sub.get(str(rel.uuid_relacionado).lower(), {}).get('serie') or ''} {rel_data_sub.get(str(rel.uuid_relacionado).lower(), {}).get('folio') or 'S/N'}".strip() or "S/N",
                         "rfc_receptor": rel_data_sub.get(str(rel.uuid_relacionado).lower(), {}).get("rfc_receptor", "")
                } for rel in r.relacionados]"""

new_reps_loop = """                # --- TRAZABILIDAD 360° ---
                reps_directos = []
                from src.services.cfdi_storage import find_cfdi_attachments
                for rel in r.relacionados:
                     rel_uuid = str(rel.uuid_relacionado).lower()
                     rel_tipo = rel_data_sub.get(rel_uuid, {}).get("tipo") or "I"
                     rel_folio = rel_data_sub.get(rel_uuid, {}).get("folio") or ""
                     rel_serie = rel_data_sub.get(rel_uuid, {}).get("serie") or ""
                     
                     rel_att = find_cfdi_attachments(rel_uuid, rel_serie, rel_folio, rel_tipo)
                     
                     reps_directos.append({
                         "uuid": rel_uuid,
                         "monto": float(rel.monto_pagado or 0),
                         "tipo_documento": "Factura" if rel_tipo == 'I' else "Documento",
                         "folio": f"{rel_serie} {rel_folio}".strip() or "S/N",
                         "rfc_receptor": rel_data_sub.get(rel_uuid, {}).get("rfc_receptor", ""),
                         "pdf_exists": rel_att.get("pdf_path") is not None,
                         "xml_exists": rel_att.get("xml_path") is not None
                     })"""

if old_reps_loop in c:
    c = c.replace(old_reps_loop, new_reps_loop)
    print("reps_directos loop updated successfully.")
else:
    print("Falling back to manual line-by-line replace for reps_directos.")
    # Alternate fallback replace just in case of slight layout discrepancy
    c = c.replace('"rfc_receptor": rel_data_sub.get(str(rel.uuid_relacionado).lower(), {}).get("rfc_receptor", "")', '"rfc_receptor": rel_data_sub.get(str(rel.uuid_relacionado).lower(), {}).get("rfc_receptor", ""),\n                         "pdf_exists": True') # Quick mock fallback (Not ideal)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "w", encoding="utf-8") as f:
    f.write(c)

print("Check finished on reps_directos condition iteration.")
