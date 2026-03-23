with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "r", encoding="utf-8") as f:
    c = f.read()

old_fallback = """                     # Idempotencia y Resiliencia (Libro 1): Si existe XML, la API genera el PDF On-the-Fly de emergencia
                     if not pdf_exists and xml_exists:
                          pdf_exists = True"""

if old_fallback in c:
    c = c.replace(old_fallback, "")
    print("Forzado artificial de pdf_exists = True removido exitosamente de comprobantes.py")
else:
    print("No se encontró el bloque de forzado artificial en comprobantes.py")

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "w", encoding="utf-8") as f:
    f.write(c)


with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\services\cfdi_storage.py", "r", encoding="utf-8") as f:
    s = f.read()

# Remover el parche de 'if tipo == I' y hacer una búsqueda estricta por folders para evitar colisiones
old_filter_block = """    # Solo incluir historicos si es Tipo Ingreso (I), para Pagos (P) no colisionar folio
    if tipo == 'I':
         pdf_candidates.append(f"C:\\\\ITC\\\\Fappeal\\\\Planeta\\\\Outfile\\\\SAT\\\\Factura\\\\**\\\\{folio}.pdf")
         pdf_candidates.append(f"C:\\\\ITC\\\\Fappeal\\\\Planeta\\\\Outfile\\\\SAT\\\\Factura\\\\**\\\\{clean_folio}.pdf")"""

if old_filter_block in s:
    # Solution without Patch: Remove collision wildcard ** recursive y usar subcarpetas explicitas
    new_candidates_logic = """    # Evitar búsqueda recursiva profunda (**) para no colisionar folios de años anteriores.
    # El archivo debe estar en la carpeta raíz del Outfile o subcarpeta bucket directa (ej. 0-2K).
    pdf_candidates.append(f"C:\\\\ITC\\\\Fappeal\\\\Planeta\\\\Outfile\\\\SAT\\\\Factura\\\\**\\\\{folio}.pdf")
    pdf_candidates.append(f"C:\\\\ITC\\\\Fappeal\\\\Planeta\\\\Outfile\\\\SAT\\\\Factura\\\\**\\\\{clean_folio}.pdf")"""
    
    # Wait, if recursive is necessary, how to isolate without type?
    # Actually, look at screenshot: it is sitting inside Bucket 0-2K specifically. 
    # To fix collision without tipo exception: We can enforce that the PDF MUST sit adjacent to the XML path found!
    
    # Let's read s.replace to remove the old_filter_block first.
    s = s.replace(old_filter_block, "")

    # Add candidate lookup that enforces adjacent to xml_path found
    # We will just append the candidate normally but without recursive wildcard on historicals IF we can use UUID first.
    pass

# Direct overwrite find_cfdi_attachments to strictly prevent cross-folder wildcard collision
new_find_def = """def find_cfdi_attachments(uuid: str, serie: str = "", folio: str = "", tipo: str = "") -> dict:
    import glob
    import os
    xml_path = None
    pdf_path = None
    
    clean_folio = str(folio).lstrip('0') if folio else ""
    
    # 1. Workspace UUID matching (100% atomic)
    xml_candidates = [
         f"C:\\\\Test_Antigravity\\\\Gestor_CFDI_Vantec\\\\storage\\\\**\\\\{uuid}.xml",
         f"C:\\\\Test_Antigravity\\\\Gestor_CFDI_Vantec\\\\Operacion_CFDI\\\\**\\\\{uuid}.xml"
    ]
    pdf_candidates = [
         f"C:\\\\Test_Antigravity\\\\Gestor_CFDI_Vantec\\\\storage\\\\**\\\\{uuid}.pdf",
         f"C:\\\\Test_Antigravity\\\\Gestor_CFDI_Vantec\\\\Operacion_CFDI\\\\**\\\\{uuid}.pdf"
    ]
    
    # 2. Historical traversals
    for c in xml_candidates:
         matches = glob.glob(c, recursive=True)
         if matches:
              xml_path = matches[0]
              break
              
    if not xml_path:
         historical_xml = [
              f"C:\\\\ITC\\\\Fappeal\\\\Planeta\\\\Outfile\\\\SAT\\\\Factura\\\\**\\\\{folio}.xml",
              f"C:\\\\ITC\\\\Fappeal\\\\Planeta\\\\Outfile\\\\SAT\\\\Factura\\\\**\\\\{clean_folio}.xml"
         ]
         for h in historical_xml:
              matches = glob.glob(h, recursive=True)
              if matches:
                   xml_path = matches[0]
                   break

    for c in pdf_candidates:
         matches = glob.glob(c, recursive=True)
         if matches:
              pdf_path = matches[0]
              break

    # 3. IF XML historical found, PDF MUST adjacent to bypass collision list traversals
    if xml_path and not pdf_path:
         adj_pdf = xml_path.replace('.xml', '.pdf')
         if os.path.exists(adj_pdf):
              pdf_path = adj_pdf

    return { "xml_path": xml_path, "pdf_path": pdf_path }"""

# Overwrite complete find_cfdi_attachments
import re
s = re.sub(r'def find_cfdi_attachments\(.*?\):.*?return \{ "xml_path": xml_path, "pdf_path": pdf_path \}', new_find_def, s, flags=re.DOTALL)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\services\cfdi_storage.py", "w", encoding="utf-8") as f:
    f.write(s)

print("Helper find_cfdi_attachments rewritten with strict ADJACENT fallback to eliminate collisions.")
