with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "r", encoding="utf-8") as f:
    c = f.read()

# 1. Update List Verificación with single Call
old_list_verify = """            if not xml_exists or not pdf_exists:
                 import glob
                 if not xml_exists:
                      xml_matches = glob.glob(f"storage/**/{r.uuid}.xml") or glob.glob(f"Operacion_CFDI/**/{r.uuid}.xml")
                      xml_exists = bool(xml_matches)
                 if not pdf_exists:
                      pdf_matches = glob.glob(f"storage/**/{r.uuid}.pdf") or glob.glob(f"Operacion_CFDI/**/{r.uuid}.pdf")
                      pdf_exists = bool(pdf_matches)
                      if not pdf_exists and xml_exists:
                           # Si existe el XML, el modulo fallback lo genera al descargar, de cara al frontend EXISTE.
                           pdf_exists = True"""

new_list_verify = """            if not pdf_exists or not xml_exists:
                 from src.services.cfdi_storage import find_cfdi_attachments
                 att = find_cfdi_attachments(str(r.uuid), getattr(r, 'serie', ""), getattr(r, 'folio', ""))
                 if not xml_exists and att["xml_path"]:
                      xml_exists = True
                 if not pdf_exists and att["pdf_path"]:
                      pdf_exists = True"""

c = c.replace(old_list_verify, new_list_verify)

# 2. Update get_comprobante_pdf with single Call
old_pdf_fallback = """    if not actual_path or not os.path.exists(actual_path):
        import glob
        search_paths = [f"storage/**/{uuid}.pdf", f"Operacion_CFDI/**/{uuid}.pdf", f"**/{uuid}.pdf"]
        for pattern in search_paths:
            matches = glob.glob(pattern, recursive=True)
            if matches:
                 actual_path = matches[0]
                 break"""

new_pdf_fallback = """    if not actual_path or not os.path.exists(actual_path):
        from src.services.cfdi_storage import find_cfdi_attachments
        att = find_cfdi_attachments(uuid, getattr(comp, 'serie', "") if comp else "", getattr(comp, 'folio', "") if comp else "")
        if att["pdf_path"]:
             actual_path = att["pdf_path"]"""

c = c.replace(old_pdf_fallback, new_pdf_fallback)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "w", encoding="utf-8") as f:
    f.write(c)

print("Comprobantes refactored applied")
