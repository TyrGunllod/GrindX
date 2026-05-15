/**
 * Módulo de Usuários - Integração Real
 * Consome a API /v1/usuarios da api-postgres.
 */

class UsersController {
    constructor() {
        this.tableBody = document.getElementById('userTableBody');
        this.userModal = document.getElementById('userModal');
        this.modalController = new window.grindx.components.ReusableModal(this.userModal, {
            initialFocusSelector: '#nome_completo',
            onClose: () => this.resetForm()
        });
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
            {
                className: 'text-right',
                render: user => `
                    <div class="actions-group justify-end">
                        <button class="btn-icon" onclick="window.usersController.editUser('${user.id}')" title="Editar Usuário"><i class="fas fa-edit"></i></button>
                        <button class="btn-icon text-danger" onclick="window.usersController.deleteUser('${user.id}')" title="Excluir Usuário"><i class="fas fa-trash"></i></button>
                    </div>
                `
            }
        ]);
        this.token = localStorage.getItem('access_token');
        this.currentUserId = null;
        
        this.init();
    }

    async init() {
        console.log('Módulo de Usuários Inicializado');
        
        // Garantir que pegamos o token mais atualizado
        this.token = localStorage.getItem('access_token');
        
        if (!this.token) {
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
        document.getElementById('addUserBtn').onclick = () => this.openModal();
        document.getElementById('closeModal').onclick = () => this.closeModal();
        document.getElementById('btnCancel').onclick = () => this.closeModal();
        document.getElementById('btnSave').onclick = () => this.saveUser();
    }

    async loadUsers() {
        this.tableBody.innerHTML = `
            <tr>
                <td colspan="4"></td>
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
                if (this.users.length) {
                    this.renderTable(this.users);
                } else {
                    this.userTable.renderEmpty('Nenhum usuário encontrado.', 4);
                }
            } else {
                console.warn('Formato de dados inesperado:', result);
                this.userTable.renderEmpty('Nenhum usuário encontrado.', 4);
            }
        } catch (err) {
            console.error('Falha no loadUsers:', err);
            this.userTable.renderEmpty(window.grindx.components.LoadingSpinner.toUserMessage(err), 4);
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

        this.openModal();
    }

    async deleteUser(id) {
        if (!confirm('Tem certeza que deseja excluir este usuário?')) return;
        try {
            await window.grindx.api.delete(`/usuarios/${id}`);
            window.grindx.components.LoadingSpinner.toast('Usuário excluído com sucesso.', 'success');
            await this.loadUsers();
        } catch (err) {
            window.grindx.components.LoadingSpinner.toast(
                window.grindx.components.LoadingSpinner.toUserMessage(err),
                'error'
            );
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
                await window.grindx.api.put(`/usuarios/${this.currentUserId}`, formData);
            } else {
                await window.grindx.api.post('/usuarios', formData);
            }

            window.grindx.components.LoadingSpinner.toast('Usuário salvo com sucesso.', 'success');
            this.closeModal();
            await this.loadUsers();
        } catch (err) {
            window.grindx.components.LoadingSpinner.toast(
                window.grindx.components.LoadingSpinner.toUserMessage(err),
                'error'
            );
        }
    }

    validateUserForm() {
        const passwordRules = this.currentUserId
            ? []
            : [{ id: 'password', required: true, minLength: 6, message: 'Informe uma senha.' }];
        const result = window.grindx.validation.validateRules([
            { id: 'nome_completo', required: true, message: 'Informe o nome completo.' },
            { id: 'email', required: true, email: true, message: 'Informe o e-mail.' },
            { id: 'username', required: true, minLength: 3, message: 'Informe o username.' },
            ...passwordRules,
            { id: 'role', required: true, message: 'Selecione o perfil.' }
        ]);

        if (!result.valid) {
            window.grindx.components.LoadingSpinner.toast('Revise os campos destacados.', 'warning');
        }

        return result.valid;
    }

    openModal() { 
        if (!this.currentUserId) {
            this.modalTitle.textContent = 'Cadastrar Usuário';
            this.userForm.reset();
        }
        this.modalController.open();
    }
    closeModal() { 
        this.modalController.close();
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
