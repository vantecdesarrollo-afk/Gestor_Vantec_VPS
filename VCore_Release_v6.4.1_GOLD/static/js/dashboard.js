/**
 * dashboard.js - Lógica para poblar el Dashboard de Vantec con datos reales
 */

// SSoT de Filtros VCORE (Directiva CTO v34.0)
const currentFilters = {
    fecha_inicio: '',
    fecha_fin: '',
    searchTerm: '',
    moneda: 'ALL',
    concepto: ''
};

async function loadDashboardData() {
    const kpiTotalDocs = document.getElementById('kpi-total-docs');
    
    const filterMoneda = document.getElementById('filter-moneda');
    const filterConcepto = document.getElementById('filter-concepto');
    
    const moneda = currentFilters.moneda !== 'ALL' ? currentFilters.moneda : (filterMoneda ? filterMoneda.value : 'ALL');
    const concepto = currentFilters.concepto || (filterConcepto ? filterConcepto.value : '');
    const fecha_inicio = currentFilters.fecha_inicio;
    const fecha_fin = currentFilters.fecha_fin;

    const kpiTotalAmount = document.getElementById('kpi-total-amount');
    const kpiPpdPending = document.getElementById('kpi-ppd-pending');
    const kpiAlertsStatus = document.getElementById('kpi-alerts-status');
    const topClientesContainer = document.getElementById('top-clientes-container');

    const dashboardContent = document.getElementById('dashboard-content');
    const emptyState = document.getElementById('empty-state-container');
    const adminHint = document.getElementById('admin-hint');

    // 1. Verificar Contexto Global (STRIKE 3 Hardening)
    let activeEntidad = localStorage.getItem('active_entidad');

    // 1. Sincronizar Selección Visual (Prioridad Absoluta)
    const selector = document.getElementById('entity-selector');
    if (selector && selector.value && selector.value !== "") {
        if (selector.value !== activeEntidad) {
            console.log("[+] Sincronizando visual prioritaria con localStorage:", selector.value);
            activeEntidad = selector.value;
            localStorage.setItem('active_entidad', activeEntidad);
        }
    }

    const payload = getUserPayload();
    const isSuperAdmin = payload && payload.is_superadmin;

    if (!activeEntidad || activeEntidad === 'null' || activeEntidad === '' || activeEntidad === 'undefined') {
        if (!isSuperAdmin) {
            if (dashboardContent) dashboardContent.classList.add('hidden');
            if (emptyState) emptyState.classList.remove('hidden');
            return;
        }
        // Modo Neutral: SuperAdmin puede ver el dashboard global
        console.log("🛡️ [VCORE] Modo Neutral SuperAdmin detectado en Dashboard.");
    }

    // Si hay entidad, mostrar contenido y ocultar empty state
    if (dashboardContent) dashboardContent.classList.remove('hidden');
    if (emptyState) emptyState.classList.add('hidden');

    try {
        // 2. Mostrar estado de carga
        if (kpiTotalDocs) kpiTotalDocs.innerText = 'Cargando...';

        // 3. Petición autenticada a la API
        let url = '/api/v1/analytics/dashboard';
        const params = new URLSearchParams();
        if (fecha_inicio) params.append('fecha_inicio', fecha_inicio);
        if (fecha_fin) params.append('fecha_fin', fecha_fin);
        if (moneda && moneda !== 'ALL') params.append('moneda', moneda);
        if (concepto) params.append('concepto', concepto);
        if (params.toString()) {
            url += '?' + params.toString();
        }

        const data = await vantecFetch(url);

        // Populate Custom Dropdown BI (Marvel Test - Unified Search)
        const suggestionsContainer = document.getElementById('search-suggestions');
        if (data.conceptos_options && suggestionsContainer) {
            suggestionsContainer.innerHTML = '';
            data.conceptos_options.forEach(c => {
                const item = document.createElement('div');
                item.className = 'px-4 py-2 hover:bg-gray-50 cursor-pointer text-sm font-medium text-vantec-primary border-b border-gray-50 last:border-0 transition-colors';
                item.innerText = c;
                item.onclick = () => {
                    const input = document.getElementById('filter-concepto');
                    if (input) {
                        input.value = c;
                        currentFilters.concepto = c;
                        suggestionsContainer.classList.add('hidden');
                        loadDashboardData();
                    }
                };
                suggestionsContainer.appendChild(item);
            });
        }

        if (data.monedas_options) {
             const selectMoneda = document.getElementById('filter-moneda');
             if (selectMoneda && selectMoneda.options && selectMoneda.options.length <= 1) {
                  data.monedas_options.forEach(m => {
                       const opt = document.createElement('option');
                       opt.value = m;
                       opt.innerText = m;
                       selectMoneda.appendChild(opt);
                  });
             }
        }

        // Renderizar Gráfica BI
        if (data.facturacion_mensual) {
            renderMonthlyChart(data.facturacion_mensual);
        }

        // 3. Mapeo al DOM (Data Binding BI)
        const formatter = new Intl.NumberFormat('es-MX', {
            style: 'currency',
            currency: 'MXN',
        });

        if (document.getElementById('kpi-total-ingresos')) {
            document.getElementById('kpi-total-ingresos').innerText = formatter.format(data.total_ingresos || 0);
        }

        if (document.getElementById('kpi-total-egresos')) {
            document.getElementById('kpi-total-egresos').innerText = formatter.format(data.total_egresos || 0);
        }

        // Total de Documentos
        if (kpiTotalDocs) {
            const totalVal = parseInt(data.total_documentos);
            kpiTotalDocs.innerText = isNaN(totalVal) ? '0' : totalVal.toLocaleString();
        }

        // Renderizar Gráfica de Donas (Estatus de Envío)
        if (data.envio_stats) {
            renderSendDonutChart(data.envio_stats);
        }

        // Alerta de Cobranza (PPD)
        const cardPpd = document.getElementById('card-ppd');
        const iconWrapperPpd = document.getElementById('icon-wrapper-ppd');
        const iconPpd = document.getElementById('icon-ppd');
        
        if (kpiPpdPending) {
            const ppdVal = parseInt(data.ppd_pending_count || 0);
            kpiPpdPending.innerText = ppdVal.toString();
            
            if (ppdVal === 0) {
                if(cardPpd) cardPpd.className = 'bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow';
                if(iconWrapperPpd) iconWrapperPpd.className = 'p-3 bg-gray-50 text-gray-400 rounded-xl';
                if(iconPpd) iconPpd.className = 'fas fa-check-circle fa-lg text-green-500';
            } else {
                if(cardPpd) cardPpd.className = 'bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow border-l-4 border-l-orange-400';
                if(iconWrapperPpd) iconWrapperPpd.className = 'p-3 bg-orange-50 text-orange-600 rounded-xl';
                if(iconPpd) iconPpd.className = 'fas fa-exclamation-circle fa-lg';
            }
        }

        // Pagos Huérfanos (L6 Protocol)
        const kpiOrphans = document.getElementById('kpi-orphans-count');
        const cardOrphans = document.getElementById('card-orphans');
        const iconWrapperOrphans = document.getElementById('icon-wrapper-orphans');
        const iconOrphans = document.getElementById('icon-orphans');

        if (kpiOrphans) {
            const orphanCount = parseInt(data.orphans_count || 0);
            kpiOrphans.innerText = orphanCount.toString();

            if (orphanCount === 0) {
                 if(cardOrphans) cardOrphans.className = 'bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow';
                 if(iconWrapperOrphans) iconWrapperOrphans.className = 'p-3 bg-gray-50 text-gray-400 rounded-xl';
                 if(iconOrphans) iconOrphans.className = 'fas fa-ghost fa-lg text-gray-200';
            } else {
                 if(cardOrphans) cardOrphans.className = 'bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow border-l-4 border-l-red-500 bg-red-50/10 animate-pulse';
                 if(iconWrapperOrphans) iconWrapperOrphans.className = 'p-3 bg-red-50 text-red-600 rounded-xl';
                 if(iconOrphans) iconOrphans.className = 'fas fa-ghost fa-lg';
            }
        }

        // Restauración de Inteligencia de Negocio: Top 5 Clientes (Directiva v48.0)
        if (topClientesContainer) {
            topClientesContainer.innerHTML = '';
            if (data.top_clientes && data.top_clientes.length > 0) {
                data.top_clientes.forEach((c, idx) => {
                    const row = document.createElement('div');
                    row.className = 'flex items-center justify-between p-3 rounded-xl hover:bg-gray-50 transition-colors border border-transparent hover:border-gray-100';
                    row.innerHTML = `
                        <div class="flex items-center">
                            <span class="flex items-center justify-center w-8 h-8 rounded-lg ${idx === 0 ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-100 text-gray-500'} text-xs font-bold mr-4">
                                #${idx + 1}
                            </span>
                            <div>
                                <p class="text-sm font-bold text-vantec-primary">${c.cliente}</p>
                                <p class="text-[10px] text-gray-400 font-medium">Facturación Acumulada</p>
                            </div>
                        </div>
                        <div class="text-right">
                            <p class="text-sm font-black text-vantec-primary">${formatter.format(c.total)}</p>
                        </div>
                    `;
                    topClientesContainer.appendChild(row);
                });
            } else {
                topClientesContainer.innerHTML = `
                    <div class="flex flex-col items-center justify-center py-8 text-gray-400 italic">
                        <i class="fas fa-chart-line fa-2x mb-3 opacity-20"></i>
                        <p class="text-xs">Sin actividad comercial en este periodo</p>
                    </div>
                `;
            }
        }
    } catch (error) {
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
    }
}

