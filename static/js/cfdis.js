/**
 * cfdis.js - Lógica para el Explorador de Documentos Vantec
 * REPARADO: Conexión estricta a /api/v1/comprobantes/
 */

let allCfdis = [];

const formatCurrency = (amount) => {
    return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(amount);
};

let isLoadingCfdis = false;
async function loadCfdis() {
    if (isLoadingCfdis) return;
    isLoadingCfdis = true;
    const tableBody = document.getElementById('cfdiTableBody');
    const counter = document.getElementById('cfdiCounter');

    // Validación de Entidad Activa (Multi-tenant)
    let activeEntidad = localStorage.getItem('active_entidad');

    // 1. Sincronizar Selección Visual (Prioridad Absoluta)
    const selector = document.getElementById('entity-selector');
    if (selector && selector.value && selector.value !== "") {
        if (selector.value !== activeEntidad) {
            console.log("[CFDIS] Sincronizando visual prioritaria con localStorage:", selector.value);
            activeEntidad = selector.value;
            localStorage.setItem('active_entidad', activeEntidad);
        }
    }

    console.log(`[VANTEC AUDIT] Consultando para Entidad: ${activeEntidad}`);

    if (!activeEntidad || activeEntidad === 'null' || activeEntidad === '') {
        if (tableBody) {
            tableBody.innerHTML = `<tr><td colspan="11" class="px-6 py-12 text-center text-orange-400 font-bold"><i class="fas fa-exclamation-triangle mr-2"></i> ERROR: Seleccione una empresa en el menú superior para activar la vista.</td></tr>`;
        }
        return;
    }

    try {
        // Forzamos la ruta correcta de la tabla 'comprobantes' con timestamp para evitar caché
        const url = `/api/v1/comprobantes?t=${Date.now()}`;
        const data = await vantecFetch(url);

        
        console.log(`[VANTEC AUDIT] Respuesta del Servidor:`, data);
        allCfdis = Array.isArray(data) ? data : [];

        populateHeaderFilters(allCfdis);
        renderTable(allCfdis);

        if (counter) {
            counter.innerText = `Mostrando ${allCfdis.length} resultados en tiempo real`;
        }

    } catch (error) {
        console.error('[VANTEC FATAL] Fallo al cargar desde /api/v1/comprobantes/:', error);
        if (tableBody) {
            tableBody.innerHTML = `<tr><td colspan="11" class="px-6 py-12 text-center text-red-500 font-bold">Error de conexión: ${error.message}</td></tr>`;
        }
    } finally {
        isLoadingCfdis = false;
    }
}

