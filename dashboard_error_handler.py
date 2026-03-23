with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\dashboard.js", "r", encoding="utf-8") as f:
    js = f.read()

old_catch = """    } catch (error) {
        console.error('🛡️ VANTEC DASHBOARD ERROR:', error);
        if (kpiTotalDocs) kpiTotalDocs.innerText = '0';
        if (topClientesContainer) {
            topClientesContainer.innerHTML = `
                <div class="flex items-center justify-center pt-8 text-gray-400">
                    <i class="fas fa-info-circle mr-2"></i> Error al cargar datos
                </div>
            `;
        }
    }"""

new_catch = """    } catch (error) {
        console.error('🛡️ VANTEC DASHBOARD ERROR:', error);
        if (kpiTotalDocs) kpiTotalDocs.innerText = 'Error';
        if (kpiTotalAmount) kpiTotalAmount.innerText = 'Error';
        if (kpiPpdPending) kpiPpdPending.innerText = 'Error';
        if (topClientesContainer) {
            topClientesContainer.innerHTML = `
                <div class="flex items-center justify-center pt-8 text-gray-400">
                    <i class="fas fa-exclamation-triangle mr-2 text-red-500"></i> Error al cargar datos
                </div>
            `;
        }
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: '❌ Error de Carga',
                text: 'No se pudo sincronizar el Dashboard: ' + error.message,
                icon: 'error',
                confirmButtonColor: '#1E3A5F'
            });
        }
    }"""

js = js.replace(old_catch, new_catch)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\dashboard.js", "w", encoding="utf-8") as f:
    f.write(js)

print("Dashboard Error Handler Applied")
