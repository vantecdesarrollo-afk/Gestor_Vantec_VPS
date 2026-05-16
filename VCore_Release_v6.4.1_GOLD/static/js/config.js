// VCORE Admin Configuration Logic
document.addEventListener('DOMContentLoaded', () => {
    // RBAC: Verificación de Privilegios SuperAdmin (Directiva v84.0)
    const token = localStorage.getItem('token');
    let isSuperAdmin = false;
    if (token) {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            isSuperAdmin = payload.is_superadmin === true;
        } catch (e) { console.error("Error parsing token for RBAC", e); }
    }

    if (isSuperAdmin) {
        const btnEntidades = document.getElementById('btn-entidades');
        if (btnEntidades) btnEntidades.classList.remove('hidden');

        const superAdminCheck = document.getElementById('container-is-superadmin');
        if (superAdminCheck) superAdminCheck.classList.remove('hidden');
        
        switchTab('tab-entidades');
    } else {
        switchTab('tab-usuarios');
    }

    loadEntidades();
    loadUsuarios();

    // VINCULACIÓN SEGURA DE EVENTOS SMTP (Bypass de Caché y SES)
    const smtpSelect = document.getElementById('smtp-entidad-id');
    if (smtpSelect) {
        smtpSelect.addEventListener('change', (e) => {
            loadSmtpConfig(e.target.value);
        });
    }

    const btnSaveSmtp = document.getElementById('btn-save-smtp');
    if (btnSaveSmtp) {
        btnSaveSmtp.addEventListener('click', saveSmtpConfig);
    }

    const btnTestSmtp = document.getElementById('btn-test-smtp');
    if (btnTestSmtp) {
        btnTestSmtp.addEventListener('click', testSmtpConfig);
    }
});

// --- Tab Switching ---
window.switchTab = function (tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.add('hidden'));
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('block'));

    const target = document.getElementById(tabId);
    if (target) {
        target.classList.remove('hidden');
        target.classList.add('block');
    }

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('border-[#4EBCE9]', 'text-[#1E3A5F]', 'font-bold');
        btn.classList.add('border-transparent', 'text-gray-500');
    });

    const activeBtn = document.getElementById('btn-' + tabId.replace('tab-', ''));
    if(activeBtn){
        activeBtn.classList.add('border-[#4EBCE9]', 'text-[#1E3A5F]', 'font-bold');
        activeBtn.classList.remove('border-transparent', 'text-gray-500');
    }

    // Interceptamos para cargar SMTP si se abre la pestaña
    if (tabId === 'tab-correo') {
        const tenantId = document.getElementById('smtp-entidad-id')?.value;
        if (tenantId) {
            loadSmtpConfig(tenantId);
        }
    }
    
    if (tabId === 'tab-auditoria') {
        loadFinancialAnomalies();
        loadGlobalAuditLogs();
    }
};

/**
 * Carga los logs de auditoría global para el SuperAdmin (Bitácora Técnica v45.0)
 */
async function loadGlobalAuditLogs() {
    const content = document.getElementById('global-log-content');
    if (!content) return;
    
    try {
        const response = await vantecFetch('/api/v1/admin/audit/logs');
        if (response && response.content) {
            content.style.whiteSpace = 'pre-wrap';
            content.innerText = response.content;
            content.scrollTop = content.scrollHeight;
        } else {
            content.innerText = 'No se encontraron registros de auditoría global para hoy.';
        }
    } catch (error) {
        console.error('Error cargando logs globales:', error);
        content.innerText = 'Error al conectar con el servicio de auditoría técnica.';
    }
}