/**
 * Renderiza la gráfica de donas para estatus de envío (BI - Sincronizado ApexCharts)
 */
function renderSendDonutChart(stats) {
    const ctx = document.getElementById('sendDonutChart');
    if (!ctx) return;
    
    ctx.innerHTML = ''; // Limpiar contenedor
    
    const options = {
        series: [Number(stats.exito || 0), Number(stats.pendiente || 0)],
        chart: {
            height: 250,
            type: 'donut',
        },
        labels: ['Éxito', 'Pendiente'],
        colors: ['#1E3A5F', '#4EBCE9'],
        dataLabels: { enabled: false },
        legend: {
            position: 'bottom',
            fontFamily: 'Inter, sans-serif',
            fontSize: '10px',
            fontWeight: 700,
            labels: { colors: '#64748B' }
        },
        plotOptions: {
            pie: {
                donut: {
                    size: '75%',
                    labels: {
                        show: true,
                        total: {
                            show: true,
                            label: 'TOTAL',
                            fontSize: '10px',
                            fontWeight: 900,
                            color: '#1E3A5F',
                            formatter: function (w) {
                                return w.globals.seriesTotals.reduce((a, b) => a + b, 0);
                            }
                        }
                    }
                }
            }
        },
        stroke: { show: false }
    };

    const chart = new ApexCharts(ctx, options);
    chart.render();
}

