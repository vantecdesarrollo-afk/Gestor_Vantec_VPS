import os

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\services\cfdi_storage.py", "r", encoding="utf-8") as f:
    orig = f.read()

# 1. Update find_cfdi_attachments to accept tipo
old_def = """def find_cfdi_attachments(uuid: str, serie: str = "", folio: str = "") -> dict:"""

new_def = """def find_cfdi_attachments(uuid: str, serie: str = "", folio: str = "", tipo: str = "") -> dict:"""

orig = orig.replace(old_def, new_def)

old_candidates = """    pdf_candidates = [
         f"C:\\\\Test_Antigravity\\\\Gestor_CFDI_Vantec\\\\storage\\\\**\\\\{uuid}.pdf",
         f"C:\\\\Test_Antigravity\\\\Gestor_CFDI_Vantec\\\\Operacion_CFDI\\\\**\\\\{uuid}.pdf",
         f"C:\\\\ITC\\\\Fappeal\\\\Planeta\\\\Outfile\\\\SAT\\\\Factura\\\\**\\\\{folio}.pdf",
         f"C:\\\\ITC\\\\Fappeal\\\\Planeta\\\\Outfile\\\\SAT\\\\Factura\\\\**\\\\{clean_folio}.pdf"
    ]"""

new_candidates = """    pdf_candidates = [
         f"C:\\\\Test_Antigravity\\\\Gestor_CFDI_Vantec\\\\storage\\\\**\\\\{uuid}.pdf",
         f"C:\\\\Test_Antigravity\\\\Gestor_CFDI_Vantec\\\\Operacion_CFDI\\\\**\\\\{uuid}.pdf"
    ]
    
    # Solo incluir historicos si es Tipo Ingreso (I), para Pagos (P) no colisionar folio
    if tipo == 'I':
         pdf_candidates.append(f"C:\\\\ITC\\\\Fappeal\\\\Planeta\\\\Outfile\\\\SAT\\\\Factura\\\\**\\\\{folio}.pdf")
         pdf_candidates.append(f"C:\\\\ITC\\\\Fappeal\\\\Planeta\\\\Outfile\\\\SAT\\\\Factura\\\\**\\\\{clean_folio}.pdf")"""

orig = orig.replace(old_candidates, new_candidates)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\services\cfdi_storage.py", "w", encoding="utf-8") as f:
    f.write(orig)

print("Helper file updated with Tipo filter.")


# 2. Update Calls in comprobantes.py to include 'tipo'
with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "r", encoding="utf-8") as f:
    c = f.read()

old_call_list = """                 from src.services.cfdi_storage import find_cfdi_attachments
                 att = find_cfdi_attachments(str(r.uuid), getattr(r, 'serie', ""), getattr(r, 'folio', ""))"""

new_call_list = """                 from src.services.cfdi_storage import find_cfdi_attachments
                 att = find_cfdi_attachments(str(r.uuid), getattr(r, 'serie', ""), getattr(r, 'folio', ""), getattr(r, 'tipo_comprobante', "I"))"""

c = c.replace(old_call_list, new_call_list)

old_call_pdf = """        from src.services.cfdi_storage import find_cfdi_attachments
        att = find_cfdi_attachments(uuid, getattr(comp, 'serie', "") if comp else "", getattr(comp, 'folio', "") if comp else "")"""

new_call_pdf = """        from src.services.cfdi_storage import find_cfdi_attachments
        att = find_cfdi_attachments(uuid, getattr(comp, 'serie', "") if comp else "", getattr(comp, 'folio', "") if comp else "", getattr(comp, 'tipo_comprobante', "I") if comp else "I")"""

c = c.replace(old_call_pdf, new_call_pdf)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "w", encoding="utf-8") as f:
    f.write(c)


# 3. Update Calls in orquestador.py to include 'tipo'
with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\orquestador.py", "r", encoding="utf-8") as f:
    o = f.read()

old_call_orq = """        from src.services.cfdi_storage import find_cfdi_attachments
        att = find_cfdi_attachments(cfdi.uuid, getattr(cfdi, 'serie', ""), getattr(cfdi, 'folio', ""))"""

new_call_orq = """        from src.services.cfdi_storage import find_cfdi_attachments
        att = find_cfdi_attachments(cfdi.uuid, getattr(cfdi, 'serie', ""), getattr(cfdi, 'folio', ""), getattr(cfdi, 'tipo_comprobante', "I"))"""

o = o.replace(old_call_orq, new_call_orq)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\orquestador.py", "w", encoding="utf-8") as f:
    o.write(o)

print("All endpoints calls updated passing tipo filter")
