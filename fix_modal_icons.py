with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "r", encoding="utf-8") as f:
    c = f.read()

old_modal = """                        <button onclick="downloadCfdi('${r.uuid}', 'xml')" class="text-[#4EBCE9] hover:text-[#1E3A5F]" title="Descargar XML"><i class="fas fa-file-code fa-lg"></i></button>
                        <button onclick="downloadCfdi('${r.uuid}', 'pdf')" class="text-red-500 hover:text-red-700" title="Descargar PDF"><i class="fas fa-file-pdf fa-lg"></i></button>"""

new_modal = """                        <button onclick="downloadCfdi('${r.uuid}', 'xml')" class="text-[#4EBCE9] hover:text-[#1E3A5F]" title="Descargar XML"><i class="fas fa-file-code fa-lg"></i></button>
                        <button onclick="downloadCfdi('${r.uuid}', 'pdf')" class="${r.pdf_exists === true ? 'text-red-500 hover:text-red-700' : 'text-gray-300 cursor-not-allowed'}" title="Descargar PDF"><i class="fas fa-file-pdf fa-lg"></i></button>"""

if old_modal in c:
    c = c.replace(old_modal, new_modal)
    print("Modal icons conditional rendering fixed.")
else:
    # alternate approach for slight spacing
    c = c.replace("class=\"text-red-500 hover:text-red-700\"", "class=\"${r.pdf_exists === true ? 'text-red-500 hover:text-red-700' : 'text-gray-300 cursor-not-allowed'}\"")
    print("Fallback replace on modal icons.")

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "w", encoding="utf-8") as f:
    f.write(c)

print("Componentes Modal sincronizados.")
