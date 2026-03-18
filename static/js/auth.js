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

// Cerrar sesión
function logout() {
    localStorage.removeItem('token');
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
            localStorage.removeItem('active_entidad');
            console.log("Login exitoso");
            window.location.href = '/dashboard';
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
            const error = await response.json();
            errorDetail = error.detail || 'API Error';
        } catch (e) {
            // El cuerpo no era JSON (ej: 500 Internal Server Error de texto plano)
            try {
                errorDetail = await response.text();
            } catch (textError) {
                errorDetail = 'Error de Servidor desconocido';
            }
        }
        throw new Error(errorDetail);
    }

    return response.json();
}

// Inicializar datos de usuario en la UI
document.addEventListener('DOMContentLoaded', () => {
    const payload = getUserPayload();
    const userNameElement = document.getElementById('userName');
    const configLink = document.getElementById('nav-config');
    const tenantSelector = document.getElementById('entity-selector');

    if (payload) {
        // 1. Actualizar nombre en sidebar
        if (userNameElement && payload.username) {
            userNameElement.innerText = payload.username;
        }

        // 2. Mostrar Configuración solo si es Superadmin
        if (configLink && payload.is_superadmin) {
            configLink.classList.remove('hidden');
        }

        // 3. Poblar Selector de Entidades (Multi-tenant)
        if (tenantSelector && Array.isArray(payload.entidades)) {
            tenantSelector.innerHTML = '<option value="" disabled selected>-- Seleccionar Empresa --</option>';

            payload.entidades.forEach(entidad => {
                const opt = document.createElement('option');
                opt.value = entidad.id; // UUID
                opt.textContent = entidad.rfc;
                opt.setAttribute('data-logo', entidad.logo_url || "");
                tenantSelector.appendChild(opt);
            });

            // --- REQUISITO: Recuperar selección previa ---
            const activeEntidad = localStorage.getItem('active_entidad');
            const optionExists = Array.from(tenantSelector.options).some(opt => opt.value === activeEntidad);
            
            if (activeEntidad && optionExists && activeEntidad !== 'null' && activeEntidad !== 'undefined') {
                tenantSelector.value = activeEntidad;
                syncBrandingLogo(tenantSelector);
            } else {
                // Estado Neutro: No autoseleccionar nada, remover active_entidad previo para forzar elección
                localStorage.removeItem('active_entidad');
                tenantSelector.value = "";
            }

            // 4. Evento de cambio (Ciclo de Vida Limpio + STRIKE CTO)
            tenantSelector.addEventListener('change', (e) => {
                const selectedOption = e.target.options[e.target.selectedIndex];
                const selectedId = selectedOption.value;

                if (selectedId && selectedId !== "" && selectedId !== "undefined" && selectedId !== "null") {
                    console.log("[+] Seleccionando Entidad (UUID):", selectedId);
                    setActiveEntidad(selectedId);
                    window.location.reload();
                } else if (selectedId === "") {
                    console.log("[+] Deseleccionando Entidad");
                    localStorage.removeItem('active_entidad');
                    window.location.href = '/dashboard';
                }
            });
        }
    } else if (window.location.pathname !== '/login') {
        window.location.href = '/login';
    }
});

function syncBrandingLogo(selector) {
    // Logo is now statically defined in base.html. Feature disabled to prevent flicker.
    return;
}

function updateSidebarLogo(entidadId, entidades) {
    // Logo is now statically defined in base.html. Feature disabled to prevent flicker.
    return;
}

function resetSidebarLogo() {
    // Logo is now statically defined in base.html. Feature disabled to prevent flicker.
    return;
}
