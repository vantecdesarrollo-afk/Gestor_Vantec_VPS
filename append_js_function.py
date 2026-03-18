import os

file_path = "static/js/cfdis.js"

append_code = """
window.abrirModalReenvio = function(folio, uuid) {
     const overlay = document.createElement('div');
     overlay.className = "fixed inset-0 bg-black/50 backdrop-blur-sm z-[90] flex items-center justify-center p-4";
     overlay.id = "modalReenvioDynamic";

     overlay.innerHTML = `
         <div class="bg-white rounded-xl shadow-2xl w-full max-w-md p-6 transform transition-all">
             <div class="flex items-center justify-between border-b pb-4">
                 <h3 class="font-black text-lg text-[#1E3A5F]"><i class="fas fa-paper-plane mr-2 text-blue-500"></i> Reenviar Comprobante</h3>
                 <button onclick="document.getElementById('modalReenvioDynamic').remove()" class="text-gray-400 hover:text-red-500"><i class="fas fa-times fa-lg"></i></button>
             </div>
             
             <form id="formReenvio" class="mt-4 space-y-4">
                 <input type="hidden" id="reenvio-uuid" value="${uuid}">
                 
                 <div>
                     <label class="block text-xs font-bold text-gray-500 uppercase">Folio</label>
                     <p class="text-sm font-black text-[#1E3A5F]">${folio}</p>
                 </div>

                 <div>
                     <label for="destinatario" class="block text-xs font-bold text-gray-500 uppercase mb-1">Correo Destinatario</label>
                     <input type="email" id="destinatario" required class="w-full px-4 py-2 border rounded-xl text-sm focus:outline-none focus:border-blue-500" placeholder="ejemplo@correo.com">
                 </div>

                 <div>
                     <label for="asunto" class="block text-xs font-bold text-gray-500 uppercase mb-1">Asunto</label>
                     <input type="text" id="asunto" value="Envío de Comprobante Fiscal - Folio ${folio}" required class="w-full px-4 py-2 border rounded-xl text-sm focus:outline-none focus:border-blue-500">
                 </div>

                 <div>
                     <label for="cuerpo" class="block text-xs font-bold text-gray-500 uppercase mb-1">Mensaje</label>
                     <textarea id="cuerpo" rows="3" class="w-full px-4 py-2 border rounded-xl text-sm focus:outline-none focus:border-blue-500">Adjuntamos el Comprobante Fiscal solicitado.</textarea>
                 </div>

                 <button type="submit" id="btnSubmitReenvio" class="w-full bg-[#1E3A5F] text-white py-2 rounded-xl font-bold hover:bg-[#152842] transition-colors flex items-center justify-center space-x-2">
                     <i class="fas fa-paper-plane"></i>
                     <span>Enviar Correo</span>
                 </button>
             </form>
         </div>
     `;

    document.body.appendChild(overlay);

    const form = document.getElementById('formReenvio');
    form.addEventListener('submit', async (e) => {
         e.preventDefault();
         const btn = document.getElementById('btnSubmitReenvio');
         btn.disabled = true;
         btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> <span>Enviando...</span>`;

         const payload = {
              uuid_documento: document.getElementById('reenvio-uuid').value,
              destinatario: document.getElementById('destinatario').value,
              asunto: document.getElementById('asunto').value,
              cuerpo: document.getElementById('cuerpo').value
         };

         try {
              const response = await fetch('/api/orquestador/reenvio', {
                   method: 'POST',
                   headers: { 'Content-Type': 'application/json' },
                   body: JSON.stringify(payload)
              });

              if (response.ok) {
                   alert("✅ Comprobante enviado exitosamente.");
                   overlay.remove();
              } else {
                   const err = await response.json();
                   alert(`❌ Error al enviar: ${err.detail || "Falla desconocida"}`);
              }
         } catch (error) {
              alert(`❌ Error de red: ${error.message}`);
         } finally {
              if (btn) {
                   btn.disabled = false;
                   btn.innerHTML = `<i class="fas fa-paper-plane"></i> <span>Enviar Correo</span>`;
              }
         }
    });
};
"""

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "window.abrirModalReenvio" not in content:
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n" + append_code)
    print("✅ Appended abrirModalReenvio successfully.")
else:
    print("ℹ️ abrirModalReenvio already exists.")
