file_path = "static/js/cfdis.js"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

placeholder = "function populateHeaderFilters() {} // Placeholder para evitar errores de referencia"

new_code = """function populateHeaderFilters(data) {
    const receptorSelect = document.getElementById('receptorFilter');
    const tipoSelect = document.getElementById('tipoFilter');
    const estadoSelect = document.getElementById('estadoFilter');

    if (!receptorSelect || !tipoSelect || !estadoSelect) return;

    // Clear existing options except "Todos"
    receptorSelect.innerHTML = '<option value="">Todos</option>';
    tipoSelect.innerHTML = '<option value="">Todos</option>';
    estadoSelect.innerHTML = '<option value="">Todos</option>';

    const receptors = [...new Set(data.map(c => c.rfc_receptor).filter(Boolean))];
    const tipos = [...new Set(data.map(c => c.tipo_comprobante).filter(Boolean))];
    const estados = [...new Set(data.map(c => c.status).filter(Boolean))];

    receptors.sort().forEach(r => {
        receptorSelect.innerHTML += `<option value="${r}">${r}</option>`;
    });

    tipos.sort().forEach(t => {
        tipoSelect.innerHTML += `<option value="${t}">${t}</option>`;
    });

    estados.sort().forEach(e => {
        estadoSelect.innerHTML += `<option value="${e}">${e}</option>`;
    });

    // Wire up change events to trigger filtering
    receptorSelect.onchange = applyFilters;
    tipoSelect.onchange = applyFilters;
    estadoSelect.onchange = applyFilters;
}

window.applyFilters = function() {
    let filtered = [...allCfdis];

    const serie = document.getElementById('filterSerie')?.value.trim().toUpperCase();
    const folioStart = parseInt(document.getElementById('filterFolioStart')?.value);
    const folioEnd = parseInt(document.getElementById('filterFolioEnd')?.value);
    const filterType = document.getElementById('filterType')?.value;

    if (serie) {
        filtered = filtered.filter(c => (c.serie || '').toUpperCase() === serie);
    }

    if (!isNaN(folioStart)) {
        filtered = filtered.filter(c => {
            const f = parseInt(c.folio);
            return !isNaN(f) && f >= folioStart;
        });
    }

    if (!isNaN(folioEnd)) {
        filtered = filtered.filter(c => {
            const f = parseInt(c.folio);
            return !isNaN(f) && f <= folioEnd;
        });
    }

    if (filterType) {
        filtered = filtered.filter(c => c.tipo_comprobante === filterType);
    }

    const receptorHeader = document.getElementById('receptorFilter')?.value;
    const tipoHeader = document.getElementById('tipoFilter')?.value;
    const estadoHeader = document.getElementById('estadoFilter')?.value;

    if (receptorHeader) {
        filtered = filtered.filter(c => c.rfc_receptor === receptorHeader);
    }

    if (tipoHeader) {
        filtered = filtered.filter(c => c.tipo_comprobante === tipoHeader);
    }

    if (estadoHeader) {
        filtered = filtered.filter(c => c.status === estadoHeader);
    }

    renderTable(filtered);
    
    const counter = document.getElementById('cfdiCounter');
    if (counter) {
        counter.innerText = `Mostrando ${filtered.length} resultados`;
    }
};

window.resetFilters = function() {
    if (document.getElementById('filterSerie')) document.getElementById('filterSerie').value = '';
    if (document.getElementById('filterFolioStart')) document.getElementById('filterFolioStart').value = '';
    if (document.getElementById('filterFolioEnd')) document.getElementById('filterFolioEnd').value = '';
    if (document.getElementById('filterType')) document.getElementById('filterType').value = '';
    
    if (document.getElementById('receptorFilter')) document.getElementById('receptorFilter').value = '';
    if (document.getElementById('tipoFilter')) document.getElementById('tipoFilter').value = '';
    if (document.getElementById('estadoFilter')) document.getElementById('estadoFilter').value = '';

    renderTable(allCfdis);
    const counter = document.getElementById('cfdiCounter');
    if (counter) {
        counter.innerText = `Mostrando ${allCfdis.length} resultados`;
    }
};"""

if placeholder in content:
    content = content.replace(placeholder, new_code)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Header filters implemented successfully.")
else:
    # Fallback if comment differs
    if "function populateHeaderFilters() {}" in content:
         content = content.replace("function populateHeaderFilters() {}", new_code)
         with open(file_path, 'w', encoding='utf-8') as f:
             f.write(content)
         print("✅ Header filters implemented successfully (fallback match).")
    else:
         print("❌ Placeholder not found.")
