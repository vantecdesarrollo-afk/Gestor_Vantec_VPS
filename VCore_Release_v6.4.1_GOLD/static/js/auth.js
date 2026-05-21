/**
 * auth.js - Manejo de sesión y peticiones API Vantec (Estándar OAuth2)
 */

// Guardar token al iniciar sesión
function saveToken(token) {
    localStorage.setItem('token', token);
}

// Obtener token almacenado
function getToken() {
    return localStorage.getItem('token');
}

// Cambiar de empresa (Regresa al selector sin cerrar sesión)
function switchCompany() {
    localStorage.removeItem('active_entidad');
    window.location.href = '/selector';
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('active_entidad');
    window.location.href = '/login';
}

// Guardar entidad activa
function setActiveEntidad(entidadId) {
    localStorage.setItem('active_entidad', entidadId);
}

// Obtener entidad activa
function getActiveEntidad() {
    return localStorage.getItem('active_entidad');
}

// Decodificar payload de JWT (Base64)
function getUserPayload() {
    const token = getToken();
    if (!token) return null;
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function (c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (e) {
        console.error("Error al decodificar token:", e);
        return null;
    }
}

/**
 * Función de Login compatible con FastAPI OAuth2 (Password Flow)
 */
async function login(username, password) {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    const errorAlert = document.getElementById('loginError');

    try {
        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: params
        });

        const data = await response.json();

        if (response.ok) {
            saveToken(data.access_token);
            // --- ESTADO TENANT-LESS (CTO MANDATO L3) ---
            localStorage.removeItem('active_entidad');
            
            console.log("[AUTHENTICATION] Login exitoso. Redirigiendo a Aduana Neutral (/selector).");
            window.location.href = '/selector';
            return true;
        } else {
            console.error("Error de autenticación:", data.detail || "Credenciales inválidas");
            if (errorAlert) {
                errorAlert.innerText = data.detail || "Credenciales incorrectas. Intente de nuevo.";
                errorAlert.classList.remove('hidden');
            }
            return false;
        }
    } catch (error) {
        console.error("Error de red en login:", error);
        if (errorAlert) {
            errorAlert.innerText = "Error de conexión con el servidor.";
            errorAlert.classList.remove('hidden');
        }
        return false;
    }
}