// --- Modals ---
window.showModal = function (id) {
    if (id === 'modal-entidad') {
        document.getElementById('form-entidad').reset();
        document.getElementById('field-entidad-id').value = '';
        document.getElementById('modal-entidad-title').innerText = 'Registrar Nueva Empresa';
        document.getElementById('container-is-active').classList.add('hidden');
        document.getElementById('logo-preview-container').classList.add('hidden');
        document.getElementById('logo-preview').src = '';
    } else if (id === 'modal-usuario') {
        const form = document.getElementById('form-usuario');
        form.reset();
        form.removeAttribute('data-id');
        const passField = form.querySelector('[name="password"]');
        if (passField) { passField.required = true; passField.placeholder = ''; }
        const title = document.querySelector('#modal-usuario h3');
        if (title) title.innerText = 'Crear Nuevo Usuario';
        const btn = form.querySelector('button[type="submit"]');
        if (btn) btn.innerText = 'Crear Cuenta';
    }
    document.getElementById(id).style.display = 'flex';
};

window.hideModal = function (id) {
    document.getElementById(id).style.display = 'none';
};

// --- Data Fetching ---
async function loadEntidades() {
    try {
        const data = await vantecFetch('/api/v1/admin/entidades');
        const container = document.getElementById('table-entidades');
        const select = document.getElementById('select-entidad');
        const smtpSelect = document.getElementById('smtp-entidad-id');
        container.innerHTML = '';
        select.innerHTML = '<option value="">-- Seleccionar Empresa --</option>';
        if (smtpSelect) smtpSelect.innerHTML = '<option value="">-- Seleccionar Empresa para SMTP --</option>';

        // RBAC: Determinar autoridad para Matriz de Acceso (Directiva v84.2)
        const token = localStorage.getItem('token');
        let authEntidades = [];
        let isSuper = false;
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                authEntidades = payload.entidades || [];
                isSuper = payload.is_superadmin === true;
            } catch(e) {}
        }

        data?.forEach(e => {
            const row = `
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-bold text-[#1E3A5F]">${e.rfc}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${e.razon_social}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2 py-1 text-xs font-bold rounded-full ${e.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                            ${e.is_active ? 'ACTIVO' : 'INACTIVO'}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                        <button onclick="editEntidad('${e.id}', '${e.rfc}', '${e.razon_social}', ${e.is_active}, '${e.logo_path || ''}')" class="text-[#4EBCE9] hover:text-[#1E3A5F] font-bold">Editar</button>
                    </td>
                </tr>
            `;
            container.insertAdjacentHTML('beforeend', row);
            
            // BLINDAJE: Solo permitir asignar accesos en empresas donde se es ADMIN (o Global Super)
            const meta = authEntidades.find(ae => ae.id === e.id);
            if (isSuper || (meta && meta.rol === 'ADMIN')) {
                const opt = `<option value="${e.id}">${e.rfc} - ${e.razon_social}</option>`;
                select.insertAdjacentHTML('beforeend', opt);
                if (smtpSelect) smtpSelect.insertAdjacentHTML('beforeend', opt);
            }
        });

        const activeEntidad = localStorage.getItem('active_entidad');
        if (activeEntidad) {
            select.value = activeEntidad;
            if (smtpSelect) smtpSelect.value = activeEntidad;
        }
    } catch (error) {
        console.error('Error loading entidades:', error);
    }
}

async function loadUsuarios() {
    try {
        const data = await vantecFetch('/api/v1/admin/usuarios');
        const container = document.getElementById('table-usuarios');
        const select = document.getElementById('select-usuario');
        container.innerHTML = '';
        select.innerHTML = '<option value="">-- Seleccionar Usuario --</option>';

        data?.forEach(u => {
            container.innerHTML += `
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-bold text-[#1E3A5F]">${u.username}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${u.email || ''}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2 py-1 text-[10px] font-black rounded-full ${u.is_superadmin ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'} uppercase">
                            ${u.is_superadmin ? 'SUPER ADMIN' : u.rol}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                        ${u.is_active ? 'Habilitado' : 'Suspendido'}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                        <button onclick="editUsuario(this)" data-id="${u.id}" data-username="${u.username}" data-email="${u.email || ''}" data-superadmin="${u.is_superadmin}" data-active="${u.is_active}" data-rol="${u.rol || 'VISOR'}" class="text-[#4EBCE9] hover:text-[#1E3A5F] font-bold mr-3">Editar</button>
                        <button onclick="toggleUsuarioStatus('${u.id}', ${u.is_active})" class="${u.is_active ? 'text-red-500 hover:text-red-700' : 'text-green-500 hover:text-green-700'} font-bold">
                            ${u.is_active ? 'Deshabilitar' : 'Habilitar'}
                        </button>
                    </td>
                </tr>
            `;
            if (u.is_active) {
                select.innerHTML += `<option value="${u.id}">${u.email || ''} (${u.username})</option>`;
            }
        });
    } catch (error) {
        console.error('Error loading usuarios:', error);
    }
}

