with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "r", encoding="utf-8") as f:
    c = f.read()

# 1. Update populateHeaderFilters
old_populate = """function populateHeaderFilters(data) {
    const receptorSelect = document.getElementById('receptorFilter');
    const tipoSelect = document.getElementById('tipoFilter');
    const estadoSelect = document.getElementById('estadoFilter');

    if (!receptorSelect || !tipoSelect || !estadoSelect) return;

    // Clear existing options except "Todos"
    receptorSelect.innerHTML = '<option value="">Todos</option>';
    tipoSelect.innerHTML = '<option value="">Todos</option>';
    estadoSelect.innerHTML = '<option value="">Todos</option>';

    const receptors = [...new Set(data.map(c => c.rfc_receptor).filter(Boolean))];
    const tipos = [...new Set(data.map(c => c.tipo).filter(Boolean))];
    const estados = [...new Set(data.map(c => c.estatus).filter(Boolean))];

    receptors.sort().forEach(r => {
        receptorSelect.innerHTML += `<option value="${r}">${r}</option>`;
    });

    tipos.sort().forEach(t => {
        const tLabel = t === 'P' ? 'Pago' : t === 'E' ? 'Egreso' : t === 'N' ? 'Nómina' : t === 'T' ? 'Traslado' : 'Ingreso';
        tipoSelect.innerHTML += `<option value="${t}">${tLabel}</option>`;
    });

    estados.sort().forEach(e => {
        estadoSelect.innerHTML += `<option value="${e}">${e}</option>`;
    });

    // Wire up change events to trigger filtering
    receptorSelect.onchange = applyFilters;
    tipoSelect.onchange = applyFilters;
    estadoSelect.onchange = applyFilters;
}"""

new_populate = """function populateHeaderFilters(data) {
    const receptorSelect = document.getElementById('receptorFilter');
    const tipoSelect = document.getElementById('tipoFilter');
    const estadoSelect = document.getElementById('estadoFilter');
    const metodoSelect = document.getElementById('metodoFilter');
    const formaSelect = document.getElementById('formaFilter');

    if (receptorSelect) receptorSelect.innerHTML = '<option value="">Todos</option>';
    if (tipoSelect) tipoSelect.innerHTML = '<option value="">Todos</option>';
    if (estadoSelect) estadoSelect.innerHTML = '<option value="">Todos</option>';
    if (metodoSelect) metodoSelect.innerHTML = '<option value="">Todos</option>';
    if (formaSelect) formaSelect.innerHTML = '<option value="">Todas</option>';

    const receptors = [...new Set(data.map(c => c.rfc_receptor).filter(Boolean))];
    const tipos = [...new Set(data.map(c => c.tipo).filter(Boolean))];
    const estados = [...new Set(data.map(c => c.estatus).filter(Boolean))];
    const metodos = [...new Set(data.map(c => c.metodo_pago).filter(Boolean))];
    const formas = [...new Set(data.map(c => c.forma_pago).filter(Boolean))];

    if (receptorSelect) receptors.sort().forEach(r => { receptorSelect.innerHTML += `<option value="${r}">${r}</option>`; });
    if (tipoSelect) tipos.sort().forEach(t => {
        const tLabel = t === 'P' ? 'Pago' : t === 'E' ? 'Egreso' : t === 'N' ? 'Nómina' : t === 'T' ? 'Traslado' : 'Ingreso';
        tipoSelect.innerHTML += `<option value="${t}">${tLabel}</option>`;
    });
    if (estadoSelect) estados.sort().forEach(e => { estadoSelect.innerHTML += `<option value="${e}">${e}</option>`; });
    if (metodoSelect) metodos.sort().forEach(m => { metodoSelect.innerHTML += `<option value="${m}">${m}</option>`; });
    if (formaSelect) formas.sort().forEach(f => { formaSelect.innerHTML += `<option value="${f}">${f}</option>`; });

    if (receptorSelect) receptorSelect.onchange = applyFilters;
    if (tipoSelect) tipoSelect.onchange = applyFilters;
    if (estadoSelect) estadoSelect.onchange = applyFilters;
    if (metodoSelect) metodoSelect.onchange = applyFilters;
    if (formaSelect) formaSelect.onchange = applyFilters;
}"""

c = c.replace(old_populate, new_populate)

# 2. Update applyFilters
old_apply_vars = """    const receptorHeader = document.getElementById('receptorFilter')?.value;
    const tipoHeader = document.getElementById('tipoFilter')?.value;
    const estadoHeader = document.getElementById('estadoFilter')?.value;"""

new_apply_vars = """    const receptorHeader = document.getElementById('receptorFilter')?.value;
    const tipoHeader = document.getElementById('tipoFilter')?.value;
    const estadoHeader = document.getElementById('estadoFilter')?.value;
    const metodoHeader = document.getElementById('metodoFilter')?.value;
    const formaHeader = document.getElementById('formaFilter')?.value;"""

c = c.replace(old_apply_vars, new_apply_vars)

old_apply_conditions = """    if (estadoHeader) {
        filtered = filtered.filter(c => c.estatus === estadoHeader);
    }"""

new_apply_conditions = """    if (estadoHeader) {
        filtered = filtered.filter(c => c.estatus === estadoHeader);
    }

    if (metodoHeader) {
        filtered = filtered.filter(c => c.metodo_pago === metodoHeader);
    }

    if (formaHeader) {
        filtered = filtered.filter(c => c.forma_pago === formaHeader);
    }"""

c = c.replace(old_apply_conditions, new_apply_conditions)

# 3. Update resetFilters
old_reset = """    if (document.getElementById('receptorFilter')) document.getElementById('receptorFilter').value = '';
    if (document.getElementById('tipoFilter')) document.getElementById('tipoFilter').value = '';
    if (document.getElementById('estadoFilter')) document.getElementById('estadoFilter').value = '';"""

new_reset = """    if (document.getElementById('receptorFilter')) document.getElementById('receptorFilter').value = '';
    if (document.getElementById('tipoFilter')) document.getElementById('tipoFilter').value = '';
    if (document.getElementById('estadoFilter')) document.getElementById('estadoFilter').value = '';
    if (document.getElementById('metodoFilter')) document.getElementById('metodoFilter').value = '';
    if (document.getElementById('formaFilter')) document.getElementById('formaFilter').value = '';"""

c = c.replace(old_reset, new_reset)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "w", encoding="utf-8") as f:
    f.write(c)

print("Frontend filters Applied")
