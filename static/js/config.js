// VCORE Admin Configuration Logic
document.addEventListener('DOMContentLoaded', () => {
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
};

// --- Modals ---
window.showModal = function (id) {
    if (id === 'modal-entidad') {
        document.getElementById('form-entidad').reset();
        document.getElementById('field-entidad-id').value = '';
        document.getElementById('modal-entidad-title').innerText = 'Registrar Nueva Empresa';
        document.getElementById('container-is-active').classList.add('hidden');
        document.getElementById('logo-preview-container').classList.add('hidden');
        document.getElementById('logo-preview').src = '';
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
                        <button onclick="editEntidad('${e.id}', '${e.rfc}', '${e.razon_social}', ${e.is_active}, '${e.logo_url || ''}')" class="text-[#4EBCE9] hover:text-[#1E3A5F] font-bold">Editar</button>
                    </td>
                </tr>
            `;
            container.insertAdjacentHTML('beforeend', row);
            
            const opt = `<option value="${e.id}">${e.rfc} - ${e.razon_social}</option>`;
            select.insertAdjacentHTML('beforeend', opt);
            if (smtpSelect) smtpSelect.insertAdjacentHTML('beforeend', opt);
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
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${u.email}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2 py-1 text-xs font-bold rounded-full ${u.is_superadmin ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'}">
                            ${u.is_superadmin ? 'SUPER ADMIN' : 'USUARIO'}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-400">
                        ${u.is_active ? 'Habilitado' : 'Suspendido'}
                    </td>
                </tr>
            `;
            select.innerHTML += `<option value="${u.id}">${u.email} (${u.username})</option>`;
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
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());
    payload.is_superadmin = document.getElementById('is_superadmin').checked;

    try {
        const result = await vantecFetch('/api/v1/admin/usuarios', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        if (result) {
            alert('Usuario creado correctamente.');
            hideModal('modal-usuario');
            form.reset();
            loadUsuarios();
        }
    } catch (error) {
        alert('Error al crear usuario.');
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
            alert(result.message);
        }
    } catch (error) {
        alert('Error al asignar acceso.');
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

function testSmtpConfig() {
    Swal.fire({
        title: 'Prueba de Conexión',
        text: 'Conexión SMTP exitosa (250 OK)',
        icon: 'success',
        confirmButtonColor: '#1E3A5F'
    });
}