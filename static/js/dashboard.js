/**
 * dashboard.js - Lógica para poblar el Dashboard de Vantec con datos reales
 */

async function loadDashboardData(startDate = null, endDate = null) {
    const kpiTotalDocs = document.getElementById('kpi-total-docs');

    // Advanced Filters
    const filterMoneda = document.getElementById('filter-moneda');
    const filterConcepto = document.getElementById('filter-concepto');
    const moneda = filterMoneda ? filterMoneda.value : null;
    const concepto = filterConcepto ? filterConcepto.value : null;

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

    if (!activeEntidad || activeEntidad === 'null' || activeEntidad === '' || activeEntidad === 'undefined') {
        if (dashboardContent) dashboardContent.classList.add('hidden');
        if (emptyState) emptyState.classList.remove('hidden');

        // Mostrar hint adicional si es SuperAdmin
        const payload = getUserPayload();
        if (payload && payload.is_superadmin && adminHint) {
            adminHint.classList.remove('hidden');
        }
        return;
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
        if (startDate) params.append('fecha_inicio', startDate);
        if (endDate) params.append('fecha_fin', endDate);
        if (moneda) params.append('moneda', moneda);
        if (concepto) params.append('concepto', concepto);
        if (params.toString()) {
            url += '?' + params.toString();
        }

        const data = await vantecFetch(url);

        // Populate Conceptos Drowpdown once
        if (data.conceptos_options) {
             const selectConcepto = document.getElementById('filter-concepto');
             if (selectConcepto && selectConcepto.options.length <= 1) {
                  data.conceptos_options.forEach(c => {
                       const opt = document.createElement('option');
                       opt.value = c;
                       opt.innerText = c.substring(0, 50) + (c.length > 50 ? '...' : '');
                       selectConcepto.appendChild(opt);
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
                if(kpiAlertsStatus) kpiAlertsStatus.classList.add('hidden');
            } else {
                if(cardPpd) cardPpd.className = 'bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow border-l-4 border-l-red-500';
                if(iconWrapperPpd) iconWrapperPpd.className = 'p-3 bg-red-50 text-red-600 rounded-xl';
                if(iconPpd) iconPpd.className = 'fas fa-exclamation-circle fa-lg';
                if(kpiAlertsStatus) kpiAlertsStatus.classList.remove('hidden');
            }
        }

        // Top 5 Clientes
        if (topClientesContainer) {
            topClientesContainer.innerHTML = ''; // Limpiar cargador

            const clientes = data.top_clientes || [];
            if (clientes.length === 0) {
                topClientesContainer.innerHTML = `
                    <div class="flex items-center justify-center pt-8 text-gray-400">
                        <i class="fas fa-info-circle mr-2"></i> Sin datos suficientes
                    </div>
                `;
            } else {
                clientes.forEach(cliente => {
                    const row = document.createElement('div');
                    row.className = 'flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors';

                    row.innerHTML = `
                        <div class="flex items-center space-x-4">
                            <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center text-vantec-accent">
                                <i class="fas fa-user-tie"></i>
                            </div>
                            <div>
                                <p class="text-sm font-bold text-vantec-primary">${cliente.rfc_receptor}</p>
                                <p class="text-xs text-gray-500">Cliente Principal</p>
                            </div>
                        </div>
                        <p class="text-sm font-bold text-vantec-primary">${formatter.format(cliente.total_monto)}</p>
                    `;
                    topClientesContainer.appendChild(row);
                });
            }
        }

    } catch (error) {
        console.error('🛡️ VANTEC DASHBOARD ERROR:', error);
        if (kpiTotalDocs) kpiTotalDocs.innerText = '0';
        if (topClientesContainer) {
            topClientesContainer.innerHTML = `
                <div class="flex items-center justify-center pt-8 text-gray-400">
                    <i class="fas fa-info-circle mr-2"></i> Error al cargar datos
                </div>
            `;
        }
    }
}

/**
 * Renderiza la gráfica de donas para estatus de envío (BI)
 */
function renderSendDonutChart(stats) {
    const ctx = document.getElementById('sendDonutChart');
    if (!ctx) return;

    const existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Éxito', 'Pendiente'],
            datasets: [{
                data: [stats.exito, stats.pendiente],
                backgroundColor: ['#1E3A5F', '#4EBCE9'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            cutout: '70%'
        }
    });
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
            data: data.map(item => item.total)
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
                    return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', maximumSignificantDigits: 3 }).format(val);
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
    loadDashboardData();

    // Inicializar Flatpickr
    let currentStartDate = null;
    let currentEndDate = null;

    // Listeners para Filtros BI
    const filterMoneda = document.getElementById('filter-moneda');
    const filterConcepto = document.getElementById('filter-concepto');
    
    if (filterMoneda) {
        filterMoneda.addEventListener('change', () => {
            const fpInstance = document.getElementById('date-range-picker')._flatpickr;
            loadDashboardData(
                fpInstance && fpInstance.selectedDates.length === 2 ? flatpickr.formatDate(fpInstance.selectedDates[0], "Y-m-d") : null,
                fpInstance && fpInstance.selectedDates.length === 2 ? flatpickr.formatDate(fpInstance.selectedDates[1], "Y-m-d") : null
            );
        });
    }
    
    if (filterConcepto) {
        filterConcepto.addEventListener('change', () => {
            const fpInstance = document.getElementById('date-range-picker')._flatpickr;
            loadDashboardData(
                fpInstance && fpInstance.selectedDates.length === 2 ? flatpickr.formatDate(fpInstance.selectedDates[0], "Y-m-d") : null,
                fpInstance && fpInstance.selectedDates.length === 2 ? flatpickr.formatDate(fpInstance.selectedDates[1], "Y-m-d") : null
            );
        });
    }

    // Atajos de Fecha Vantec (Accesos Rápidos)
    document.querySelectorAll('.preset-date').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const preset = e.target.getAttribute('data-preset');
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
            
            currentStartDate = startStr;
            currentEndDate = endStr;
            loadDashboardData(startStr, endStr);
        });
    });

    fp = flatpickr("#date-range-picker", {
        mode: "range",
        dateFormat: "Y-m-d",
        locale: "es",
        onChange: function(selectedDates, dateStr, instance) {
            if (selectedDates.length === 2) {
                // Formatear fechas a YYYY-MM-DD local
                const start = flatpickr.formatDate(selectedDates[0], "Y-m-d");
                const end = flatpickr.formatDate(selectedDates[1], "Y-m-d");
                currentStartDate = start;
                currentEndDate = end;
                loadDashboardData(start, end);
            } else if (selectedDates.length === 0) {
                currentStartDate = null;
                currentEndDate = null;
                loadDashboardData();
            }
        }
    });

    // Acción para el botón de exportar reporte
    const btnExport = document.getElementById('btn-export-report');
    if (btnExport) {
        btnExport.addEventListener('click', async () => {
            const token = localStorage.getItem('token');
            let activeEntidad = localStorage.getItem('active_entidad');
    
            // 1. Sincronizar Selección Visual (Prioridad Absoluta) para evitar 404s
            const selector = document.getElementById('entity-selector');
            if (selector && selector.value && selector.value !== "") {
                if (selector.value !== activeEntidad) {
                    console.log("[+] btnExport Sincronizando visual prioritaria:", selector.value);
                    activeEntidad = selector.value;
                    localStorage.setItem('active_entidad', activeEntidad);
                }
            }

            if (!activeEntidad) {
                if (typeof Swal !== 'undefined') {
                    Swal.fire({
                        title: 'Atención',
                        text: 'Por favor, seleccione una empresa en la barra superior para continuar.',
                        icon: 'warning',
                        confirmButtonColor: '#1E3A5F'
                    });
                }
                return;
            }

            if (!token) {
                alert("No estás autenticado.");
                return;
            }
            
            try {
                let exportUrl = `/api/v1/analytics/export?entidad_id=${activeEntidad}`;
                if (currentStartDate) exportUrl += `&fecha_inicio=${currentStartDate}`;
                if (currentEndDate) exportUrl += `&fecha_fin=${currentEndDate}`;

                const response = await fetch(exportUrl, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `reporte_cfdi_${activeEntidad.substring(0,8)}.xlsx`;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    window.URL.revokeObjectURL(url);
                } else {
                    alert("Error al descargar el reporte.");
                }
            } catch (error) {
                console.error("🛡️ VANTEC EXPORT ERROR:", error);
                alert("Error de red al exportar.");
            }
        });
    }
});