/**
 * Renderiza la gráfica de barras de Facturación Mensual
 */
function renderMonthlyChart(data) {
    const ctx = document.getElementById('monthlyChart');
    if (!ctx) return;
    
    ctx.innerHTML = ''; // Clear for ApexCharts

    const options = {
        series: [{
            name: 'Total Facturado (MXN)',
            data: data.map(item => Number(item.total) || 0)
        }],
        chart: {
            height: 320,
            type: 'area',
            toolbar: { show: false },
            zoom: { enabled: false }
        },
        colors: ['#1E3A5F'],
        stroke: { curve: 'smooth', width: 3 },
        fill: {
            type: 'gradient',
            gradient: {
                shadeIntensity: 1,
                opacityFrom: 0.6,
                opacityTo: 0.1,
                colorStops: [
                    { offset: 0, color: '#4EBCE9', opacity: 0.4 },
                    { offset: 100, color: '#FFFFFF', opacity: 0.1 }
                ]
            }
        },
        dataLabels: { enabled: false },
        xaxis: {
            categories: data.map(item => item.mes),
            axisBorder: { show: false },
            axisTicks: { show: false },
            labels: { style: { colors: '#64748B', fontWeight: 500 } }
        },
        yaxis: {
            labels: {
                style: { colors: '#64748B' },
                formatter: function (val) {
                    return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', maximumSignificantDigits: 3 }).format(Number(val) || 0);
                }
            }
        },
        grid: { borderColor: '#F1F5F9', strokeDashArray: 4 }
    };

    const chart = new ApexCharts(ctx, options);
    chart.render();
}