// Wrapper para fetch con autorización Bearer
async function vantecFetch(url, options = {}) {
    const token = getToken();
    const activeEntidad = getActiveEntidad();

    // Si el body es FormData, dejamos que el navegador ponga el Content-Type y boundary automáticamente
    const isFormData = options.body instanceof FormData;

    const headers = {
        ...options.headers
    };

    if (!isFormData) {
        headers['Content-Type'] = 'application/json';
    }

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    if (activeEntidad) {
        headers['X-Entidad-ID'] = activeEntidad;
    }

    const response = await fetch(url, {
        ...options,
        headers
    });

    if (response.status === 401) {
        console.warn("Sesión expirada o no autorizada (401). Redirigiendo a login.");
        logout();
    }

    if (response.status === 428) {
        console.warn("[VCORE] Contexto de RFC Obligatorio (428). Redirección de Cortesía.");
        if (typeof Swal !== 'undefined') {
            let timerInterval;
            Swal.fire({
                title: '🏢 Selección de Empresa Requerida',
                html: 'Para acceder a este módulo debe seleccionar una empresa activa.<br><br>Redirigiendo al selector en <b></b> milisegundos.',
                timer: 3000,
                timerProgressBar: true,
                confirmButtonText: 'Ir a Selector Ahora',
                confirmButtonColor: '#4EBCE9',
                didOpen: () => {
                    const b = Swal.getHtmlContainer().querySelector('b');
                    timerInterval = setInterval(() => {
                        if (b) b.textContent = Swal.getTimerLeft();
                    }, 100);
                },
                willClose: () => {
                    clearInterval(timerInterval);
                }
            }).then(() => {
                window.location.href = '/selector';
            });
        } else {
            window.location.href = '/selector';
        }
        return response.json(); // Para evitar errores de cadena de promesas
    }

    if (response.status === 402) {
        console.warn("Licencia Vantec Expirada o Inválida (402). Alerta Modal.");
        let errorDetail = 'Licencia de Gestor CFDI Expirada o Inválida.';
        try {
            // Clonar respuesta para no agotar el stream si se usa después
            const error = await response.clone().json();
            errorDetail = error.detail || errorDetail;
        } catch (e) {
            try {
                errorDetail = await response.clone().text();
            } catch (textError) {}
        }

        if (typeof Swal !== 'undefined') {
            const machineIdMatch = errorDetail.match(/\(Machine ID: (.*?)\)/);
            const machineId = machineIdMatch ? machineIdMatch[1] : 'No disponible';
            const cleanMessage = errorDetail.split('(')[0].trim();

            Swal.fire({
                title: '⛔ Licencia Vantec',
                html: `<div style="text-align: left;">
                        <p style="color: #d9534f; font-weight: bold; margin-bottom: 10px;">${cleanMessage}</p>
                        <p style="font-size: 14px; color: #555;">Por favor, envíe este código de máquina a Vantec Consultores para gestionar su renovación:</p>
                        <div style="background: #f4f4f4; padding: 12px; border-radius: 6px; font-family: monospace; border: 1px solid #ddd; margin: 15px 0; word-break: break-all; font-weight: bold; color: #333;">
                            ${machineId}
                        </div>
                       </div>`,
                icon: 'error',
                showCancelButton: false,
                allowOutsideClick: false,
                allowEscapeKey: false,
                confirmButtonText: 'Entendido',
                confirmButtonColor: '#1E3A5F'
            });
        } else {
            alert(errorDetail);
        }
        throw new Error("LICENCIA_INVALIDA");
    }

    if (!response.ok) {
        let errorDetail = 'API Error';
        try {
            const text = await response.text();
            try {
                const error = JSON.parse(text);
                if (error.detail) {
                    if (Array.isArray(error.detail)) {
                        errorDetail = error.detail.map(d => `${d.loc.join('.')}: ${d.msg}`).join('\n');
                    } else if (typeof error.detail === 'object') {
                        errorDetail = JSON.stringify(error.detail, null, 2);
                    } else {
                        errorDetail = error.detail;
                    }
                } else {
                    errorDetail = text;
                }
            } catch (jsonError) {
                errorDetail = text;
            }
        } catch (e) {
            errorDetail = 'Error de red o servidor';
        }
        throw new Error(errorDetail);
    }

    return response.json();
}

