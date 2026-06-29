/**
 * Módulo de Usuários - Integração Real
 * Consome a API /v1/usuarios da api-postgres.
 */

class UsersController extends window.grindx.controllers.BaseController {
    constructor() {
        super();
        this.tableBody = document.getElementById('userTableBody');
        this.userModal = document.getElementById('userModal');
        this.modalController = new window.grindx.components.ReusableModal(this.userModal, {
            initialFocusSelector: '#nome_completo',
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
            { dataLabel: 'Status', render: user => `<span class="badge ${user.ativo ? 'badge-success' : 'badge-muted'}">${user.ativo ? 'Ativo' : 'Inativo'}</span>` },
            {
                dataLabel: 'Ações',
                className: 'text-right',
                render: user => `
                    <div class="actions-group justify-end">
                        <button class="btn-icon" onclick="window.usersController.editUser('${user.id}')" title="Editar Usuário"><i class="fas fa-edit"></i></button>
                        <button class="btn-icon" onclick="window.usersController.openPermissoes('${user.id}')" title="Permissões"><i class="fas fa-shield-alt"></i></button>
                        ${user.ativo 
                            ? `<button class="btn-icon text-success" onclick="window.usersController.toggleUserStatus('${user.id}', false)" title="Desativar usuário"><i class="fas fa-toggle-on"></i></button>`
                            : `<button class="btn-icon text-muted" onclick="window.usersController.toggleUserStatus('${user.id}', true)" title="Ativar usuário"><i class="fas fa-toggle-off"></i></button>`
                        }
                    </div>
                `
            }
        ]);
        this.users = [];
        this.currentUserId = null;
        
        this.init();
    }

    async init() {
        console.log('Módulo de Usuários Inicializado');
        
        if (!this.requireAuth('../../index.html')) {
            console.error('Token não encontrado no LocalStorage!');
            this.userTable.renderEmpty('Sessão expirada. Faça login novamente.', 4);
            return;
        }

        this.setupForm();
        this.bindEvents();
        await this.loadUsers();
    }

    setupForm() {
        this.userForm.innerHTML = '';

        const fields = [
            { label: 'Nome Completo', id: 'nome_completo', required: true },
            { label: 'E-mail', id: 'email', type: 'email', required: true },
            { label: 'Username', id: 'username', required: true },
            { label: 'Senha', id: 'password', type: 'password', required: true },
        ];

        window.grindx.components.FormField.appendFields(this.userForm, fields);
        this.userForm.appendChild(window.grindx.components.FormField.createSelect({
            id: 'role',
            label: 'Perfil',
            options: window.grindx.constants.USER_ROLES
        }));
    }

    bindEvents() {
        document.getElementById('addUserBtn').onclick = () => {
            this.resetForm();
            this.modalTitle.textContent = 'Cadastrar Usuário';
            this.modalController.open();
        };
        document.getElementById('btnCancel').onclick = () => this.modalController.close();
        document.getElementById('btnSave').onclick = () => this.saveUser();

        document.getElementById('btnCancelPermissoes').onclick = () => this.permissoesController.close();
        document.getElementById('btnSavePermissoes').onclick = () => this.savePermissoes();
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
            console.log('Solicitando listagem de usuários...');
            const result = await window.grindx.api.get('/usuarios');
            console.log('Dados recebidos:', result);

            if (result && Array.isArray(result.items)) {
                this.users = result.items; // Guardar no estado
                this.renderTableOrEmpty();
            } else {
                console.warn('Formato de dados inesperado:', result);
                this.userTable.renderEmpty('Nenhum usuário encontrado.', 5);
            }
        } catch (err) {
            console.error('Falha no loadUsers:', err);
            this.userTable.renderEmpty(window.grindx.components.LoadingSpinner.toUserMessage(err), 5);
        }
    }

    renderTable(users) {
        this.userTable.render(users);
    }

    editUser(id) {
        // Encontrar usuário nos dados carregados (seria melhor via API se dados parciais, mas aqui ok)
        // Como não temos a lista guardada no state, vamos buscar do DOM ou recarregar.
        // Melhorei o controller para guardar 'this.users' no loadUsers.
        const user = this.users.find(u => u.id == id);
        if (!user) return;

        this.currentUserId = id;
        this.modalTitle.textContent = 'Editar Usuário';
        
        document.getElementById('nome_completo').value = user.nome_completo;
        document.getElementById('email').value = user.email;
        document.getElementById('username').value = user.username;
        document.getElementById('password').value = ''; // Senha em branco por segurança
        document.getElementById('role').value = user.role;

        this.modalController.open();
    }

    async deleteUser(id) {
        if (!confirm('Tem certeza que deseja excluir este usuário?')) return;
        try {
            await window.grindx.api.delete(`/usuarios/${id}`);
            this.users = this.users.filter(user => String(user.id) !== String(id));
            this.renderTableOrEmpty();
            this.toastSuccess('Usuário excluído com sucesso.');
        } catch (err) {
            this.toastError(err);
        }
    }

    async toggleUserStatus(id, novoStatus) {
        try {
            const updatedUser = await window.grindx.api.put(`/usuarios/${id}`, { ativo: novoStatus });
            this.upsertUser(updatedUser);
            this.renderTableOrEmpty();
            this.toastSuccess(`Usuário ${novoStatus ? 'ativado' : 'desativado'} com sucesso.`);
        } catch (err) {
            this.toastError(err);
        }
    }

    async saveUser() {
        if (!this.validateUserForm()) return;

        const formData = {
            nome_completo: document.getElementById('nome_completo').value,
            email: document.getElementById('email').value,
            username: document.getElementById('username').value,
            password: document.getElementById('password').value,
            role: document.getElementById('role').value,
            ativo: true
        };

        try {
            if (this.currentUserId) {
                const updatedUser = await window.grindx.api.put(`/usuarios/${this.currentUserId}`, formData);
                this.upsertUser(updatedUser);
            } else {
                const createdUser = await window.grindx.api.post('/usuarios', formData);
                this.upsertUser(createdUser);
            }

            this.toastSuccess('Usuário salvo com sucesso.');
            this.modalController.close();
            this.renderTableOrEmpty();
        } catch (err) {
            this.toastError(err);
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

    validateUserForm() {
        const schemaName = this.currentUserId ? 'userUpdate' : 'userCreate';
        const result = window.grindx.validation.validateSchema(schemaName);

        if (!result.valid) {
            window.grindx.components.LoadingSpinner.toast('Revise os campos destacados.', 'warning');
        }

        return result.valid;
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
            console.error('Falha ao carregar permissões:', err);
            container.innerHTML = '<p class="text-danger">Erro ao carregar permissões.</p>';
        }
    }

    async savePermissoes() {
        const checkboxes = document.querySelectorAll('#permissoesContent input[name="modulo"]:checked');
        const moduloIds = Array.from(checkboxes).map(cb => parseInt(cb.value));

        try {
            await window.grindx.api.put(`/usuarios/${this.currentUserId}/modulos`, { modulo_ids: moduloIds });
            this.toastSuccess('Permissões atualizadas com sucesso.');
            this.permissoesController.close();
        } catch (err) {
            this.toastError(err);
        }
    }

    resetForm() {
        this.currentUserId = null;
        window.grindx.validation.clearForm(this.userForm);
        this.userForm.reset();
    }
}

// Expor para o escopo global para os botões inline (onclick)
document.addEventListener('DOMContentLoaded', () => {
    window.usersController = new UsersController();
});
