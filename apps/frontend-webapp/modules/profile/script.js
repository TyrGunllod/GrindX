(function initProfile() {
    let currentUser = {};

    async function loadProfile() {
        try {
            const profile = await window.grindx.api.get('/auth/me');
            if (!profile) return;
            currentUser = profile;
        } catch (err) {
            showToast(err.message || 'Erro ao carregar perfil.', 'error');
            return;
        }

        document.getElementById('profileUsername').value = profile.username || '';
        document.getElementById('profileRole').value = formatRole(profile.role);
        document.getElementById('profileName').value = profile.nome_completo || '';
        document.getElementById('profileEmail').value = profile.email || '';

        const currentTheme = window.grindx.theme.theme;
        document.querySelectorAll('.theme-option').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === currentTheme);
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

            const selectedTheme = document.querySelector('.theme-option.active')?.dataset.theme;
            if (selectedTheme && selectedTheme !== window.grindx.theme.theme) {
                window.grindx.theme.theme = selectedTheme;
                window.grindx.storage.set('grindx_theme', selectedTheme);
                window.grindx.theme.apply();
                window.parent.postMessage('theme-changed', '*');
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

        document.querySelectorAll('.theme-option').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.theme-option').forEach(b => b.classList.remove('active'));
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
            document.querySelectorAll('.theme-option').forEach(btn => {
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