window.editEntidad = function (id, rfc, razonSocial, isActive, logoUrl) {
    document.getElementById('modal-entidad-title').innerText = 'Editar Empresa';
    document.getElementById('field-entidad-id').value = id;
    document.getElementById('rfc').value = rfc || '';
    document.getElementById('razon_social').value = razonSocial || '';

    const checkActive = document.getElementById('field-is-active');
    if (checkActive) checkActive.checked = isActive === true;
    document.getElementById('container-is-active').classList.remove('hidden');

    const previewContainer = document.getElementById('logo-preview-container');
    const previewImg = document.getElementById('logo-preview');
    if (logoUrl) {
        previewImg.src = logoUrl;
        previewContainer.classList.remove('hidden');
    } else {
        previewContainer.classList.add('hidden');
    }

    document.getElementById('modal-entidad').style.display = 'flex';
};

document.addEventListener('change', (e) => {
    if (e.target && e.target.id === 'field-logo') {
        const file = e.target.files[0];
        const previewContainer = document.getElementById('logo-preview-container');
        const previewImg = document.getElementById('logo-preview');

        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                previewImg.src = event.target.result;
                previewContainer.classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        }
    }
});

// --- Submissions ---
window.forceTokenRefresh = async function() {
    try {
        const response = await fetch('/api/v1/auth/refresh', { method: 'POST', headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } });
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.access_token);
        }
    } catch(e) {}
};

window.submitEntidad = async function () {
    const form = document.getElementById('form-entidad');
    const formData = new FormData(form);
    const entidadId = document.getElementById('field-entidad-id').value;

    const url = entidadId ? `/api/v1/admin/entidades/${entidadId}` : '/api/v1/admin/entidades';
    const method = entidadId ? 'PATCH' : 'POST';

    if (entidadId) {
        const isActive = document.getElementById('field-is-active').checked;
        formData.set('is_active', isActive ? 'true' : 'false');
    }

    try {
        const result = await vantecFetch(url, { method: method, body: formData });
        if (result) {
            await window.forceTokenRefresh();
            alert(entidadId ? 'Empresa actualizada exitosamente.' : 'Empresa registrada exitosamente.');
            hideModal('modal-entidad');
            form.reset();
            window.location.reload();
        }
    } catch (error) {
        alert('Error al guardar empresa: ' + error.message);
    }
};

window.submitUsuario = async function () {
    const form = document.getElementById('form-usuario');
    const userId = form.getAttribute('data-id');
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());
    payload.is_superadmin = document.getElementById('is_superadmin').checked;

    const url = userId ? `/api/v1/admin/usuarios/${userId}` : '/api/v1/admin/usuarios';
    const method = userId ? 'PUT' : 'POST';

    if (!userId) {
        const password = payload.password;
        const passRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
        if (!passRegex.test(password)) {
            Swal.fire('Seguridad', 'La contraseña debe tener al menos 8 caracteres, una mayúscula, un número y un carácter especial.', 'warning');
            return;
        }
    }

    try {
        const result = await vantecFetch(url, {
            method: method,
            body: JSON.stringify(payload)
        });
        if (result) {
            Swal.fire('Éxito', userId ? 'Usuario actualizado.' : 'Usuario creado.', 'success');
            hideModal('modal-usuario');
            form.reset();
            form.removeAttribute('data-id');
            loadUsuarios();
        }
    } catch (error) {
        Swal.fire('Error', 'Error al procesar usuario: ' + error.message, 'error');
    }
};

