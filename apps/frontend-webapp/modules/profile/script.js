(function initProfile() {
    let currentUser = {};

    function getUserData() {
        try {
            return window.parent.grindx?.session?.getUserProfile?.() || {};
        } catch (e) {
            return {};
        }
    }

    async function loadProfile() {
        let profile = null;
        try {
            profile = await window.grindx.api.get('/auth/me');
        } catch (err) {
            profile = getUserData();
        }

        if (!profile || !profile.username) {
            profile = getUserData();
        }

        if (!profile || !profile.username) {
            showToast('Erro ao carregar perfil.', 'error');
            return;
        }

        currentUser = profile;

        document.getElementById('profileUsername').value = profile.username || '';
        document.getElementById('profileRole').value = formatRole(profile.role);
        document.getElementById('profileName').value = profile.nome_completo || '';
        document.getElementById('profileEmail').value = profile.email || '';

        const currentTheme = window.grindx.theme.theme;
        document.querySelectorAll('.toggle-option[data-theme]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === currentTheme);
        });

        const currentLayout = window.parent.grindx?.storage?.get('grindx_layout') || profile.layout_preference || 'topbar';
        document.querySelectorAll('.toggle-option[data-layout]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.layout === currentLayout);
        });
    }

    function formatRole(role) {
        const labels = { admin: 'Administrador', operador: 'Operador', leitura: 'Leitura' };
        return labels[role] || role || 'Usuário';
    }

    function showError(elementId, message) {
        const el = document.getElementById(elementId);
        if (el) {
            el.textContent = message;
            el.style.display = message ? 'block' : 'none';
        }
    }

    async function handleSave() {
        const saveBtn = document.getElementById('saveProfileBtn');
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Salvando...';

        showError('emailError', '');
        showError('passwordError', '');

        try {
            const newEmail = document.getElementById('profileEmail').value.trim();
            if (newEmail !== currentUser.email) {
                await window.grindx.api.put('/auth/me', { email: newEmail });
                currentUser.email = newEmail;
            }

            const currentPassword = document.getElementById('currentPassword').value;
            const newPassword = document.getElementById('newPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            if (currentPassword || newPassword || confirmPassword) {
                if (newPassword !== confirmPassword) {
                    showError('passwordError', 'Nova senha e confirmação não conferem.');
                    saveBtn.disabled = false;
                    saveBtn.innerHTML = '<i class="fas fa-save"></i> Salvar Alterações';
                    return;
                }
                if (newPassword.length < 6) {
                    showError('passwordError', 'Nova senha deve ter no mínimo 6 caracteres.');
                    saveBtn.disabled = false;
                    saveBtn.innerHTML = '<i class="fas fa-save"></i> Salvar Alterações';
                    return;
                }
                await window.grindx.api.post('/auth/change-password', {
                    current_password: currentPassword,
                    new_password: newPassword,
                });
                document.getElementById('passwordForm').reset();
            }

            const selectedTheme = document.querySelector('.toggle-option[data-theme].active')?.dataset.theme;
            const updateData = {};
            if (selectedTheme && selectedTheme !== window.grindx.theme.theme) {
                window.grindx.theme.theme = selectedTheme;
                window.grindx.storage.set('grindx_theme', selectedTheme);
                window.grindx.theme.apply();
                window.parent.postMessage('theme-changed', '*');
                updateData.theme_preference = selectedTheme;
            }

            const selectedLayout = document.querySelector('.toggle-option[data-layout].active')?.dataset.layout;
            const currentLayout = window.parent.grindx?.storage?.get('grindx_layout') || '';
            if (selectedLayout && selectedLayout !== currentLayout) {
                window.parent.grindx.storage.set('grindx_layout', selectedLayout);
                updateData.layout_preference = selectedLayout;
                window.parent.postMessage('layout-changed', '*');
            }

            if (Object.keys(updateData).length > 0) {
                await window.grindx.api.put('/auth/me', updateData);
            }

            window.parent.postMessage('profile-saved', '*');
            showToast('Alterações salvas com sucesso!', 'success');
        } catch (err) {
            const msg = err.message || 'Erro ao salvar alterações.';
            if (msg.toLowerCase().includes('email') || msg.toLowerCase().includes('e-mail')) {
                showError('emailError', msg);
            } else if (msg.toLowerCase().includes('senha') || msg.toLowerCase().includes('password')) {
                showError('passwordError', msg);
            } else {
                showToast(msg, 'error');
            }
        } finally {
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="fas fa-save"></i> Salvar Alterações';
        }
    }

    function showToast(message, type) {
        const region = document.getElementById('toastRegion') || (() => {
            const r = document.createElement('div');
            r.id = 'toastRegion';
            r.className = 'toast-region';
            document.body.appendChild(r);
            return r;
        })();
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        region.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

    function setupEvents() {
        document.getElementById('saveProfileBtn').addEventListener('click', handleSave);

        document.querySelectorAll('.toggle-option').forEach(btn => {
            btn.addEventListener('click', () => {
                const group = btn.closest('.toggle-group');
                group.querySelectorAll('.toggle-option').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });

        document.querySelectorAll('input').forEach(input => {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    handleSave();
                }
            });
        });
    }

    window.addEventListener('message', (e) => {
        if (e.data === 'theme-changed') {
            const currentTheme = window.grindx.theme.theme;
            document.querySelectorAll('.toggle-option[data-theme]').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.theme === currentTheme);
            });
        }
    });

    document.addEventListener('DOMContentLoaded', () => {
        setupEvents();
        loadProfile();
    });

    if (document.readyState !== 'loading') {
        setupEvents();
        loadProfile();
    }
})();