// Inicializar datos de usuario en la UI (Security Hardening VCORE)
document.addEventListener('DOMContentLoaded', async () => {
    if (window.location.pathname === '/login') return;

    const payload = getUserPayload();
    if (!payload) {
        window.location.href = '/login';
        return;
    }

    // 1. Zona de Neutralidad: /selector y /configuracion no requieren active_entidad (Mandato CTO)
    const neutralVistas = ['/selector', '/configuracion'];
    const isNeutral = neutralVistas.includes(window.location.pathname);
    const activeEntidad = localStorage.getItem('active_entidad');

    if (!isNeutral && (!activeEntidad || activeEntidad === 'null' || activeEntidad === 'undefined')) {
        if (payload.is_superadmin) {
             console.log("🛡️ [VCORE] SuperAdmin en Modo Neutral. Bypass de redirección a Selector permitido continuar inicialización de UI.");
             // NO return; aquí. Permitimos que el script rellene el Menú Lateral y el Avatar.
        } else {
             console.warn("[SESSION] Sin RFC activo en vista protegida. Redirigiendo a Selector.");
             window.location.href = '/selector';
             return;
        }
    }

    // 3. Poblar UI de Usuario (Global Header)
    const userNameElement = document.getElementById('userName');
    if (userNameElement && payload.username) {
        userNameElement.innerText = payload.username.toUpperCase();
    }

    // 4. Poblar Selector Global (Context Management)
    const tenantSelector = document.getElementById('entity-selector');
    const configLink = document.getElementById('nav-config');

    if (tenantSelector && Array.isArray(payload.entidades)) {
        tenantSelector.innerHTML = '<option value="">-- SELECCIONAR EMPRESA --</option>';
        
        payload.entidades.forEach(e => {
            const opt = document.createElement('option');
            opt.value = e.id;
            opt.textContent = e.rfc;
            opt.setAttribute('data-logo', e.logo_url || "");
            tenantSelector.appendChild(opt);
        });

        // Sincronizar selección visual
        if (activeEntidad && activeEntidad !== 'null' && activeEntidad !== 'undefined') {
            const exists = Array.from(tenantSelector.options).some(o => o.value === activeEntidad);
            if (exists) {
                tenantSelector.value = activeEntidad;
                syncBrandingLogo(tenantSelector);
            } else {
                localStorage.removeItem('active_entidad');
                tenantSelector.value = "";
            }
        }

        // RBAC Contextual (Configuración)
        const activeEntidadData = payload.entidades.find(e => e.id === activeEntidad);
        const currentRole = activeEntidadData ? activeEntidadData.rol : (payload.is_superadmin ? 'ADMIN' : 'VISOR');
        if (configLink) {
             if (currentRole === 'ADMIN' || payload.is_superadmin) configLink.classList.remove('hidden');
             else configLink.classList.add('hidden');
        }

        // Evento de cambio (Context Switcher)
        tenantSelector.addEventListener('change', (e) => {
             const selectedId = e.target.value;
             if (selectedId) {
                  setActiveEntidad(selectedId);
                  window.location.reload();
             } else {
                  localStorage.removeItem('active_entidad');
                  window.location.href = '/selector';
             }
        });
    }
});

function syncBrandingLogo(selector) {
    const selectedOption = selector.options[selector.selectedIndex];
    if (selectedOption && selectedOption.getAttribute('data-logo')) {
        let logoUrl = selectedOption.getAttribute('data-logo');
        const sidebarLogo = document.getElementById('sidebar-logo');
        const companyLogoContainer = document.getElementById('company-logo-container');
        const sidebarBrandText = document.getElementById('sidebar-brand-text');
        
        if (sidebarLogo && logoUrl && logoUrl !== 'null' && logoUrl !== '') {
            if (!logoUrl.startsWith('/') && !logoUrl.startsWith('http')) {
                logoUrl = '/static/logos/' + logoUrl;
            }
            sidebarLogo.src = logoUrl;
            companyLogoContainer.classList.remove('hidden');
            if(sidebarBrandText) sidebarBrandText.classList.add('hidden');
        } else {
            resetSidebarLogo();
        }
    } else {
        resetSidebarLogo();
    }
}

function updateSidebarLogo(entidadId, entidades) {
    const entidad = entidades.find(e => e.id === entidadId);
    const sidebarLogo = document.getElementById('sidebar-logo');
    const companyLogoContainer = document.getElementById('company-logo-container');
    const sidebarBrandText = document.getElementById('sidebar-brand-text');
    
    if (entidad && entidad.logo_url && sidebarLogo) {
        let logoUrl = entidad.logo_url;
        if (!logoUrl.startsWith('/') && !logoUrl.startsWith('http')) {
            logoUrl = '/static/logos/' + logoUrl;
        }
        sidebarLogo.src = logoUrl;
        companyLogoContainer.classList.remove('hidden');
        if(sidebarBrandText) sidebarBrandText.classList.add('hidden');
    } else {
        resetSidebarLogo();
    }
}

function resetSidebarLogo() {
    const sidebarLogo = document.getElementById('sidebar-logo');
    const sidebarBrandText = document.getElementById('sidebar-brand-text');
    if (sidebarLogo) {
        sidebarLogo.src = '/static/img/Logo_Escudo_Sin_Fondo.png';
    }
    if (sidebarBrandText) {
        sidebarBrandText.classList.remove('hidden');
    }
}