window.saveAccess = async function () {
    const usuario_id = document.getElementById('select-usuario').value;
    const entidad_id = document.getElementById('select-entidad').value;
    const rol = document.getElementById('select-rol').value;

    if (!usuario_id || !entidad_id) {
        alert('Debe seleccionar un usuario y una empresa.');
        return;
    }

    try {
        const result = await vantecFetch('/api/v1/admin/accesos', {
            method: 'POST',
            body: JSON.stringify({ usuario_id, entidad_id, rol })
        });
        if (result) {
            Swal.fire('Éxito', 'Permisos vinculados y guardados correctamente.', 'success');
            // Opcional: recargar lista si se requiere
        }
    } catch (error) {
        Swal.fire('Error', 'Falla al asignar acceso: ' + error.message, 'error');
    }
};

// --- Funciones SMTP Formales ---
async function loadSmtpConfig(tenantId) {
    if (!tenantId) {
        document.getElementById('form-smtp').reset();
        return;
    }
    try {
        const data = await vantecFetch(`/api/v1/smtp/${tenantId}`);
        if (data) {
            // Se corrige la frágil selección por placeholder usando IDs
            document.getElementById('smtp-host').value = data.host || '';
            document.getElementById('smtp-port').value = data.port || 587;
            document.getElementById('smtp-username').value = data.username || '';
            document.getElementById('smtp-from-address').value = data.from_address || '';
            document.getElementById('smtp-security-type').value = data.security_type || 'STARTTLS';
            document.getElementById('smtp-auth-type').value = data.authentication_type || 'LOGIN';
            
            const passField = document.getElementById('smtp-password');
            passField.value = ''; 
            if (data.has_password) {
                passField.placeholder = '•••••••• (Preservado, rellenar solo para cambiar)';
            } else {
                passField.placeholder = 'Rellenar contraseña';
            }
        }
    } catch (error) {
        if (error.message.includes("404") || error.message.toLowerCase().includes("not found") || error.message.includes("encontrado")) {
             document.getElementById('form-smtp').reset();
             document.getElementById('smtp-password').placeholder = 'Rellenar contraseña';
             return;
        }
        console.error('Error loading SMTP Config:', error);
        Swal.fire('Error', 'Falla al cargar configuración SMTP: ' + error.message, 'error');
    }
}

