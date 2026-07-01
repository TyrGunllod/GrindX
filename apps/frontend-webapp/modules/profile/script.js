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
        document.getElementById('profileCodigo').value = profile.codigo || '';
        document.getElementById('profileCbo').value = profile.cbo || '';
        document.getElementById('profileDepartamento').value = profile.departamento || '';
        document.getElementById('profileCargo').value = profile.cargo || '';
        document.getElementById('profileClassificacao').value = profile.classificacao || '';
        document.getElementById('profileCpf').value = formatCpf(profile.cpf || '');
        document.getElementById('profileEndereco').value = profile.endereco || '';
        document.getElementById('profileNumero').value = profile.numero || '';
        document.getElementById('profileCep').value = formatCep(profile.cep || '');
        document.getElementById('profileTelefone').value = formatTelefone(profile.telefone || '');
        document.getElementById('profileCelular').value = formatCelular(profile.celular || '');

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

    function formatCpf(v) {
        const d = v.replace(/\D/g, '').slice(0, 11);
        if (d.length <= 3) return d;
        if (d.length <= 6) return d.slice(0, 3) + '.' + d.slice(3);
        if (d.length <= 9) return d.slice(0, 3) + '.' + d.slice(3, 6) + '.' + d.slice(6);
        return d.slice(0, 3) + '.' + d.slice(3, 6) + '.' + d.slice(6, 9) + '-' + d.slice(9, 11);
    }

    function formatCep(v) {
        const d = v.replace(/\D/g, '').slice(0, 8);
        if (d.length <= 5) return d;
        return d.slice(0, 5) + '-' + d.slice(5);
    }

    function formatFone(v, isCelular) {
        const d = v.replace(/\D/g, '').slice(0, isCelular ? 11 : 10);
        if (d.length < 3) return d;
        let s = '(' + d.slice(0, 2) + ') ';
        if (isCelular) {
            s += d.slice(2, 7);
            if (d.length > 7) s += '-' + d.slice(7);
        } else {
            s += d.slice(2, 6);
            if (d.length > 6) s += '-' + d.slice(6);
        }
        return s;
    }

    function formatTelefone(v) { return formatFone(v, false); }
    function formatCelular(v) { return formatFone(v, true); }

    function stripMask(v) {
        return v.replace(/\D/g, '');
    }

    function showError(elementId, message) {
        const el = document.getElementById(elementId);
        if (el) {
            el.textContent = message;
            el.style.display = message ? 'block' : 'none';
        }
    }

    function setLoading(btnId, loading) {
        const btn = document.getElementById(btnId);
        if (!btn) return;
        btn.disabled = loading;
        btn.innerHTML = loading
            ? '<i class="fas fa-spinner fa-spin"></i> Salvando...'
            : '<i class="fas fa-save"></i> Salvar';
    }

    async function saveProfile() {
        setLoading('saveProfileBtn', true);
        showError('emailError', '');

        try {
            const data = {};
            const fields = ['codigo', 'cbo', 'departamento', 'cargo', 'classificacao', 'cpf', 'endereco', 'numero', 'cep', 'telefone', 'celular', 'email'];
            fields.forEach(f => {
                const el = document.getElementById('profile' + f.charAt(0).toUpperCase() + f.slice(1));
                if (el) data[f] = el.value.trim();
            });

            if (data.cpf) data.cpf = stripMask(data.cpf);
            if (data.cep) data.cep = stripMask(data.cep);
            if (data.telefone) data.telefone = stripMask(data.telefone);
            if (data.celular) data.celular = stripMask(data.celular);
            if (data.email === currentUser.email) delete data.email;

            if (Object.keys(data).length > 0) {
                await window.grindx.api.put('/auth/me', data);
                Object.assign(currentUser, data);
            }

            window.parent.postMessage('profile-saved', '*');
            showToast('Dados salvos com sucesso!', 'success');
        } catch (err) {
            const msg = err.message || 'Erro ao salvar dados.';
            if (msg.toLowerCase().includes('email') || msg.toLowerCase().includes('e-mail')) {
                showError('emailError', msg);
            } else {
                showToast(msg, 'error');
            }
        } finally {
            setLoading('saveProfileBtn', false);
        }
    }

    async function savePassword() {
        setLoading('savePasswordBtn', true);
        showError('passwordError', '');

        try {
            const currentPassword = document.getElementById('currentPassword').value;
            const newPassword = document.getElementById('newPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            if (!currentPassword || !newPassword || !confirmPassword) {
                showError('passwordError', 'Preencha todos os campos de senha.');
                setLoading('savePasswordBtn', false);
                return;
            }

            if (newPassword !== confirmPassword) {
                showError('passwordError', 'Nova senha e confirmação não conferem.');
                setLoading('savePasswordBtn', false);
                return;
            }
            if (newPassword.length < 6) {
                showError('passwordError', 'Nova senha deve ter no mínimo 6 caracteres.');
                setLoading('savePasswordBtn', false);
                return;
            }

            await window.grindx.api.post('/auth/change-password', {
                current_password: currentPassword,
                new_password: newPassword,
            });

            document.getElementById('passwordForm').reset();
            window.parent.postMessage('profile-saved', '*');
            showToast('Senha alterada com sucesso!', 'success');
        } catch (err) {
            const msg = err.message || 'Erro ao alterar senha.';
            if (msg.toLowerCase().includes('senha') || msg.toLowerCase().includes('password')) {
                showError('passwordError', msg);
            } else {
                showToast(msg, 'error');
            }
        } finally {
            setLoading('savePasswordBtn', false);
        }
    }

    async function savePreferences() {
        setLoading('savePreferencesBtn', true);

        try {
            const updateData = {};

            const selectedTheme = document.querySelector('.toggle-option[data-theme].active')?.dataset.theme;
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
            showToast('Preferências salvas com sucesso!', 'success');
        } catch (err) {
            showToast(err.message || 'Erro ao salvar preferências.', 'error');
        } finally {
            setLoading('savePreferencesBtn', false);
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

    function maskCpfOnBlur() {
        const el = document.getElementById('profileCpf');
        if (el.value) el.value = formatCpf(el.value);
    }
    function maskCepOnBlur() {
        const el = document.getElementById('profileCep');
        if (el.value) el.value = formatCep(el.value);
    }
    function maskTelefoneOnBlur() {
        const el = document.getElementById('profileTelefone');
        if (el.value) el.value = formatTelefone(el.value);
    }
    function maskCelularOnBlur() {
        const el = document.getElementById('profileCelular');
        if (el.value) el.value = formatCelular(el.value);
    }
    function unmaskOnFocus(el) {
        el.value = stripMask(el.value);
    }

    async function lookupCbo() {
        const cboEl = document.getElementById('profileCbo');
        const cargoEl = document.getElementById('profileCargo');
        const cbo = cboEl.value.replace(/\D/g, '').slice(0, 6);
        if (cbo.length < 4) return;
        try {
            const res = await fetch('https://sistemas.unasus.gov.br/ws_cbo/cbo.php?cbo=' + cbo);
            const xml = await res.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(xml, 'text/xml');
            const desc = doc.querySelector('descricao');
            if (desc && desc.textContent) {
                cargoEl.value = desc.textContent;
            }
        } catch (e) {
            // silently fail — external API may be unreachable
        }
    }

    function setupEvents() {
        document.getElementById('saveProfileBtn').addEventListener('click', saveProfile);
        document.getElementById('savePasswordBtn').addEventListener('click', savePassword);
        document.getElementById('savePreferencesBtn').addEventListener('click', savePreferences);

        const cpfEl = document.getElementById('profileCpf');
        const cepEl = document.getElementById('profileCep');
        const telEl = document.getElementById('profileTelefone');
        const celEl = document.getElementById('profileCelular');
        cpfEl.addEventListener('blur', maskCpfOnBlur);
        cepEl.addEventListener('blur', maskCepOnBlur);
        telEl.addEventListener('blur', maskTelefoneOnBlur);
        celEl.addEventListener('blur', maskCelularOnBlur);
        cpfEl.addEventListener('focus', () => unmaskOnFocus(cpfEl));
        cepEl.addEventListener('focus', () => unmaskOnFocus(cepEl));
        telEl.addEventListener('focus', () => unmaskOnFocus(telEl));
        celEl.addEventListener('focus', () => unmaskOnFocus(celEl));

        document.getElementById('profileCbo').addEventListener('blur', lookupCbo);

        document.querySelectorAll('.toggle-option').forEach(btn => {
            btn.addEventListener('click', () => {
                const group = btn.closest('.toggle-group');
                group.querySelectorAll('.toggle-option').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });

        document.querySelectorAll('#profileForm input').forEach(input => {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    saveProfile();
                }
            });
        });

        document.querySelectorAll('#passwordForm input').forEach(input => {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    savePassword();
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
