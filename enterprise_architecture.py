import os

# --- 1. Append to cfdi_storage.py ---
with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\services\cfdi_storage.py", "r", encoding="utf-8") as f:
    s = f.read()

helper_code = """
def find_cfdi_attachments(uuid: str, serie: str = "", folio: str = "") -> dict:
    \"\"\"
    [ES] Busca síncronamente los adjuntos (XML y PDF) en rutas de resguardo histórico y workspace.
    \"\"\"
    import glob
    xml_path = None
    pdf_path = None
    
    clean_folio = str(folio).lstrip('0') if folio else ""
    
    xml_candidates = [
         f"C:\\\\Test_Antigravity\\\\Gestor_CFDI_Vantec\\\\storage\\\\**\\\\{uuid}.xml",
         f"C:\\\\Test_Antigravity\\\\Gestor_CFDI_Vantec\\\\Operacion_CFDI\\\\**\\\\{uuid}.xml",
         f"C:\\\\ITC\\\\Fappeal\\\\Planeta\\\\Outfile\\\\SAT\\\\Factura\\\\**\\\\{folio}.xml",
         f"C:\\\\ITC\\\\Fappeal\\\\Planeta\\\\Outfile\\\\SAT\\\\Factura\\\\**\\\\{clean_folio}.xml"
    ]
    
    pdf_candidates = [
         f"C:\\\\Test_Antigravity\\\\Gestor_CFDI_Vantec\\\\storage\\\\**\\\\{uuid}.pdf",
         f"C:\\\\Test_Antigravity\\\\Gestor_CFDI_Vantec\\\\Operacion_CFDI\\\\**\\\\{uuid}.pdf",
         f"C:\\\\ITC\\\\Fappeal\\\\Planeta\\\\Outfile\\\\SAT\\\\Factura\\\\**\\\\{folio}.pdf",
         f"C:\\\\ITC\\\\Fappeal\\\\Planeta\\\\Outfile\\\\SAT\\\\Factura\\\\**\\\\{clean_folio}.pdf"
    ]

    for c in xml_candidates:
         matches = glob.glob(c, recursive=True)
         if matches:
              xml_path = matches[0]
              break
              
    for c in pdf_candidates:
         matches = glob.glob(c, recursive=True)
         if matches:
              pdf_path = matches[0]
              break
              
    return { "xml_path": xml_path, "pdf_path": pdf_path }
"""

if "def find_cfdi_attachments" not in s:
    s += helper_code

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\services\cfdi_storage.py", "w", encoding="utf-8") as f:
    f.write(s)

# --- 2. frontend_isolation.py ---
with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "r", encoding="utf-8") as f:
    js = f.read()

old_open = """window.openDetailDrawer = async function(uuid) {
    const drawer = document.getElementById('detailDrawer');"""

new_open = """window.openDetailDrawer = async function(uuid) {
    const drawer = document.getElementById('detailDrawer');
    const drawerContent = document.getElementById('drawerContent');
    if (drawerContent) {
        drawerContent.innerHTML = `<div class="p-12 text-center text-gray-400"><i class="fas fa-spinner fa-spin fa-2x"></i><p class="mt-2 text-xs">Cargando detalles...</p></div>`;
    }"""

js = js.replace(old_open, new_open)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "w", encoding="utf-8") as f:
    f.write(js)


# --- 3. Refactor orquestador.py ---
with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\orquestador.py", "r", encoding="utf-8") as f:
    oq = f.read()

# Update attachments list fetch 
old_preflight = """        # 3. Pre-flight Check: Verificar existencia física de archivos
        xml_path = cfdi.xml_file_path
        pdf_path = cfdi.pdf_file_path

        if not xml_path:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Ruta de XML no especificada en la base de datos."
            )"""

new_preflight = """        # 3. Pre-flight Check: Verificar con Helper Enterprise
        from src.services.cfdi_storage import find_cfdi_attachments
        att = find_cfdi_attachments(cfdi.uuid, getattr(cfdi, 'serie', ""), getattr(cfdi, 'folio', ""))
        xml_path = att["xml_path"] or cfdi.xml_file_path
        pdf_path = att["pdf_path"] or cfdi.pdf_file_path

        if not xml_path or not os.path.exists(xml_path):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Archivo XML no encontrado en rutas históricas resguardadas."
            )"""

oq = oq.replace(old_preflight, new_preflight)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\orquestador.py", "w", encoding="utf-8") as f:
    f.write(oq)

print("Architecture refactored applied")