async function saveSmtpConfig() {
    const tenantId = document.getElementById('smtp-entidad-id').value;
    if (!tenantId) {
        Swal.fire('Error', 'Debe seleccionar una empresa.', 'error');
        return;
    }

    const payload = {
        host: document.getElementById('smtp-host').value,
        port: parseInt(document.getElementById('smtp-port').value) || 587,
        username: document.getElementById('smtp-username').value,
        from_address: document.getElementById('smtp-from-address').value,
        password: document.getElementById('smtp-password').value, 
        security_type: document.getElementById('smtp-security-type').value,
        authentication_type: document.getElementById('smtp-auth-type').value
    };

    try {
        const result = await vantecFetch(`/api/v1/smtp/${tenantId}`, {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        if (result) {
            Swal.fire({
                title: 'Guardado',
                text: 'Configuración SMTP guardada exitosamente.',
                icon: 'success',
                confirmButtonColor: '#1E3A5F'
            });
            loadSmtpConfig(tenantId);
        }
    } catch (error) {
        Swal.fire('Error', 'Falla al guardar SMTP: ' + error.message, 'error');
    }
}

async function testSmtpConfig() {
    const tenantId = document.getElementById('smtp-entidad-id').value;
    if (!tenantId) {
        Swal.fire('Error', 'Debe seleccionar una empresa.', 'error');
        return;
    }
    try {
        const result = await vantecFetch(`/api/v1/smtp/${tenantId}/test`, {
            method: 'POST'
        });
        if (result) {
            Swal.fire('Éxito', 'Conexión SMTP exitosa (250 OK)', 'success');
        }
    } catch (error) {
        Swal.fire('Error', 'Prueba SMTP fallida: ' + error.message, 'error');
    }
}

window.editUsuario = function (btn) {
     const id = btn.getAttribute('data-id');
     const username = btn.getAttribute('data-username');
     const email = btn.getAttribute('data-email');
     const isSuperadmin = btn.getAttribute('data-superadmin') === 'true';
     const rol = btn.getAttribute('data-rol') || 'VISOR';
     
     const form = document.getElementById('form-usuario');
     form.querySelector('[name="username"]').value = username || '';
     form.querySelector('[name="email"]').value = email || '';
     const rolField = form.querySelector('[name="rol"]');
     if (rolField) rolField.value = rol;
     const passField = form.querySelector('[name="password"]');
     if (passField) { passField.required = false; passField.placeholder = '••••••••'; }
     
     const checkSuper = document.getElementById('is_superadmin');
     if (checkSuper) checkSuper.checked = isSuperadmin;
     
     form.setAttribute('data-id', id);
     
     const title = document.querySelector('#modal-usuario h3');
     if (title) title.innerText = 'Editar Usuario';
     const submitBtn = form.querySelector('button[type="submit"]');
     if (submitBtn) submitBtn.innerText = 'Guardar Cambios';

     showModal('modal-usuario');
};

window.toggleUsuarioStatus = async function (id, currentStatus) {
     const newStatus = !currentStatus;
     try {
          const result = await vantecFetch(`/api/v1/admin/usuarios/${id}`, {
               method: 'PUT',
               body: JSON.stringify({ is_active: newStatus })
          });
          if (result) {
               Swal.fire('Éxito', `Usuario ${newStatus ? 'Habilitado' : 'Deshabilitado'}`, 'success');
               loadUsuarios();
          }
     } catch (error) {
          Swal.fire('Error', 'Falla al cambiar estado: ' + error.message, 'error');
     }
};

window.loadFinancialAnomalies = async function() {
    const tableBody = document.getElementById('table-anomalias');
    if (!tableBody) return;

    try {
        const data = await vantecFetch('/api/v1/admin/audit/financial-anomalies');
        tableBody.innerHTML = '';

        if (!data || data.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="p-12 text-center text-gray-400 font-bold">No hay anomalías registradas en la bitácora.</td></tr>';
            return;
        }

        data.forEach(a => {
            let statusClass = 'bg-red-100 text-red-800';
            if (a.estatus === 'RESUELTA') statusClass = 'bg-green-100 text-green-800';
            
            let typeIcon = 'fa-exclamation-triangle';
            if (a.tipo_anomalia === 'GHOST_RECOVERY') typeIcon = 'fa-ghost text-blue-500';

            const row = `
                <tr class="hover:bg-gray-50 transition-colors">
                    <td class="px-6 py-4 whitespace-nowrap text-xs font-mono text-gray-500">${a.fecha}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-xs font-bold text-[#1E3A5F]">
                        <i class="fas ${typeIcon} mr-2"></i> ${a.tipo_anomalia}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-xs font-mono text-gray-400">${a.uuid_documento}</td>
                    <td class="px-6 py-4 text-xs font-medium text-gray-600">${a.detalle}</td>
                    <td class="px-6 py-4 text-center">
                        <span class="px-2 py-1 text-[10px] font-black rounded-full ${statusClass} uppercase">
                            ${a.estatus}
                        </span>
                    </td>
                </tr>
            `;
            tableBody.insertAdjacentHTML('beforeend', row);
        });
    } catch (error) {
        console.error('Error loading anomalies:', error);
        tableBody.innerHTML = `<tr><td colspan="5" class="p-12 text-center text-red-500 font-bold">Error al cargar bitácora: ${error.message}</td></tr>`;
    }
};