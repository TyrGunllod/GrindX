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
                render: user => `
                    <div class="flex items-center gap-2">
                        <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(user.nome_completo)}&background=4f46e5&color=fff&bold=true" class="avatar-mini" alt="">
                        <strong>${user.nome_completo}</strong>
                    </div>
                `
            },
            { className: 'hide-mobile', render: user => user.email },
            { render: user => `<span class="badge role-${user.role}">${user.role.toUpperCase()}</span>` },
            { render: user => `<span class="badge ${user.ativo ? 'badge-success' : 'badge-muted'}">${user.ativo ? 'Ativo' : 'Inativo'}</span>` },
            {
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
        document.getElementById('btnRefresh').onclick = () => this.loadUsers();
        document.getElementById('addUserBtn').onclick = () => this.modalController.open();
        document.getElementById('closeModal').onclick = () => this.modalController.close();
        document.getElementById('btnCancel').onclick = () => this.modalController.close();
        document.getElementById('btnSave').onclick = () => this.saveUser();

        document.getElementById('closePermissoesModal').onclick = () => this.permissoesController.close();
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
            const result = await window.grindx.api.get('/v1/usuarios');
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
            await window.grindx.api.delete(`/v1/usuarios/${id}`);
            this.users = this.users.filter(user => String(user.id) !== String(id));
            this.renderTableOrEmpty();
            this.toastSuccess('Usuário excluído com sucesso.');
        } catch (err) {
            this.toastError(err);
        }
    }

    async toggleUserStatus(id, novoStatus) {
        try {
            const updatedUser = await window.grindx.api.put(`/v1/usuarios/${id}`, { ativo: novoStatus });
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
                const updatedUser = await window.grindx.api.put(`/v1/usuarios/${this.currentUserId}`, formData);
                this.upsertUser(updatedUser);
            } else {
                const createdUser = await window.grindx.api.post('/v1/usuarios', formData);
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
            // Busca módulos do usuário e menu completo
            const [userModulos, menu] = await Promise.all([
                window.grindx.api.get(`/v1/usuarios/${id}/modulos`),
                window.grindx.api.get('/v1/portal/menu') // Assumindo que este endpoint existe e retorna tudo para admin ou já foi filtrado no backend para admin
            ]);

            const liberados = userModulos.modulos || [];
            
            // Renderiza checkboxes agrupados
            let html = '<div class="grid grid-1 gap-4">';
            menu.forEach(aba => {
                html += `<div><strong>${aba.nome}</strong><div class="grid grid-md-2 gap-2 mt-2">`;
                aba.modulos.forEach(mod => {
                    const checked = liberados.includes(mod.id) ? 'checked' : '';
                    html += `
                        <label class="flex items-center gap-2">
                            <input type="checkbox" name="modulo" value="${mod.id}" ${checked}>
                            ${mod.nome}
                        </label>
                    `;
                });
                html += '</div></div>';
            });
            html += '</div>';
            container.innerHTML = html;
        } catch (err) {
            console.error('Falha ao carregar permissões:', err);
            container.innerHTML = '<p class="text-danger">Erro ao carregar permissões.</p>';
        }
    }

    async savePermissoes() {
        const checkboxes = document.querySelectorAll('#permissoesContent input[name="modulo"]:checked');
        const moduloIds = Array.from(checkboxes).map(cb => parseInt(cb.value));

        try {
            await window.grindx.api.put(`/v1/usuarios/${this.currentUserId}/modulos`, { modulo_ids: moduloIds });
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