function renderTable(data) {
    const tableBody = document.getElementById('cfdiTableBody');
    if (!tableBody) return;

    tableBody.innerHTML = '';

    if (data.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="11" class="px-6 py-16 text-center">
                    <div class="flex flex-col items-center justify-center space-y-3">
                        <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center text-[#4EBCE9] animate-pulse">
                            <i class="fas fa-search fa-2x"></i>
                        </div>
                        <p class="text-vantec-primary font-bold text-lg">Sin documentos para esta entidad</p>
                        <p class="text-gray-400 text-xs">Asegúrate de que el RFC en pgAdmin coincida con la empresa seleccionada.</p>
                        <button onclick="loadCfdis()" class="mt-4 px-4 py-2 bg-[#4EBCE9] text-white rounded-lg font-bold text-xs"><i class="fas fa-sync-alt mr-2"></i> Forzar Actualización</button>
                    </div>
                </td>
            </tr>`;
        return;
    }

    data.forEach(cfdi => {
        const fragment = createCfdiRow(cfdi);
        tableBody.appendChild(fragment);
    });
}

function createCfdiRow(cfdi) {
    if (!cfdi) return document.createDocumentFragment();

    const tr = document.createElement('tr');
    tr.className = 'hover:bg-gray-50/50 transition-colors border-b border-gray-100';

    const serie = cfdi.serie || '';
    const folio = cfdi.folio || 'S/N';
    const cleanFolio = cfdi.folio && cfdi.folio !== 'S/N' ? cfdi.folio.replace(/^0+/, '') || '0' : 'S/N';
    const serieFolio = (serie && cleanFolio !== 'S/N') ? `${serie}-${cleanFolio}` : cleanFolio;
    const fechaStr = cfdi.fecha || '---';
    const total = parseFloat(cfdi.total || 0);

    const pdf_exists = cfdi.pdf_exists === true || cfdi.pdf_exists === 'true';
    const xml_exists = cfdi.xml_exists === true || cfdi.xml_exists === 'true';
    const hasReps = cfdi.tiene_relacionados === true;

    let metodoHtml = cfdi.metodo_pago || '---';

    let tipoBg = 'bg-blue-50'; let tipoColor = 'text-[#1E3A5F]'; let tipoLabel = 'Ingreso';
    if (cfdi.tipo === 'P') { tipoBg = 'bg-green-50'; tipoColor = 'text-green-600'; tipoLabel = 'Pago'; }
    else if (cfdi.tipo === 'E') { tipoBg = 'bg-red-50'; tipoColor = 'text-red-600'; tipoLabel = 'Egreso'; }
    else if (cfdi.tipo === 'N') { tipoBg = 'bg-purple-50'; tipoColor = 'text-purple-600'; tipoLabel = 'Nómina'; }
    else if (cfdi.tipo === 'T') { tipoBg = 'bg-gray-50'; tipoColor = 'text-gray-600'; tipoLabel = 'Traslado'; }

    const linkIcon = hasReps ? `<button onclick="mostrarModalRelaciones('${cfdi.uuid}')" class="text-green-500 hover:text-green-600" title="Ver Asociaciones"><i class="fas fa-link fa-lg"></i></button>` : '';

    // RBAC: Visor no puede enviar correos
    const payload = getUserPayload();
    const activeEntidad = localStorage.getItem('active_entidad');
    const activeEntidadData = payload && payload.entidades ? payload.entidades.find(e => e.id === activeEntidad) : null;
    const currentRole = activeEntidadData ? activeEntidadData.rol : (payload && payload.is_superadmin ? 'ADMIN' : 'VISOR');
    const reenvioBtn = currentRole !== 'VISOR' ? `<button onclick="abrirModalReenvio('${cleanFolio}', '${cfdi.uuid}', '${cfdi.rfc_receptor}')" class="text-gray-400 hover:text-[#1E3A5F]" title="Reenviar Correo"><i class="fas fa-envelope fa-lg"></i></button>` : '';

    tr.innerHTML = `
        <td class="px-6 py-4">
            <button onclick="console.log('Expand')" class="text-gray-400 hover:text-vantec-primary"><i class="fas fa-chevron-right text-xs"></i></button>
        </td>
        <td class="px-6 py-4 text-gray-600 font-medium whitespace-nowrap text-xs">${fechaStr}</td>
        <td class="px-6 py-4 whitespace-nowrap align-middle">
            <div>
                <p class="font-bold text-[#1E3A5F] text-sm">${serieFolio}</p>
                <p class="text-[10px] text-gray-400 font-mono">${(cfdi.uuid || '').substring(0, 13)}...</p>
            </div>
        </td>
        <td class="px-6 py-4">
            <div class="max-w-[180px]">
                <p class="font-bold text-[#1E3A5F] text-xs truncate" title="${cfdi.nombre_receptor || 'S/N'}">${cfdi.nombre_receptor || 'S/N'}</p>
                <p class="text-[10px] text-gray-400 font-medium">${cfdi.rfc_receptor || 'N/A'}</p>
            </div>
        </td>
        <td class="px-4 py-4 text-center font-bold text-[#1E3A5F] text-xs">${metodoHtml}</td>
        <td class="px-4 py-4 text-center font-bold text-gray-400 text-xs">${cfdi.forma_pago || '---'}</td>
        <td class="px-4 py-4 text-center">
             <span class="px-2 py-1 ${tipoBg} ${tipoColor} rounded text-[10px] font-bold">${tipoLabel}</span>
        </td>
        <td class="px-4 py-4 text-right font-black text-[#1E3A5F]">${formatCurrency(total)}</td>
        <td class="px-4 py-4 text-center">
            ${cfdi.estatus === 'Vigente' || cfdi.estatus === 'Pagado' ? '<span class="px-2 py-1 bg-green-50 text-green-600 rounded-full text-[10px] font-bold"><i class="fas fa-check-circle mr-1"></i>Vigente</span>' :
              cfdi.estatus === 'Pendiente' ? '<span class="px-2 py-1 bg-red-50 text-red-600 rounded-full text-[10px] font-bold"><i class="fas fa-exclamation-circle mr-1"></i>Pendiente</span>' :
              cfdi.estatus === 'Parcial' ? '<span class="px-2 py-1 bg-amber-50 text-amber-600 rounded-full text-[10px] font-bold"><i class="fas fa-hourglass-half mr-1"></i>Parcial</span>' :
              cfdi.estatus === 'Cancelado' ? '<span class="px-2 py-1 bg-gray-50 text-gray-400 rounded-full text-[10px] font-bold"><i class="fas fa-times-circle mr-1"></i>Cancelado</span>' :
              `<span class="px-2 py-1 bg-gray-50 text-gray-400 rounded-full text-[10px] font-bold">${cfdi.estatus || '---'}</span>`}
        </td>
        <td class="px-4 py-4 text-right">
            <div class="flex items-center justify-end space-x-3">
                <button onclick="openDetailDrawer('${cfdi.uuid}')" class="text-gray-400 hover:text-[#1E3A5F]" title="Ver Detalles"><i class="fas fa-search-plus fa-lg"></i></button>
                ${linkIcon}
                ${reenvioBtn}
                <button onclick="downloadCfdi('${cfdi.uuid}', 'xml')" class="${xml_exists ? 'text-[#4EBCE9]' : 'text-gray-400'}" title="Descargar XML"><i class="fas fa-file-code fa-lg"></i></button>
                <button onclick="downloadCfdi('${cfdi.uuid}', 'pdf')" class="${pdf_exists ? 'text-red-500' : 'text-gray-400'}" title="Descargar PDF"><i class="fas fa-file-pdf fa-lg"></i></button>
            </div>
        </td>
    `;

    const fragment = document.createDocumentFragment();
    fragment.appendChild(tr);
    return fragment;
}



function populateHeaderFilters(data) {
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
        filtered = filtered.filter(c => c.tipo === filterType);
    }

    const receptorHeader = document.getElementById('receptorFilter')?.value;
    const tipoHeader = document.getElementById('tipoFilter')?.value;
    const estadoHeader = document.getElementById('estadoFilter')?.value;
    const metodoHeader = document.getElementById('metodoFilter')?.value;
    const formaHeader = document.getElementById('formaFilter')?.value;

    if (receptorHeader) {
        filtered = filtered.filter(c => c.rfc_receptor === receptorHeader);
    }

    if (tipoHeader) {
        filtered = filtered.filter(c => c.tipo === tipoHeader);
    }

    if (estadoHeader) {
        filtered = filtered.filter(c => c.estatus === estadoHeader);
    }

    if (metodoHeader) {
        filtered = filtered.filter(c => c.metodo_pago === metodoHeader);
    }

    if (formaHeader) {
        filtered = filtered.filter(c => c.forma_pago === formaHeader);
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
    if (document.getElementById('metodoFilter')) document.getElementById('metodoFilter').value = '';
    if (document.getElementById('formaFilter')) document.getElementById('formaFilter').value = '';

    renderTable(allCfdis);
    const counter = document.getElementById('cfdiCounter');
    if (counter) {
        counter.innerText = `Mostrando ${allCfdis.length} resultados`;
    }
};

window.openDetailDrawer = async function(uuid) {
    const drawer = document.getElementById('detailDrawer');
    const drawerContent = document.getElementById('drawerContent');
    const btnPdf = document.getElementById('btn-drawer-pdf');
    
    const content = drawerContent;
    if (!drawer || !content) return;

    content.innerHTML = `
        <div class="flex flex-col items-center justify-center py-12 space-y-2">
            <div class="w-10 h-10 border-4 border-gray-100 border-t-vantec-accent rounded-full animate-spin"></div>
            <p class="text-xs text-gray-400 font-bold uppercase tracking-wider">Cargando detalles...</p>
        </div>
    `;
    drawer.classList.remove('translate-x-full');

    try {
        const cfdi = await vantecFetch(`/api/v1/comprobantes/${uuid}`);
        if (btnPdf) btnPdf.setAttribute('data-uuid', uuid);

        const cleanFolio = cfdi.folio && cfdi.folio !== 'S/N' ? cfdi.folio.replace(/^0+/, '') || '0' : 'S/N';

        content.innerHTML = `
            <div class="space-y-6">
                <div class="bg-gray-50 p-4 rounded-xl space-y-2">
                    <p class="text-xs font-bold text-gray-400 uppercase">Información General</p>
                    <div class="grid grid-cols-2 gap-2 text-sm">
                        <div><span class="text-gray-400">Serie/Folio:</span> <span class="font-bold text-[#1E3A5F]">${cfdi.serie || ''}${cleanFolio}</span></div>
                        <div><span class="text-gray-400">Tipo:</span> <span class="font-bold">${cfdi.tipo_comprobante}</span></div>
                        <div><span class="text-gray-400">Método:</span> <span class="font-bold">${cfdi.metodo_pago || 'N/A'}</span></div>
                        <div><span class="text-gray-400">Forma:</span> <span class="font-bold">${cfdi.forma_pago || 'N/A'}</span></div>
                    </div>
                    <div class="border-t border-gray-100 pt-2 mt-1 text-xs">
                        <span class="text-gray-400 font-medium">Descripción:</span>
                        <p class="font-semibold text-[#1E3A5F] mt-0.5 break-words">${cfdi.descripcion_concepto || 'Sin descripción'}</p>
                    </div>
                </div>
                
                <div class="bg-gray-50 p-4 rounded-xl space-y-2">
                    <p class="text-xs font-bold text-gray-400 uppercase">Fiscales</p>
                    <div class="space-y-1 text-sm">
                        <p><span class="text-gray-400 font-medium">UUID:</span> <span class="font-mono text-xs break-all">${cfdi.uuid}</span></p>
                        <p><span class="text-gray-400 font-medium">Emisor:</span> <span class="font-semibold text-xs">${cfdi.rfc_emisor}</span></p>
                        <p><span class="text-gray-400 font-medium">Receptor:</span> <span class="font-semibold text-xs">${cfdi.rfc_receptor}</span></p>
                    </div>
                </div>

                <div class="border-t border-dashed border-gray-200 pt-4 flex items-center justify-between">
                    <p class="text-sm font-bold text-gray-500">Monto Total</p>
                    <p class="text-2xl font-black text-green-600">${formatCurrency(cfdi.total)}</p>
                </div>
            </div>
        `;

        const btnShare = document.getElementById('btn-drawer-share');
        if (btnShare) {
            btnShare.onclick = () => abrirModalReenvio(cfdi.folio || 'S/N', cfdi.uuid);
        }

    } catch (error) {
        content.innerHTML = `
            <div class="p-6 text-center space-y-2">
                <i class="fas fa-exclamation-circle fa-2x text-red-400"></i>
                <p class="text-red-500 font-bold">Error al cargar detalles</p>
                <p class="text-gray-400 text-xs">${error.message}</p>
            </div>
        `;
    }
};

window.closeDetailDrawer = function() {
    const drawer = document.getElementById('detailDrawer');
    if (drawer) drawer.classList.add('translate-x-full');
};
window.downloadCfdi = async function(uuid, type) {
    const activeEntidad = localStorage.getItem('active_entidad');
    const token = localStorage.getItem('token'); 

    if (!token) {
        alert("Sesión no válida o expirada.");
        return;
    }

    try {
        const response = await fetch(`/api/v1/comprobantes/${uuid}/${type}?entidad_id=${activeEntidad}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const disposition = response.headers.get('Content-Disposition');
            let filename = `${uuid}.${type}`;
            if (disposition && disposition.indexOf('filename=') !== -1) {
                filename = disposition.split('filename=')[1].replace(/"/g, '');
            }
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } else {
            try {
                const errData = await response.json();
                Swal.fire({ icon: 'error', title: 'Error de Descarga', text: errData.detail || "Archivo no disponible", confirmButtonColor: '#1E3A5F' });
            } catch (e) {
                alert("Error al descargar el archivo o archivo no encontrado.");
            }
        }
    } catch (error) {
        console.error("🛡️ VANTEC DOWNLOAD ERROR:", error);
        alert("Error de red al descargar el archivo.");
    }
};

document.addEventListener('DOMContentLoaded', loadCfdis);

window.mostrarModalRelaciones = function(uuid) {
    const cfdi = allCfdis.find(c => c.uuid === uuid);
    if (!cfdi || !cfdi.reps_asociados) return;

    // RBAC: Visor no puede enviar correos
    const payload = getUserPayload();
    const activeEntidad = localStorage.getItem('active_entidad');
    const activeEntidadData = payload && payload.entidades ? payload.entidades.find(e => e.id === activeEntidad) : null;
    const currentRole = activeEntidadData ? activeEntidadData.rol : (payload && payload.is_superadmin ? 'ADMIN' : 'VISOR');

    const overlay = document.createElement('div');
    overlay.className = "fixed inset-0 bg-black/50 z-[80] flex items-center justify-center p-4";
    overlay.id = "modalRelacionesDynamic";

    let rowsHtml = "";
    cfdi.reps_asociados.forEach(r => {
        const cleanRRepFolio = r.folio && r.folio !== 'S/N' ? r.folio.replace(/^0+/, '') || '0' : 'S/N';
        const reenvioBtnRel = currentRole !== 'VISOR' ? `<button onclick="abrirModalReenvio('${r.folio || 'S/N'}', '${r.uuid}', '${r.rfc_receptor || ''}')" class="text-gray-400 hover:text-[#1E3A5F]" title="Reenviar"><i class="fas fa-envelope fa-lg"></i></button>` : '';
        rowsHtml += `
            <tr class="border-b border-gray-100 hover:bg-gray-50">
                <td class="px-4 py-3 font-bold text-[#1E3A5F]">${r.tipo_documento || 'Pago'} ${cleanRRepFolio}</td>
                <td class="px-4 py-3 font-mono text-xs text-gray-500">${r.uuid.substring(0,8)}...</td>
                <td class="px-4 py-3 text-right font-black text-green-600">${formatCurrency(r.monto)}</td>
                <td class="px-4 py-3 text-right">
                    <div class="flex items-center justify-end space-x-3">
                        <button onclick="openDetailDrawer('${r.uuid}')" class="text-gray-400 hover:text-[#1E3A5F]" title="Ver Detalles"><i class="fas fa-search-plus fa-lg"></i></button>
                        <button onclick="downloadCfdi('${r.uuid}', 'xml')" class="text-[#4EBCE9] hover:text-[#1E3A5F]" title="Descargar XML"><i class="fas fa-file-code fa-lg"></i></button>
                        <button onclick="downloadCfdi('${r.uuid}', 'pdf')" class="${r.pdf_exists === true ? 'text-red-500 hover:text-red-700' : 'text-gray-300 cursor-not-allowed'}" title="Descargar PDF"><i class="fas fa-file-pdf fa-lg"></i></button>
                        ${reenvioBtnRel}
                    </div>
                </td>
            </tr>
        `;
    });

    overlay.innerHTML = `
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-xl p-6 transform transition-all">
            <div class="flex items-center justify-between border-b pb-4">
                <h3 class="font-black text-lg text-[#1E3A5F]"><i class="fas fa-link mr-2 text-green-500"></i> Documentos Asociados</h3>
                <button onclick="document.getElementById('modalRelacionesDynamic').remove()" class="text-gray-400 hover:text-red-500"><i class="fas fa-times fa-lg"></i></button>
            </div>
            <div class="mt-4 overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-gray-50 text-gray-600 text-xs font-bold">
                            <th class="px-4 py-2">Documento</th>
                            <th class="px-4 py-2">UUID</th>
                            <th class="px-4 py-2 text-right">Monto</th>
                            <th class="px-4 py-2 text-right">Acciones</th>
                        </tr>
                    </thead>
                    <tbody class="text-sm">
                        ${rowsHtml}
                    </tbody>
                </table>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);
};

window.abrirModalReenvio = function(folio, uuid, rfc) {
     const defaultEmail = rfc ? `${rfc.toLowerCase()}@correo.com` : '';
     const overlay = document.createElement('div');
     overlay.className = "fixed inset-0 bg-black/50 z-[90] flex items-center justify-center p-4";
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
                     <input type="email" id="destinatario" required multiple class="w-full px-4 py-2 border rounded-xl text-sm focus:outline-none focus:border-blue-500" placeholder="ejemplo@correo.com, contabilidad@correo.com">
                 </div>

                 <div>
                     <label for="asunto" class="block text-xs font-bold text-gray-500 uppercase mb-1">Asunto</label>
                     <input type="text" id="asunto" placeholder="Envío de Comprobante Fiscal - Folio ${folio}" required class="w-full px-4 py-2 border rounded-xl text-sm focus:outline-none focus:border-blue-500">
                 </div>

                 <div>
                     <label for="cuerpo" class="block text-xs font-bold text-gray-500 uppercase mb-1">Mensaje</label>
                     <textarea id="cuerpo" rows="3" placeholder="Adjuntamos el Comprobante Fiscal solicitado." class="w-full px-4 py-2 border rounded-xl text-sm focus:outline-none focus:border-blue-500"></textarea>
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
                   headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
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
