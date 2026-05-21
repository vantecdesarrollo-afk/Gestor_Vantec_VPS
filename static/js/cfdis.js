/**
 * cfdis.js - Lógica para el Explorador de Documentos Vantec
 * REPARADO: Conexión estricta a /api/v1/comprobantes/
 */

let allCfdis = [];
let currentPage = 1;
const pageSize = 50;

const formatCurrency = (amount) => {
    return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(amount);
};

let isLoadingCfdis = false;
async function loadCfdis() {
    if (isLoadingCfdis) return;
    isLoadingCfdis = true;
    const tableBody = document.getElementById('cfdiTableBody');
    const counter = document.getElementById('cfdiCounter');
    const pageIndicator = document.getElementById('pageIndicator');
    const btnPrev = document.getElementById('btnPrev');
    const btnNext = document.getElementById('btnNext');

    if (pageIndicator) pageIndicator.innerText = currentPage;

    // --- ACTIVACIÓN DE FILTROS AVANZADOS (CTO REGLA L4) ---
    const toggleBtn = document.getElementById('toggleFilters');
    const filtersPanel = document.getElementById('advanced-filters');
    if (toggleBtn && filtersPanel && !toggleBtn.dataset.listener) {
        toggleBtn.dataset.listener = "true";
        toggleBtn.addEventListener('click', () => {
             filtersPanel.classList.toggle('hidden');
             console.log("[CFDIS] Toggle Filtros Avanzados");
        });
    }

    let activeEntidad = localStorage.getItem('active_entidad');

    const selector = document.getElementById('entity-selector');
    if (selector && selector.value && selector.value !== "") {
        if (selector.value !== activeEntidad) {
            console.log("[CFDIS] Sincronizando visual prioritaria con localStorage:", selector.value);
            activeEntidad = selector.value;
            localStorage.setItem('active_entidad', activeEntidad);
        }
    }

    // 1. Verificar Contexto (Soporte Modo Neutral para SuperAdmin)
    const payload = getUserPayload();
    const isSuperAdmin = payload && payload.is_superadmin;
    
    if (!activeEntidad || activeEntidad === 'null' || activeEntidad === '' || activeEntidad === 'undefined') {
        if (!isSuperAdmin) {
            if (tableBody) {
                tableBody.innerHTML = `<tr><td colspan="11" class="px-6 py-12 text-center text-orange-400 font-bold"><i class="fas fa-exclamation-triangle mr-2"></i> ERROR: Seleccione una empresa en el menú superior para activar la vista.</td></tr>`;
            }
            return;
        }
        // Modo Neutral: SuperAdmin puede ver todo sin entidad
        console.log("🛡️ [VCORE] Modo Neutral SuperAdmin detectado en Emisión.");
    }

    try {
        const searchTerm = document.getElementById('cfdiSearch')?.value || '';
        const tipoFilter = document.getElementById('filterType')?.value || document.getElementById('tipoFilter')?.value || '';
        let fechaDesde = document.getElementById('filterDateStart')?.value || '';
        let fechaHasta = document.getElementById('filterDateEnd')?.value || '';

        if (searchTerm.includes('7227') || searchTerm.length >= 4) {
            fechaDesde = '';
            fechaHasta = '';
            console.log("[VCORE] Buscador Profundo Activado. Ignorando rango de fechas.");
        }

        // L6 v6.2: Filtros de Rango y Serie (Server-Side)
        const serie = document.getElementById('filterSerie')?.value || '';
        const folioStart = document.getElementById('filterFolioStart')?.value || '';
        const folioEnd = document.getElementById('filterFolioEnd')?.value || '';

        const offset = (currentPage - 1) * pageSize;
        let url = `/api/v1/comprobantes/?offset=${offset}&limit=${pageSize}&search=${encodeURIComponent(searchTerm)}`;
        if (tipoFilter) url += `&tipo=${tipoFilter}`;
        if (fechaDesde) url += `&fecha_desde=${fechaDesde}`;
        if (fechaHasta) url += `&fecha_hasta=${fechaHasta}`;
        if (serie) url += `&serie=${encodeURIComponent(serie)}`;
        if (folioStart) url += `&folio_desde=${folioStart}`;
        if (folioEnd) url += `&folio_hasta=${folioEnd}`;
        url += `&t=${Date.now()}`;
        
        const data = await vantecFetch(url);

        console.log(`[VANTEC AUDIT] Respuesta del Servidor:`, data);
        allCfdis = data && data.resultados ? data.resultados : (Array.isArray(data) ? data : []);

        const total = data && data.total_registros_bd !== undefined ? data.total_registros_bd : allCfdis.length;

        populateHeaderFilters(allCfdis);
        renderTable(allCfdis, total);

        if (counter) {
            const start = total === 0 ? 0 : offset + 1;
            const end = Math.min(offset + pageSize, total);
            counter.innerText = `Mostrando ${start} - ${end} de ${total} resultados`;

            // --- RECONSTRUCCIÓN DE PAGINADOR NUMERADO (PROMPT MAESTRO) ---
            const container = document.getElementById('pageIndicator');
            if (container) {
                container.innerHTML = ''; // Limpiar
                const totalPages = Math.ceil(total / pageSize);
                
                // Mostrar un rango inteligente de páginas (Ej: 1, 2, 3 ... N)
                const maxVisible = 5;
                let startPage = Math.max(1, currentPage - 2);
                let endPage = Math.min(totalPages, startPage + maxVisible - 1);
                if (endPage - startPage < maxVisible - 1) {
                    startPage = Math.max(1, endPage - maxVisible + 1);
                }

                if (startPage > 1) {
                    container.innerHTML += `<button onclick="goToPage(1)" class="px-2 py-1 bg-white border border-gray-200 rounded text-gray-500 hover:bg-gray-100">1</button>`;
                    if (startPage > 2) container.innerHTML += `<span class="px-1 text-gray-400">...</span>`;
                }

                for (let i = startPage; i <= endPage; i++) {
                    const isActive = i === currentPage;
                    container.innerHTML += `
                        <button onclick="goToPage(${i})" 
                            class="px-2 py-1 rounded text-xs font-bold transition-all ${isActive ? 'bg-vantec-primary text-white shadow' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-100'}">
                            ${i}
                        </button>
                    `;
                }

                if (endPage < totalPages) {
                    if (endPage < totalPages - 1) container.innerHTML += `<span class="px-1 text-gray-400">...</span>`;
                    container.innerHTML += `<button onclick="goToPage(${totalPages})" class="px-2 py-1 bg-white border border-gray-200 rounded text-gray-500 hover:bg-gray-100">${totalPages}</button>`;
                }
            }

            if (btnPrev) btnPrev.disabled = currentPage === 1;
            if (btnNext) btnNext.disabled = end >= total;
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

window.goToPage = function(page) {
    currentPage = page;
    loadCfdis();
};

window.nextPage = function() {
    currentPage++;
    loadCfdis();
};

window.prevPage = function() {
    if (currentPage > 1) {
        currentPage--;
        loadCfdis();
    }
};

function renderTable(data, total = 0) {
    const tableBody = document.getElementById('cfdiTableBody');
    if (!tableBody) return;

    tableBody.innerHTML = '';

    if (data.length === 0) {
        if (total > 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="11" class="px-6 py-16 text-center">
                        <div class="flex flex-col items-center justify-center space-y-3">
                            <p class="text-vantec-primary font-bold text-lg">Página sin resultados</p>
                            <p class="text-gray-400 text-xs">No hay registros en esta página, intenta regresar al inicio.</p>
                            <button onclick="goToPage(1)" class="mt-4 px-4 py-2 bg-[#4EBCE9] text-white rounded-lg font-bold text-xs"><i class="fas fa-arrow-left mr-2"></i> Ir a la primera página</button>
                        </div>
                    </td>
                </tr>`;
        } else {
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
        }
        return;
    }

    data.forEach(cfdi => {
        const fragment = createCfdiRow(cfdi);
        tableBody.appendChild(fragment);
    });
}

window.showPdfMenu = function(event, uuid, files) {
    event.stopPropagation();
    
    // Eliminar cualquier menú previo
    const existing = document.getElementById('pdf-dropdown-active');
    if (existing) existing.remove();

    const menu = document.createElement('div');
    menu.id = 'pdf-dropdown-active';
    menu.className = 'absolute right-0 mt-2 w-72 bg-white rounded-xl shadow-2xl border border-gray-100 py-2 z-[100] animate-in fade-in slide-in-from-top-2 duration-200';
    menu.style.borderTop = '4px solid #1E3A5F';

    let html = `
        <div class="px-4 py-3 border-b border-gray-50 mb-1 flex items-center justify-between">
            <span class="text-[10px] font-black text-gray-400 border-l-2 border-[#1E3A5F] pl-2 uppercase tracking-widest">Documentos Adjuntos</span>
            <button onclick="document.getElementById('pdf-dropdown-active').remove();" class="text-gray-300 hover:text-red-500 transition-colors px-1">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;

    files.forEach((file, index) => {
        html += `
            <button onclick="downloadCfdi('${uuid}', 'pdf', ${index}); document.getElementById('pdf-dropdown-active').remove();" 
                    class="w-full text-left px-4 py-3 text-[11px] font-bold text-[#1E3A5F] hover:bg-gray-50 flex items-center group transition-all">
                <div class="w-8 h-8 rounded-lg bg-red-50 flex items-center justify-center mr-3 group-hover:bg-red-100 transition-colors">
                    <i class="fas fa-file-pdf text-red-500 group-hover:scale-110 transition-transform"></i>
                </div>
                <span class="truncate flex-grow">${file}</span>
                <i class="fas fa-download ml-2 text-gray-300 group-hover:text-[#4EBCE9] transition-colors"></i>
            </button>
        `;
    });

    menu.innerHTML = html;
    
    // Posicionamiento dinámico (fijo respecto al viewport)
    const rect = event.currentTarget.getBoundingClientRect();
    document.body.appendChild(menu);
    menu.style.position = 'fixed';
    menu.style.top = `${rect.bottom + 8}px`;
    menu.style.left = `${rect.right - 288}px`;

    // Cerrar al hacer click fuera o ESC
    const closeMenu = (e) => {
        if (e.type === 'keydown' && e.key === 'Escape') {
            menu.remove();
            cleanup();
        } else if (e.type === 'click' && !menu.contains(e.target) && !event.currentTarget.contains(e.target)) {
            menu.remove();
            cleanup();
        }
    };

    const cleanup = () => {
        document.removeEventListener('click', closeMenu);
        document.removeEventListener('keydown', closeMenu);
    };

    setTimeout(() => {
        document.addEventListener('click', closeMenu);
        document.addEventListener('keydown', closeMenu);
    }, 10);
};

function createCfdiRow(cfdi) {
    if (!cfdi) return document.createDocumentFragment();

    const tr = document.createElement('tr');
    tr.className = 'hover:bg-gray-50/50 transition-colors border-b border-gray-100';

    const serie = cfdi.serie || '';
    const folioStr = cfdi.folio !== null && cfdi.folio !== undefined ? String(cfdi.folio) : '';
    const cleanFolio = folioStr && folioStr !== 'S/N' ? folioStr.replace(/^0+/, '') || '0' : 'S/N';
    const serieFolio = (serie && cleanFolio !== 'S/N') ? `${serie}-${cleanFolio}` : cleanFolio;
    const fechaStr = cfdi.fecha || '---';
    const total = parseFloat(cfdi.total || 0);

    const pdf_exists = cfdi.pdf_exists === true || cfdi.pdf_exists === 'true';
    const xml_exists = cfdi.xml_exists === true || cfdi.xml_exists === 'true';
    const hasReps = cfdi.tiene_relacionados === true;

    let metodoHtml = cfdi.metodo_pago || '---';

    let tipoBg = 'bg-blue-50'; let tipoColor = 'text-[#1E3A5F]'; let tipoLabel = 'Ingreso';
    if (cfdi.tipo === 'P') { 
        tipoBg = 'bg-green-50'; tipoColor = 'text-green-600'; tipoLabel = 'Pago'; 
        if (cfdi.orphan_payment === true) {
             tipoLabel += ` <i class="fas fa-ghost text-red-500 animate-pulse" title="Pago Huérfano: No se encontró Factura de Ingreso relacionada en SSoT"></i>`;
        }
    }
    else if (cfdi.tipo === 'E') { tipoBg = 'bg-red-50'; tipoColor = 'text-red-600'; tipoLabel = 'Egreso'; }
    else if (cfdi.tipo === 'N') { tipoBg = 'bg-purple-50'; tipoColor = 'text-purple-600'; tipoLabel = 'Nómina'; }
    else if (cfdi.tipo === 'T') { tipoBg = 'bg-gray-50'; tipoColor = 'text-gray-600'; tipoLabel = 'Traslado'; }

    const linkIcon = hasReps ? `<button onclick="mostrarModalRelaciones('${cfdi.uuid}')" class="text-green-500 hover:text-green-600" title="Ver Asociaciones"><i class="fas fa-link fa-lg"></i></button>` : '';

    // RBAC: Visor no puede enviar correos
    const payload = getUserPayload();
    const activeEntidad = localStorage.getItem('active_entidad');
    const activeEntidadData = payload && payload.entidades ? payload.entidades.find(e => e.id === activeEntidad) : null;
    const currentRole = activeEntidadData ? activeEntidadData.rol : (payload && payload.is_superadmin ? 'ADMIN' : 'VISOR');
    const reenvioBtn = currentRole !== 'VISOR' ? `<button onclick="abrirModalReenvio('${cleanFolio}', '${cfdi.uuid}', '${cfdi.rfc_receptor}', '${cfdi.serie || ''}')" class="text-gray-400 hover:text-[#1E3A5F]" title="Reenviar Correo"><i class="fas fa-envelope fa-lg"></i></button>` : '';

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
            ${(function() {
                let color = '#94A3B8'; let bg = 'rgba(148, 163, 184, 0.1)'; let label = cfdi.estatus || '---'; let icon = 'fa-info-circle';
                if (cfdi.estatus === 'Vigente' || cfdi.estatus === 'Pagado') { color = '#27AE60'; bg = 'rgba(39, 174, 96, 0.1)'; label = 'Pagado'; icon = 'fa-check-circle'; }
                else if (cfdi.estatus === 'Pendiente') { color = '#E74C3C'; bg = 'rgba(231, 76, 60, 0.1)'; label = 'Pendiente'; icon = 'fa-exclamation-circle'; }
                else if (cfdi.estatus === 'Parcial') { color = '#F39C12'; bg = 'rgba(243, 156, 18, 0.1)'; label = 'Parcial'; icon = 'fa-hourglass-half'; }
                else if (cfdi.estatus === 'Cancelado') { color = '#94A3B8'; bg = 'rgba(148, 163, 184, 0.1)'; label = 'Cancelado'; icon = 'fa-times-circle'; }
                else if (cfdi.estatus === 'AUSENTE' || cfdi.estatus === 'INGRESO AUSENTE' || cfdi.orphan_payment === true) { 
                    color = '#E74C3C'; bg = 'rgba(231, 76, 60, 0.1)'; label = 'AUSENTE'; icon = 'fa-ghost fa-ghost-red'; 
                }
                
                const isOrphan = cfdi.orphan_payment === true || cfdi.estatus === 'AUSENTE';
                let ghost = isOrphan ? `<i class="fas fa-ghost text-[#E74C3C] ml-1 animate-ghost-pulse" title="Pago Huérfano: El documento pagado no existe en el sistema."></i>` : '';
                return `<span class="px-2 py-1 rounded-full text-[10px] font-black flex items-center justify-center whitespace-nowrap" style="background-color: ${bg}; color: ${color}; border: 1px solid ${color}44;">
                    <i class="fas ${icon} mr-1"></i>${label}${ghost}
                </span>`;
            })()}
        </td>
        <td class="px-4 py-4 text-right">
            <div class="flex items-center justify-end space-x-3">
                <button onclick="openDetailDrawer('${cfdi.uuid}')" class="text-gray-400 hover:text-[#1E3A5F]" title="Ver Detalles"><i class="fas fa-search-plus fa-lg"></i></button>
                ${linkIcon}
                ${reenvioBtn}
                <button onclick="downloadCfdi('${cfdi.uuid}', 'xml')" class="${xml_exists ? 'text-[#4EBCE9]' : 'text-gray-400'}" title="Descargar XML"><i class="fas fa-file-code fa-lg"></i></button>
                <div class="relative inline-block">
                    <button id="pdf-btn-${cfdi.uuid}" 
                            onclick="${(cfdi.pdf_count > 1) ? `showPdfMenu(event, '${cfdi.uuid}', ${JSON.stringify(cfdi.pdf_files || []).replace(/"/g, '&quot;')})` : `downloadCfdi('${cfdi.uuid}', 'pdf')`}" 
                            class="${pdf_exists ? 'text-red-500 hover:text-red-700' : 'text-gray-300 cursor-not-allowed'} flex items-center transition-transform" 
                            title="Descargar PDF">
                        <i class="fas fa-file-pdf fa-lg"></i>
                        ${(cfdi.pdf_count > 1) ? `<span class="ml-1 text-[10px] font-black text-red-600">[${cfdi.pdf_count}]</span>` : ''}
                    </button>
                </div>

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
    if (tipoSelect) {
        tipoSelect.onchange = () => {
            currentPage = 1;
            loadCfdis();
        };
    }
    if (estadoSelect) estadoSelect.onchange = applyFilters;
    if (metodoSelect) metodoSelect.onchange = applyFilters;
    if (formaSelect) formaSelect.onchange = applyFilters;
}

window.applyFilters = function() {
    // L6 v6.2: Redirección a Carga Total (Deep Search) si hay filtros de servidor
    const hasServerFilters = document.getElementById('filterDateStart')?.value || 
                             document.getElementById('filterDateEnd')?.value || 
                             document.getElementById('filterType')?.value ||
                             document.getElementById('tipoFilter')?.value ||
                             document.getElementById('filterSerie')?.value ||
                             document.getElementById('filterFolioStart')?.value ||
                             document.getElementById('filterFolioEnd')?.value;

    if (hasServerFilters) {
        currentPage = 1;
        loadCfdis();
        return;
    }

    let filtered = [...allCfdis];

    const serie = document.getElementById('filterSerie')?.value.trim().toUpperCase();
    const folioStart = parseInt(document.getElementById('filterFolioStart')?.value);
    const folioEnd = parseInt(document.getElementById('filterFolioEnd')?.value);
    const filterType = document.getElementById('filterType')?.value;

    if (serie) {
        filtered = filtered.filter(c => (c.serie || '').toUpperCase() === serie);
    }

    if (!isNaN(folioStart) || !isNaN(folioEnd)) {
        filtered = filtered.filter(c => {
            const f = parseInt(c.folio);
            if (isNaN(f)) return false; // Si hay filtro numérico, ocultar los S/N
            
            let match = true;
            if (!isNaN(folioStart)) match = match && f >= folioStart;
            if (!isNaN(folioEnd)) match = match && f <= folioEnd;
            return match;
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

window.limpiarBusquedaGlobal = function() {
    const searchInput = document.getElementById('cfdiSearch');
    if (searchInput) {
        searchInput.value = '';
    }
    currentPage = 1;
    loadCfdis(); 
};

window.resetFilters = function() {
    if (document.getElementById('cfdiSearch')) document.getElementById('cfdiSearch').value = '';
    if (document.getElementById('filterSerie')) document.getElementById('filterSerie').value = '';
    if (document.getElementById('filterFolioStart')) document.getElementById('filterFolioStart').value = '';
    if (document.getElementById('filterFolioEnd')) document.getElementById('filterFolioEnd').value = '';
    if (document.getElementById('filterType')) document.getElementById('filterType').value = '';
    if (document.getElementById('filterDateStart')) document.getElementById('filterDateStart').value = '';
    if (document.getElementById('filterDateEnd')) document.getElementById('filterDateEnd').value = '';
    
    if (document.getElementById('receptorFilter')) document.getElementById('receptorFilter').value = '';
    if (document.getElementById('tipoFilter')) document.getElementById('tipoFilter').value = '';
    if (document.getElementById('estadoFilter')) document.getElementById('estadoFilter').value = '';
    if (document.getElementById('metodoFilter')) document.getElementById('metodoFilter').value = '';
    if (document.getElementById('formaFilter')) document.getElementById('formaFilter').value = '';

    currentPage = 1;
    loadCfdis(); // Recarga estado base desde el servidor
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

        const folioStr = cfdi.folio !== null && cfdi.folio !== undefined ? String(cfdi.folio) : '';
        const cleanFolio = folioStr && folioStr !== 'S/N' ? folioStr.replace(/^0+/, '') || '0' : 'S/N';

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
                        <span class="text-gray-400 font-medium">Conceptos / Conceptos Relacionados:</span>
                        <div class="mt-2 space-y-2">
                            ${(cfdi.conceptos || []).map(c => `
                                <div class="p-2 bg-white border border-gray-100 rounded-lg flex justify-between items-center space-x-2">
                                    <p class="font-semibold text-[#1E3A5F] break-words flex-1 text-wrap text-start">${c.descripcion}</p>
                                    <span class="font-bold text-vantec-accent text-right whitespace-nowrap">${formatCurrency(c.importe)}</span>
                                </div>
                            `).join('') || `<p class="font-semibold text-[#1E3A5F] mt-0.5">${cfdi.descripcion_concepto || 'Sin descripción'}</p>`}
                        </div>
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
            btnShare.onclick = () => abrirModalReenvio(cfdi.folio || 'S/N', cfdi.uuid, cfdi.rfc_receptor || '', cfdi.serie || '');
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
window.downloadCfdi = async function(uuid, type, index = 0) {
    const activeEntidad = localStorage.getItem('active_entidad');
    const token = localStorage.getItem('token'); 

    if (!token) {
        alert("Sesión no válida o expirada.");
        return;
    }

    try {
        const cacheBust = `&_v=${Date.now()}`;
        const indexParam = type === 'pdf' ? `&index=${index}` : '';
        const response = await fetch(`/api/v1/comprobantes/${uuid}/${type}?entidad_id=${activeEntidad}${indexParam}${cacheBust}`, {
            headers: { 
                'Authorization': `Bearer ${token}`,
                'X-Entidad-ID': activeEntidad === null ? "" : activeEntidad
            }
        });

        if (response.ok) {
            const disposition = response.headers.get('Content-Disposition');
            let filename = `${uuid}.${type}`;
            if (disposition && disposition.indexOf('filename=') !== -1) {
                filename = disposition.split('filename=')[1].replace(/"/g, '');
            }
            const blob = await response.blob();
            console.log(`🛡️ [VANTEC DEBUG] Blob recibido para ${filename}. Tamaño: ${blob.size} bytes`);
            
            if (blob.size === 0) {
                console.error("🛡️ [VANTEC DEBUG] El Blob está vacío.");
                alert("Error: El servidor entregó un archivo vacío.");
                return;
            }

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            
            // Standard Production Practice: Esconder el elemento para no interrumpir el DOM
            a.style.display = 'none';
            a.href = url;
            a.download = filename;
            
            // Inyectar, Cargar e Invocar Diálogo OS
            console.log(`🛡️ [VANTEC DEBUG] Disparando clic de descarga para ${filename}`);
            document.body.appendChild(a);
            a.click();
            
            // W3C: Diferir la destrucción del Blob URL (Asíncrono Mac/Windows)
            setTimeout(() => {
                try {
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                    console.log(`🛡️ [VANTEC DEBUG] Limpieza de Blob completada para ${filename}`);
                } catch (e) {
                    console.warn("L6 UI WARNING: DOM cleanup of Blob anchor failed", e);
                }
            }, 2000); // Aumentado a 2s para mayor seguridad en sistemas lentos
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

document.addEventListener('DOMContentLoaded', () => {
    loadCfdis();
    
    // Vinculación de Búsqueda Global (Server-Side)
    const searchInput = document.getElementById('cfdiSearch');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                console.log("[VANTEC] Iniciando Búsqueda Global:", searchInput.value);
                currentPage = 1;
                loadCfdis();
            }
        });
        
        // Opcional: Búsqueda dinámica con debounce
        let searchTimeout;
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (searchInput.value.length >= 3 || searchInput.value.length === 0) {
                    currentPage = 1;
                    loadCfdis();
                }
            }, 600);
        });
    }
});

window.mostrarModalRelaciones = function(uuid) {
    const cfdi = allCfdis.find(c => c.uuid === uuid);
    if (!cfdi || !cfdi.reps_asociados) return;

    // RBAC: Visor no puede enviar correos
    const payload = getUserPayload();
    const activeEntidad = localStorage.getItem('active_entidad');
    const activeEntidadData = payload && payload.entidades ? payload.entidades.find(e => e.id === activeEntidad) : null;
    const currentRole = activeEntidadData ? activeEntidadData.rol : (payload && payload.is_superadmin ? 'ADMIN' : 'VISOR');

    const overlay = document.createElement('div');
    overlay.className = "fixed inset-0 bg-black/50 z-[80] flex items-center justify-center p-4 cursor-pointer";
    overlay.id = "modalRelacionesDynamic";
    
    // Anti-Freeze v12.0: Clic afuera para cerrar
    overlay.onclick = (e) => {
        if (e.target.id === 'modalRelacionesDynamic') {
            overlay.remove();
            document.removeEventListener('keydown', _escHandlerRelaciones);
        }
    };

    // Anti-Freeze v12.0: ESC para cerrar
    const _escHandlerRelaciones = (e) => {
        if (e.key === 'Escape') {
            const el = document.getElementById('modalRelacionesDynamic');
            if (el) el.remove();
            document.removeEventListener('keydown', _escHandlerRelaciones);
        }
    };
    document.addEventListener('keydown', _escHandlerRelaciones);

    let rowsHtml = "";
    cfdi.reps_asociados.forEach(r => {
        const rFolioStr = r.folio !== null && r.folio !== undefined ? String(r.folio) : '';
        const cleanRRepFolio = rFolioStr && rFolioStr !== 'S/N' ? rFolioStr.replace(/^0+/, '') || '0' : 'S/N';
        const reenvioBtnRel = currentRole !== 'VISOR' ? `<button onclick="abrirModalReenvio('${r.folio || 'S/N'}', '${r.uuid}', '${r.rfc_receptor || ''}', '${r.serie || ''}')" class="text-gray-400 hover:text-[#1E3A5F]" title="Reenviar"><i class="fas fa-envelope fa-lg"></i></button>` : '';
        rowsHtml += `
            <tr class="border-b border-gray-100 hover:bg-gray-50">
                <td class="px-4 py-3 font-bold text-[#1E3A5F]">${r.tipo_documento || 'Pago'} ${cleanRRepFolio}</td>
                <td class="px-4 py-3 font-mono text-xs text-gray-500">${r.uuid.substring(0,8)}...</td>
                <td class="px-4 py-3 text-right font-black text-green-600">${formatCurrency(r.monto)}</td>
                <td class="px-4 py-3 text-right">
                    <div class="flex items-center justify-end space-x-3">
                        <button onclick="openDetailDrawer('${r.uuid}')" class="text-gray-400 hover:text-[#1E3A5F]" title="Ver Detalles"><i class="fas fa-search-plus fa-lg"></i></button>
                        <button onclick="downloadCfdi('${r.uuid}', 'xml')" class="text-[#4EBCE9] hover:text-[#1E3A5F]" title="Descargar XML"><i class="fas fa-file-code fa-lg"></i></button>
                        <button id="pdf-btn-${r.uuid}"
                                onclick="${(r.pdf_count > 1) ? `showPdfMenu(event, '${r.uuid}', ${JSON.stringify(r.pdf_files || []).replace(/"/g, '&quot;')})` : `downloadCfdi('${r.uuid}', 'pdf')`}" 
                                class="${r.pdf_exists === true ? 'text-red-500 hover:text-red-700' : 'text-gray-300 cursor-not-allowed'} flex items-center transition-transform" 
                                title="Descargar PDF">
                            <i class="fas fa-file-pdf fa-lg"></i>
                            ${r.pdf_count > 1 ? `<span class="ml-1 text-[10px] font-black text-red-600">[${r.pdf_count}]</span>` : ''}
                        </button>
                        ${reenvioBtnRel}
                    </div>
                </td>
            </tr>
        `;
    });

    overlay.innerHTML = `
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-xl p-6 transform transition-all">
            <div class="flex items-center justify-between border-b pb-4">
                <div class="flex items-center space-x-4">
                    <h3 class="font-black text-lg text-[#1E3A5F]"><i class="fas fa-link mr-2 text-green-500"></i> Documentos Asociados</h3>
                    <button onclick="loadCfdis(); var m = document.getElementById('modalRelacionesDynamic'); if(m) m.remove();" 
                            class="px-3 py-1 bg-gray-100 hover:bg-[#4EBCE9] hover:text-white text-[#1E3A5F] rounded-lg text-[10px] font-black transition-all uppercase tracking-tighter">
                        <i class="fas fa-sync-alt mr-1"></i> Actualizar
                    </button>
                </div>
                <button onclick="var m = document.getElementById('modalRelacionesDynamic'); if(m) m.remove();" class="text-gray-400 hover:text-red-500"><i class="fas fa-times fa-lg"></i></button>
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
     const overlay = document.createElement('div');
     overlay.className = "fixed inset-0 bg-black/50 z-[90] flex items-center justify-center p-4 cursor-pointer";
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
                     <input type="email" id="destinatario" required multiple class="w-full px-4 py-2 border rounded-xl text-sm focus:outline-none focus:border-blue-500" placeholder="ejemplo@correo.com">
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
                    headers: { 
                        'Content-Type': 'application/json', 
                        'Authorization': `Bearer ${localStorage.getItem('token')}`,
                        'X-Entidad-ID': localStorage.getItem('active_entidad') || ""
                    },
                    body: JSON.stringify(payload)
               });

              if (response.ok) {
                   alert("✅ Enviado exitosamente.");
                   overlay.remove();
              } else {
                   alert("❌ Error al enviar.");
              }
         } catch (error) {
              alert("❌ Error de red.");
         } finally {
              btn.disabled = false;
              btn.innerHTML = `<i class="fas fa-paper-plane"></i> <span>Enviar Correo</span>`;
         }
    });
};
