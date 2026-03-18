import os

js_path = "static/js/cfdis.js"
html_path = "templates/cfdis.html"

# 1. Edit cfdis.js
with open(js_path, 'r', encoding='utf-8') as f:
    js_content = f.read()

# - Remove Saldo TD inside createCfdiRow
target_row = """        <td class="px-4 py-4 text-right font-black text-[#1E3A5F]">${formatCurrency(total)}</td>
        <td class="px-4 py-4 text-right font-bold text-green-600">${formatCurrency(0)}</td>
        <td class="px-4 py-4 text-center">"""

replace_row = """        <td class="px-4 py-4 text-right font-black text-[#1E3A5F]">${formatCurrency(total)}</td>
        <td class="px-4 py-4 text-center">"""

if target_row in js_content:
    js_content = js_content.replace(target_row, replace_row)
    print("✅ Saldo column TD removed from createCfdiRow")
else:
    # Try with \r\n
    target_row_crlf = target_row.replace('\n', '\r\n')
    replace_row_crlf = replace_row.replace('\n', '\r\n')
    if target_row_crlf in js_content:
         js_content = js_content.replace(target_row_crlf, replace_row_crlf)
         print("✅ Saldo column TD removed (CRLF)")

# - Update abrirModalReenvio Call in main table
target_reenviar = """onclick="abrirModalReenvio('${cleanFolio}', '${cfdi.uuid}')\""""
replace_reenviar = """onclick="abrirModalReenvio('${cleanFolio}', '${cfdi.uuid}', '${cfdi.rfc_receptor}')\""""

if target_reenviar in js_content:
    js_content = js_content.replace(target_reenviar, replace_reenviar)
    print("✅ abrirModalReenvio main call updated")

# - Update abrirModalReenvio Call in relations sub-table
target_sub_reenviar = """onclick="abrirModalReenvio('${r.folio || 'S/N'}', '${r.uuid}')\""""
replace_sub_reenviar = """onclick="abrirModalReenvio('${r.folio || 'S/N'}', '${r.uuid}', '${r.rfc_receptor || ''}')\""""

if target_sub_reenviar in js_content:
    js_content = js_content.replace(target_sub_reenviar, replace_sub_reenviar)
    print("✅ abrirModalReenvio sub call updated")

# - Update abrirModalReenvio DEFINITION (add rfc argument, pre-fill)
target_def = """window.abrirModalReenvio = function(folio, uuid) {"""
replace_def = """window.abrirModalReenvio = function(folio, uuid, rfc) {
     const defaultEmail = rfc ? `${rfc.toLowerCase()}@correo.com` : '';"""

if target_def in js_content:
    js_content = js_content.replace(target_def, replace_def)
    
    # Also find the input tag to pre-fill
    target_input = """<input type="email" id="destinatario" required class="w-full px-4 py-2 border rounded-xl text-sm focus:outline-none focus:border-blue-500" placeholder="ejemplo@correo.com">"""
    replace_input = """<input type="email" id="destinatario" required value="${defaultEmail}" class="w-full px-4 py-2 border rounded-xl text-sm focus:outline-none focus:border-blue-500" placeholder="ejemplo@correo.com">"""
    js_content = js_content.replace(target_input, replace_input)
    print("✅ abrirModalReenvio definition & input filled updated")

# - Replace alert() with Swal.fire inside downloadCfdi
target_alert = """alert(`Error: ${errData.detail || "Archivo no encontrado"}`);"""
replace_alert = """Swal.fire({ icon: 'error', title: 'Error de Descarga', text: errData.detail || "Archivo no disponible", confirmButtonColor: '#1E3A5F' });"""

if target_alert in js_content:
    js_content = js_content.replace(target_alert, replace_alert)
    print("✅ alert() replaced with Swal.fire")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js_content)

# 2. Edit cfdis.html (Remove <th>Saldo</th>)
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

target_th = """                        <th class="px-6 py-4 text-right">Total</th>
                        <th class="px-6 py-4 text-right">Saldo</th>"""

replace_th = """                        <th class="px-6 py-4 text-right">Total</th>"""

if target_th in html_content:
    html_content = html_content.replace(target_th, replace_th)
    print("✅ Saldo TH removed from HTML")
else:
    # Try with CRLF
    target_th_crlf = target_th.replace('\n', '\r\n')
    replace_th_crlf = replace_th.replace('\n', '\r\n')
    if target_th_crlf in html_content:
         html_content = html_content.replace(target_th_crlf, replace_th_crlf)
         print("✅ Saldo TH removed from HTML (CRLF)")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ Polish applied.")
