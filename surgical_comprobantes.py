with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "r", encoding="utf-8") as f:
    c = f.read()

# Fix Direct Mapping None format bug
c = c.replace(
    "f\"{rel_data_sub.get(str(rel.uuid_relacionado).lower(), {}).get('serie', '')} {rel_data_sub.get(str(rel.uuid_relacionado).lower(), {}).get('folio', 'S/N')}\"",
    "f\"{rel_data_sub.get(str(rel.uuid_relacionado).lower(), {}).get('serie') or ''} {rel_data_sub.get(str(rel.uuid_relacionado).lower(), {}).get('folio') or 'S/N'}\""
)

# Fix Detail fallback crash on 'Cfdi'
c = c.replace('"serie": alt_comp.serie or ""', '"serie": getattr(alt_comp, "serie", "")')
c = c.replace('"folio": alt_comp.folio or ""', '"folio": getattr(alt_comp, "folio", "")')
c = c.replace('"tipo_comprobante": alt_comp.tipo_comprobante or "I"', '"tipo_comprobante": getattr(alt_comp, "tipo_comprobante", "I")')
c = c.replace('"metodo_pago": alt_comp.metodo_pago or "---"', '"metodo_pago": getattr(alt_comp, "metodo_pago", "---")')
c = c.replace('"forma_pago": alt_comp.forma_pago or "---"', '"forma_pago": getattr(alt_comp, "forma_pago", "---")')

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "w", encoding="utf-8") as f:
    f.write(c)

print("Surgical updates applied successfully")
