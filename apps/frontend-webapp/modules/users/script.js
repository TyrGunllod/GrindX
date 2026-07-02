class UsersController extends window.grindx.controllers.BaseController {
    constructor() {
        super();
        this.tableBody = document.getElementById('userTableBody');
        this.userModal = document.getElementById('userModal');
        this.modalController = new window.grindx.components.ReusableModal(this.userModal, {
            initialFocusSelector: '#userNomeCompleto',
            onClose: () => this.resetForm()
        });

        this.permissoesModal = document.getElementById('permissoesModal');
        this.permissoesController = new window.grindx.components.ReusableModal(this.permissoesModal);

        this.userForm = document.getElementById('userForm');
        this.modalTitle = document.getElementById('modalTitle');
        this.userTable = new window.grindx.components.DataTable(this.tableBody, [
            {
                dataLabel: 'Usuário',
                render: user => `
                    <div class="flex items-center gap-2">
                        <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(user.nome_completo)}&background=4f46e5&color=fff&bold=true" class="avatar-mini" alt="">
                        <strong>${user.nome_completo}</strong>
                    </div>
                `
            },
            { className: 'hide-mobile', dataLabel: 'E-mail', render: user => user.email },
            { dataLabel: 'Perfil', render: user => `<span class="badge role-${user.role}">${user.role.toUpperCase()}</span>` },
            {
                dataLabel: 'Status',
                render: user => `
                    <span class="badge ${user.ativo ? 'badge-success' : 'badge-muted'}" 
                          style="cursor:pointer" 
                          onclick="window.usersController.toggleUserStatus('${user.id}', ${!user.ativo})" 
                          title="${user.ativo ? 'Clique para desativar' : 'Clique para ativar'}">
                        ${user.ativo ? 'Ativo' : 'Inativo'}
                    </span>
                `
            },
            {
                dataLabel: 'Ações',
                className: 'text-right',
                render: user => `
                    <div class="actions-group justify-end">
                        <button class="btn-icon" onclick="window.usersController.editUser('${user.id}')" title="Editar Usuário"><i class="fas fa-edit"></i></button>
                        <button class="btn-icon" onclick="window.usersController.openPermissoes('${user.id}')" title="Permissões"><i class="fas fa-shield-alt"></i></button>
                    </div>
                `
            }
        ]);
        this.users = [];
        this.currentUserId = null;
        this.autoGenUsername = true;

        this.init();
    }

    async init() {
        console.log('Módulo de Usuários Inicializado');

        if (!this.requireAuth('../../index.html')) {
            console.error('Token não encontrado no LocalStorage!');
            this.userTable.renderEmpty('Sessão expirada. Faça login novamente.', 4);
            return;
        }

        this.populateRoleSelect();
        this.bindEvents();
        await this.loadUsers();
    }

    populateRoleSelect() {
        const sel = document.getElementById('userRole');
        sel.innerHTML = '';
        window.grindx.constants.USER_ROLES
            .filter(r => r.value !== 'admin')
            .forEach(r => {
                const opt = document.createElement('option');
                opt.value = r.value;
                opt.textContent = r.label;
                sel.appendChild(opt);
            });
    }

    bindEvents() {
        document.getElementById('addUserBtn').onclick = () => {
            this.resetForm();
            this.modalTitle.textContent = 'Cadastrar Usuário';
            document.getElementById('passwordHint').style.display = 'block';
            document.getElementById('userPassword').required = true;
            this.modalController.open();
        };
        document.getElementById('btnCancel').onclick = () => this.modalController.close();
        document.getElementById('btnSave').onclick = () => this.saveUser();

        document.getElementById('btnCancelPermissoes').onclick = () => this.permissoesController.close();
        document.getElementById('btnSavePermissoes').onclick = () => this.savePermissoes();

        const nomeField = document.getElementById('userNomeCompleto');
        const usernameField = document.getElementById('userUsername');
        nomeField.addEventListener('input', () => {
            if (this.autoGenUsername) {
                usernameField.value = this.gerarUsername(nomeField.value);
            }
        });
        usernameField.addEventListener('focus', () => {
            this.autoGenUsername = false;
        });
        usernameField.addEventListener('blur', () => {
            if (!usernameField.value) this.autoGenUsername = true;
        });

        this.setupFieldMasks();
    }

    gerarUsername(nomeCompleto) {
        if (!nomeCompleto || !nomeCompleto.trim()) return '';
        const conectivos = new Set(['do', 'da', 'de', 'dos', 'das', 'e']);
        const partes = nomeCompleto.trim().toLowerCase().split(/\s+/).filter(Boolean);
        if (partes.length === 0) return '';

        const primeiroNome = partes[0];
        const iniciais = partes.slice(1)
            .filter(p => !conectivos.has(p))
            .map(p => p[0] || '')
            .join('');

        return primeiroNome + iniciais;
    }

    setupFieldMasks() {
        const cpfEl = document.getElementById('userCpf');
        const cepEl = document.getElementById('userCep');
        const telEl = document.getElementById('userTelefone');
        const celEl = document.getElementById('userCelular');
        const rgEl = document.getElementById('userRg');
        const salarioEl = document.getElementById('userSalario');
        const cboEl = document.getElementById('userCbo');
        const cargoEl = document.getElementById('userCargo');

        cpfEl.addEventListener('blur', () => { if (cpfEl.value) cpfEl.value = this.formatCpf(cpfEl.value); });
        cepEl.addEventListener('blur', () => { if (cepEl.value) cepEl.value = this.formatCep(cepEl.value); this.lookupCep(); });
        telEl.addEventListener('blur', () => { if (telEl.value) telEl.value = this.formatFone(telEl.value, false); });
        celEl.addEventListener('blur', () => { if (celEl.value) celEl.value = this.formatFone(celEl.value, true); });
        rgEl.addEventListener('blur', () => { if (rgEl.value) rgEl.value = this.formatRg(rgEl.value); });
        salarioEl.addEventListener('blur', () => { if (salarioEl.value) salarioEl.value = this.formatSalario(salarioEl.value); });

        cpfEl.addEventListener('focus', () => { cpfEl.value = this.stripMask(cpfEl.value); });
        cepEl.addEventListener('focus', () => { cepEl.value = this.stripMask(cepEl.value); });
        telEl.addEventListener('focus', () => { telEl.value = this.stripMask(telEl.value); });
        celEl.addEventListener('focus', () => { celEl.value = this.stripMask(celEl.value); });
        rgEl.addEventListener('focus', () => { rgEl.value = this.stripMask(rgEl.value); });
        salarioEl.addEventListener('focus', () => { salarioEl.value = this.unformatSalario(salarioEl.value); });

        cboEl.addEventListener('blur', () => this.lookupCbo());
        document.getElementById('searchUserCboBtn').addEventListener('click', () => this.lookupCbo());
        document.getElementById('searchUserCepBtn').addEventListener('click', () => this.lookupCep());

        const focusable = document.querySelectorAll('#userForm input, #userForm select, #userForm button, .modal-dialog input');
        focusable.forEach(el => {
            el.addEventListener('keydown', (e) => {
                if (e.key !== 'Enter') return;
                e.preventDefault();
                if (el.id === 'userCbo') this.lookupCbo();
                if (el.id === 'userCep') this.lookupCep();
                let next = false;
                for (const f of focusable) {
                    if (f.disabled) continue;
                    if (next) { f.focus(); break; }
                    if (f === el) next = true;
                }
            });
        });
    }

    async lookupCbo() {
        const cboEl = document.getElementById('userCbo');
        const cargoEl = document.getElementById('userCargo');
        const cbo = cboEl.value.replace(/\D/g, '').slice(0, 6);
        if (cbo.length < 4) return;
        try {
            const xml = await window.grindx.api.get('/cbo/' + cbo);
            const parser = new DOMParser();
            const doc = parser.parseFromString(xml, 'text/xml');
            const desc = doc.querySelector('descricao');
            if (desc && desc.textContent) {
                cargoEl.value = desc.textContent;
            } else {
                this.showToast('CBO não encontrado.', 'error');
            }
        } catch (e) {
            this.showToast('Erro ao consultar CBO.', 'error');
        }
    }

    async lookupCep() {
        const cepEl = document.getElementById('userCep');
        const cep = cepEl.value.replace(/\D/g, '').slice(0, 8);
        if (cep.length < 8) return;
        try {
            const data = await window.grindx.api.get('/cep/' + cep);
            if (data.logradouro) document.getElementById('userEndereco').value = data.logradouro;
            if (data.bairro) document.getElementById('userBairro').value = data.bairro;
            if (data.localidade) document.getElementById('userCidade').value = data.localidade;
            if (data.uf) document.getElementById('userUf').value = data.uf;
            if (!data.logradouro) this.showToast('CEP não encontrado.', 'error');
        } catch (e) {
            this.showToast('Erro ao consultar CEP.', 'error');
        }
    }

    formatCpf(v) {
        const d = v.replace(/\D/g, '').slice(0, 11);
        if (d.length <= 3) return d;
        if (d.length <= 6) return d.slice(0, 3) + '.' + d.slice(3);
        if (d.length <= 9) return d.slice(0, 3) + '.' + d.slice(3, 6) + '.' + d.slice(6);
        return d.slice(0, 3) + '.' + d.slice(3, 6) + '.' + d.slice(6, 9) + '-' + d.slice(9, 11);
    }

    formatCep(v) {
        const d = v.replace(/\D/g, '').slice(0, 8);
        if (d.length <= 5) return d;
        return d.slice(0, 5) + '-' + d.slice(5);
    }

    formatFone(v, isCelular) {
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

    formatRg(v) {
        const d = v.replace(/\D/g, '').slice(0, 9);
        if (d.length <= 2) return d;
        if (d.length <= 5) return d.slice(0, 2) + '.' + d.slice(2);
        if (d.length <= 8) return d.slice(0, 2) + '.' + d.slice(2, 5) + '.' + d.slice(5);
        return d.slice(0, 2) + '.' + d.slice(2, 5) + '.' + d.slice(5, 8) + '-' + d.slice(8);
    }

    formatSalario(v) {
        if (!v) return '';
        const parts = v.replace(',', '.').split('.');
        const num = parseInt(parts[0], 10) || 0;
        const dec = parts.length > 1 ? parts[1].slice(0, 2).padEnd(2, '0') : '00';
        return num.toLocaleString('pt-BR') + ',' + dec;
    }

    unformatSalario(v) {
        return v.replace(/\./g, '').replace(',', '.');
    }

    stripMask(v) {
        return v.replace(/\D/g, '');
    }

    showToast(message, type) {
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

    async loadUsers() {
        this.tableBody.innerHTML = `
            <tr>
                <td colspan="5"></td>
            </tr>
        `;
        const loadingCell = this.tableBody.querySelector('td');
        loadingCell.appendChild(window.grindx.components.LoadingSpinner.create('Carregando usuários...'));

        try {
            const result = await window.grindx.api.get('/usuarios', { exclude_role: 'admin' });

            if (result && Array.isArray(result.items)) {
                this.users = result.items;
                this.renderTableOrEmpty();
            } else {
                this.userTable.renderEmpty('Nenhum usuário encontrado.', 5);
            }
        } catch (err) {
            this.userTable.renderEmpty(window.grindx.components.LoadingSpinner.toUserMessage(err), 5);
        }
    }

    renderTable(users) {
        this.userTable.render(users);
    }

    editUser(id) {
        const user = this.users.find(u => u.id == id);
        if (!user) return;

        this.currentUserId = id;
        this.autoGenUsername = false;
        this.modalTitle.textContent = 'Editar Usuário';
        document.getElementById('passwordHint').style.display = 'block';
        document.getElementById('userPassword').required = false;

        document.getElementById('userUsername').value = user.username || '';
        document.getElementById('userRole').value = user.role || 'leitura';
        document.getElementById('userNomeCompleto').value = user.nome_completo || '';
        document.getElementById('userEmail').value = user.email || '';
        document.getElementById('userPassword').value = '';
        document.getElementById('userCodigo').value = user.codigo || '';
        document.getElementById('userCbo').value = user.cbo || '';
        document.getElementById('userSalario').value = user.salario ? this.formatSalario(user.salario) : '';
        document.getElementById('userDepartamento').value = user.departamento || '';
        document.getElementById('userCargo').value = user.cargo || '';
        document.getElementById('userClassificacao').value = user.classificacao || '';
        document.getElementById('userCpf').value = user.cpf ? this.formatCpf(user.cpf) : '';
        document.getElementById('userRg').value = user.rg ? this.formatRg(user.rg) : '';
        document.getElementById('userEndereco').value = user.endereco || '';
        document.getElementById('userNumero').value = user.numero || '';
        document.getElementById('userCep').value = user.cep ? this.formatCep(user.cep) : '';
        document.getElementById('userBairro').value = user.bairro || '';
        document.getElementById('userCidade').value = user.cidade || '';
        document.getElementById('userUf').value = user.uf || '';
        document.getElementById('userTelefone').value = user.telefone ? this.formatFone(user.telefone, false) : '';
        document.getElementById('userCelular').value = user.celular ? this.formatFone(user.celular, true) : '';

        this.modalController.open();
    }

    async saveUser() {
        if (!this.validateUserForm()) return;

        const getVal = (id) => {
            const el = document.getElementById(id);
            return el ? el.value.trim() : '';
        };

        const formData = {
            nome_completo: getVal('userNomeCompleto'),
            email: getVal('userEmail'),
            username: getVal('userUsername'),
            role: getVal('userRole'),
            codigo: getVal('userCodigo'),
            cbo: getVal('userCbo'),
            departamento: getVal('userDepartamento'),
            cargo: getVal('userCargo'),
            classificacao: getVal('userClassificacao'),
            endereco: getVal('userEndereco'),
            numero: getVal('userNumero'),
            bairro: getVal('userBairro'),
            cidade: getVal('userCidade'),
            uf: getVal('userUf'),
        };

        const cpf = this.stripMask(getVal('userCpf'));
        const cep = this.stripMask(getVal('userCep'));
        const telefone = this.stripMask(getVal('userTelefone'));
        const celular = this.stripMask(getVal('userCelular'));
        const rg = this.stripMask(getVal('userRg'));
        let salario = getVal('userSalario');

        if (cpf) formData.cpf = cpf;
        if (cep) formData.cep = cep;
        if (telefone) formData.telefone = telefone;
        if (celular) formData.celular = celular;
        if (rg) formData.rg = rg;
        if (salario) formData.salario = this.unformatSalario(salario);

        const password = getVal('userPassword');
        if (password) formData.password = password;

        try {
            if (this.currentUserId) {
                const updatedUser = await window.grindx.api.put(`/usuarios/${this.currentUserId}`, formData);
                this.upsertUser(updatedUser);
            } else {
                formData.ativo = true;
                const createdUser = await window.grindx.api.post('/usuarios', formData);
                this.upsertUser(createdUser);
            }

            this.showToast('Usuário salvo com sucesso.', 'success');
            this.modalController.close();
            this.renderTableOrEmpty();
        } catch (err) {
            this.handleSaveError(err);
        }
    }

    handleSaveError(err) {
        const msg = err.message || err.detail || 'Erro ao salvar usuário.';
        this.showToast(msg, 'error');
    }

    validateUserForm() {
        const username = document.getElementById('userUsername').value.trim();
        if (!username || username.length < 3) {
            this.showToast('Nome de usuário deve ter no mínimo 3 caracteres.', 'warning');
            return false;
        }
        const nome = document.getElementById('userNomeCompleto').value.trim();
        if (!nome || nome.length < 2) {
            this.showToast('Nome completo é obrigatório.', 'warning');
            return false;
        }
        const email = document.getElementById('userEmail').value.trim();
        if (!email || !email.includes('@')) {
            this.showToast('E-mail inválido.', 'warning');
            return false;
        }
        const password = document.getElementById('userPassword').value;
        if (!this.currentUserId && (!password || password.length < 6)) {
            this.showToast('Senha deve ter no mínimo 6 caracteres.', 'warning');
            return false;
        }
        return true;
    }

    async toggleUserStatus(id, novoStatus) {
        try {
            const updatedUser = await window.grindx.api.put(`/usuarios/${id}`, { ativo: novoStatus });
            this.upsertUser(updatedUser);
            this.renderTableOrEmpty();
            this.showToast(`Usuário ${novoStatus ? 'ativado' : 'desativado'} com sucesso.`, 'success');
        } catch (err) {
            this.showToast(err.message || 'Erro ao alterar status.', 'error');
        }
    }

    upsertUser(user) {
        if (!user?.id) return;
        const index = this.users.findIndex(item => String(item.id) === String(user.id));
        if (index >= 0) {
            this.users[index] = user;
        } else {
            this.users = [user, ...this.users];
        }
    }

    renderTableOrEmpty() {
        if (this.users.length) {
            this.renderTable(this.users);
            return;
        }
        this.userTable.renderEmpty('Nenhum usuário encontrado.', 5);
    }

    resetForm() {
        this.currentUserId = null;
        this.autoGenUsername = true;
        this.userForm.reset();
        document.getElementById('userRole').value = 'leitura';
        document.getElementById('userCargo').value = '';
        document.getElementById('userClassificacao').value = '';
        document.getElementById('userEndereco').value = '';
        document.getElementById('userBairro').value = '';
        document.getElementById('userCidade').value = '';
        document.getElementById('userUf').value = '';
        document.getElementById('passwordHint').style.display = 'none';
        const errorEls = document.querySelectorAll('.field-error');
        errorEls.forEach(el => el.style.display = 'none');
    }

    async openPermissoes(id) {
        this.currentUserId = id;
        const container = document.getElementById('permissoesContent');
        container.innerHTML = '<p>Carregando permissões...</p>';
        this.permissoesController.open();

        try {
            const [userModulos, menu] = await Promise.all([
                window.grindx.api.get(`/usuarios/${id}/modulos`),
                window.grindx.api.get('/portal/menu')
            ]);

            const liberados = new Set(userModulos.modulos || []);

            const renderModulo = (mod, depth = 0) => {
                const checked = liberados.has(mod.id) ? 'checked' : '';
                const isAdminOnly = mod.role_minima === 'admin';
                const badge = isAdminOnly ? ' <span class="badge badge-admin-only">Admin</span>' : '';
                return `
                    <label class="perm-checkbox ${depth > 0 ? 'perm-checkbox-child' : ''}">
                        <input type="checkbox" name="modulo" value="${mod.id}" ${checked}>
                        <i class="${mod.icone || 'fas fa-cube'}"></i>
                        <span>${mod.nome}</span>
                        ${badge}
                    </label>
                `;
            };

            const renderChildren = (children) => {
                return children.map(child => {
                    const childMods = (child.modulos || []).map(m => renderModulo(m, 1)).join('');
                    const sub = renderChildren(child.children || []);
                    if (!childMods && !sub) return '';
                    return `
                        <div class="perm-subgroup">
                            <div class="perm-subgroup-header">
                                <i class="${child.icone || 'fas fa-folder'}"></i>
                                <span>${child.nome}</span>
                            </div>
                            <div class="perm-modules">${childMods}${sub}</div>
                        </div>
                    `;
                }).join('');
            };

            let html = '<div class="perm-container">';
            menu.forEach(aba => {
                const directMods = (aba.modulos || []).map(m => renderModulo(m)).join('');
                const childrenHtml = renderChildren(aba.children || []);
                const totalMods = (aba.modulos || []).length
                    + (aba.children || []).reduce((acc, c) => acc + (c.modulos || []).length, 0);
                const checkedCount = (aba.modulos || []).filter(m => liberados.has(m.id)).length;
                const allChecked = totalMods > 0 && checkedCount === totalMods;

                html += `
                    <div class="perm-aba">
                        <div class="perm-aba-header">
                            <div class="perm-aba-title">
                                <i class="${aba.icone || 'fas fa-folder'}"></i>
                                <span>${aba.nome}</span>
                            </div>
                            <label class="perm-toggle-label" title="${allChecked ? 'Limpar todos' : 'Selecionar todos'}">
                                <input type="checkbox" class="perm-aba-toggle" ${allChecked ? 'checked' : ''}>
                                <span class="perm-toggle-text">${allChecked ? 'Limpar' : 'Selecionar todos'}</span>
                            </label>
                        </div>
                        <div class="perm-modules">
                            ${directMods}
                            ${childrenHtml}
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            container.innerHTML = html;

            container.querySelectorAll('.perm-aba-toggle').forEach(cb => {
                cb.addEventListener('change', function () {
                    const abaCard = this.closest('.perm-aba');
                    abaCard.querySelectorAll('input[name="modulo"]').forEach(m => m.checked = this.checked);
                    const txt = this.closest('.perm-toggle-label').querySelector('.perm-toggle-text');
                    txt.textContent = this.checked ? 'Limpar' : 'Selecionar todos';
                });
            });
        } catch (err) {
            container.innerHTML = '<p class="text-danger">Erro ao carregar permissões.</p>';
        }
    }

    async savePermissoes() {
        const checkboxes = document.querySelectorAll('#permissoesContent input[name="modulo"]:checked');
        const moduloIds = Array.from(checkboxes).map(cb => parseInt(cb.value));

        try {
            await window.grindx.api.put(`/usuarios/${this.currentUserId}/modulos`, { modulo_ids: moduloIds });
            this.showToast('Permissões atualizadas com sucesso.', 'success');
            this.permissoesController.close();
        } catch (err) {
            this.showToast(err.message || 'Erro ao salvar permissões.', 'error');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.usersController = new UsersController();
});