// Ejecutar al cargar el DOM
document.addEventListener('DOMContentLoaded', () => {
    const suggestionsContainer = document.getElementById('search-suggestions');
    loadDashboardData();

    // Se eliminan variables locales redundantes para usar currentFilters global

    // Listeners para Filtros BI (Selectores)
    const filterMonedaSelector = document.getElementById('filter-moneda');
    const filterConceptoInput = document.getElementById('filter-concepto');

    if (filterMonedaSelector) {
        filterMonedaSelector.addEventListener('change', () => {
            currentFilters.moneda = filterMonedaSelector.value || 'ALL';
            console.log("💎 [VCORE] Moneda seleccionada:", currentFilters.moneda);
            loadDashboardData();
        });
    }

    if (filterConceptoInput) {
        let conceptoTimeout;
        filterConceptoInput.addEventListener('input', (e) => {
            clearTimeout(conceptoTimeout);
            
            const val = e.target.value.trim();
            
            // Marvel Test: Show suggestions ONLY if typing >= 3 characters (Directiva v47.0)
            if (suggestionsContainer && val.length >= 3 && suggestionsContainer.children.length > 0) {
                suggestionsContainer.classList.remove('hidden');
            } else if (suggestionsContainer) {
                suggestionsContainer.classList.add('hidden');
            }

            // Optimización v47.0: Solo disparar búsqueda si val.length >= 3 o si se borró totalmente (reset)
            if (val.length >= 3 || val.length === 0) {
                conceptoTimeout = setTimeout(() => {
                    currentFilters.concepto = val;
                    console.log(`🔍 [VCORE] Live Search Concepto: ${currentFilters.concepto}`);
                    loadDashboardData();
                }, 300);
            }
        });
        
        filterConceptoInput.addEventListener('keypress', (e) => {
             if (e.key === 'Enter') {
                const val = filterConceptoInput.value.trim();
                if (val.length >= 3 || val.length === 0) {
                    clearTimeout(conceptoTimeout);
                    currentFilters.concepto = val;
                    if (suggestionsContainer) suggestionsContainer.classList.add('hidden');
                    loadDashboardData();
                }
             }
        });
    }

    // Atajos de Fecha Vantec (Accesos Rápidos)
    document.querySelectorAll('.preset-date').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const preset = e.currentTarget.getAttribute('data-preset');
            const today = new Date();
            let start = new Date();
            let end = new Date();

            if (preset === '7d') {
                start.setDate(today.getDate() - 7);
            } else if (preset === '15d') {
                start.setDate(today.getDate() - 15);
            } else if (preset === 'mes_actual') {
                start = new Date(today.getFullYear(), today.getMonth(), 1);
                end = new Date(today.getFullYear(), today.getMonth() + 1, 0);
            } else if (preset === 'mes_anterior') {
                start = new Date(today.getFullYear(), today.getMonth() - 1, 1);
                end = new Date(today.getFullYear(), today.getMonth(), 0);
            }

            const startStr = flatpickr.formatDate(start, "Y-m-d");
            const endStr = flatpickr.formatDate(end, "Y-m-d");

            const fpInstance = document.getElementById('date-range-picker')._flatpickr;
            if (fpInstance) {
                fpInstance.setDate([start, end]);
            }
            
            // Actualizar SSoT Global (Directiva CTO v34.0)
            currentFilters.fecha_inicio = startStr;
            currentFilters.fecha_fin = endStr;
            
            console.log(`[VCORE] Aplicando Preset: ${preset} (${startStr} - ${endStr})`);
            loadDashboardData();
        });
    });

    const fp = flatpickr("#date-range-picker", {
        mode: "range",
        dateFormat: "Y-m-d",
        locale: "es",
        onChange: function(selectedDates, dateStr, instance) {
            if (selectedDates.length === 2) {
                currentFilters.fecha_inicio = flatpickr.formatDate(selectedDates[0], "Y-m-d");
                currentFilters.fecha_fin = flatpickr.formatDate(selectedDates[1], "Y-m-d");
                loadDashboardData();
            } else if (selectedDates.length === 0) {
                currentFilters.fecha_inicio = '';
                currentFilters.fecha_fin = '';
                loadDashboardData();
            }
        }
    });
    
    // Handler para Limpiar Filtros (Trash Can) - Simplificado v37.0
    const btnReset = document.getElementById('btn-reset-filters');
    if (btnReset) {
        btnReset.onclick = (e) => {
            try {
                e.preventDefault();
                console.log('🔄 Ejecutando Reset Atómico...');
                
                // 1. Limpieza de interfaz visual
                const picker = document.getElementById('date-range-picker');
                if (picker && picker._flatpickr) {
                    picker._flatpickr.clear();
                }
                
                if (document.getElementById('filter-moneda')) document.getElementById('filter-moneda').value = '';
                if (document.getElementById('filter-concepto')) document.getElementById('filter-concepto').value = '';
                if (suggestionsContainer) suggestionsContainer.classList.add('hidden');
                
                // 2. Limpieza de SSoT (Global State)
                currentFilters.fecha_inicio = '';
                currentFilters.fecha_fin = '';
                currentFilters.searchTerm = '';
                currentFilters.moneda = 'ALL';
                currentFilters.concepto = '';
                
                // 3. Recarga AJAX instantánea ($5.2M)
                loadDashboardData();
            } catch (err) {
                console.error("Reset Error:", err);
            }
        };
    }

    // --- DASHBOARD ACTIONS (CTO v34.0 EXPORT SYSTEM) ---
    
    // Toggle para Dropdown de Exportación (Mejorado para Firefox/Safari)
    const btnExportDropdown = document.getElementById('btn-export-dropdown');
    const exportMenu = document.getElementById('export-menu');

    if (btnExportDropdown && exportMenu) {
        btnExportDropdown.onclick = (e) => {
            try {
                e.preventDefault();
                e.stopPropagation();
                exportMenu.classList.toggle('hidden');
                // Hardening Z-Index para Firefox
                exportMenu.style.zIndex = "9999";
            } catch (err) {
                console.warn("[VCORE] Export Toggle Fail:", err);
            }
        };

        // Cerrar al hacer clic fuera
        window.addEventListener('click', (e) => {
            try {
                if (!exportMenu.contains(e.target) && !btnExportDropdown.contains(e.target)) {
                    exportMenu.classList.add('hidden');
                }
            } catch (err) {}
        });
    }

    // Listener para el buscador personalizado (Marvel Test)
    if (filterConceptoInput && suggestionsContainer) {
        // Saneamiento v44.0: No desplegar al hacer click o posicionar (focus)
        // Se elimina el listener de 'focus' previo.
        
        // Cerrar sugerencias al hacer clic fuera
        document.addEventListener('click', (e) => {
            if (!filterConceptoInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
                suggestionsContainer.classList.add('hidden');
            }
        });
    }

    window.startExport = async (format) => {
        try {
            const queryParams = new URLSearchParams(currentFilters).toString();
            // Llamada al endpoint unificado en analytics.py (Directiva v53.0)
            const response = await fetch(`/api/v1/analytics/export?format=${format}&${queryParams}`, {
                headers: { 
                    'Authorization': `Bearer ${getToken()}`, 
                    'X-Entidad-ID': getActiveEntidad() 
                }
            });
    
            if (!response.ok) throw new Error('Fallo en la respuesta del servidor');
    
            // USAR BLOB DIRECTO PARA COMPATIBILIDAD TOTAL
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            
            const fileExt = format === 'xlsx' ? 'xlsx' : 'csv';
            // Nombre profesional (Directiva v53.0)
            a.download = `VCore_Audit_${new Date().toISOString().split('T')[0]}.${fileExt}`;
            
            document.body.appendChild(a);
            a.click();
    
            // --- FIX CRÍTICO PARA CHROME ---
            setTimeout(() => {
                window.URL.revokeObjectURL(url);
                if (document.body.contains(a)) {
                    document.body.removeChild(a);
                }
                console.log("Descarga procesada y memoria liberada.");
            }, 1000); 
    
            Swal.fire({
                icon: 'success',
                title: 'Exportación Exitosa',
                text: 'El archivo se ha enviado al gestor de descargas.',
                timer: 2000,
                showConfirmButton: false
            });
    
        } catch (err) {
            console.error('EXPORT_ERROR:', err);
            Swal.fire({ icon: 'error', title: 'Error', text: 'No se pudo completar la descarga en este navegador.' });
        }
    };

    const linkXlsx = document.getElementById('export-xlsx');
    const linkCsv = document.getElementById('export-csv');

    if (linkXlsx) linkXlsx.addEventListener('click', (e) => { e.preventDefault(); startExport('xlsx'); });
    if (linkCsv) linkCsv.addEventListener('click', (e) => { e.preventDefault(); startExport('csv'); });

}); // Fin DOMContentLoaded
