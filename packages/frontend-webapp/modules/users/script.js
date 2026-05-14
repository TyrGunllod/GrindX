/**
 * Módulo de Usuários - Integração Real
 * Consome a API /v1/usuarios da api-postgres.
 */

const API_BASE_URL = window.sgi.config.API_BASE_URL;

class UsersController {
    constructor() {
        this.tableBody = document.getElementById('userTableBody');
        this.userModal = document.getElementById('userModal');
        this.userForm = document.getElementById('userForm');
        this.token = localStorage.getItem('access_token');
        
        this.init();
    }

    async init() {
        console.log('Módulo de Usuários Inicializado');
        
        // Garantir que pegamos o token mais atualizado
        this.token = localStorage.getItem('access_token');
        
        if (!this.token) {
            console.error('Token não encontrado no LocalStorage!');
            this.tableBody.innerHTML = `<tr><td colspan="4" class="text-error">Sessão expirada. Faça login novamente.</td></tr>`;
            return;
        }

        this.setupForm();
        this.bindEvents();
        await this.loadUsers();
    }

    setupForm() {
        // Limpar form
        this.userForm.innerHTML = '';

        // Usar UIFactory para criar campos (SOLID)
        const fields = [
            { label: 'Nome Completo', id: 'nome_completo', required: true },
            { label: 'E-mail', id: 'email', type: 'email', required: true },
            { label: 'Username', id: 'username', required: true },
            { label: 'Senha', id: 'password', type: 'password', required: true },
        ];

        fields.forEach(f => {
            this.formContainer = this.userForm;
            const input = window.sgi.ui.createInput(f);
            this.userForm.appendChild(input);
        });

        // Campo Role (Select manual por enquanto)
        const roleGroup = document.createElement('div');
        roleGroup.className = 'form-group';
        roleGroup.innerHTML = `
            <label for="role">Perfil</label>
            <select id="role" class="form-control">
                <option value="leitura">Leitura</option>
                <option value="operador">Operador</option>
                <option value="admin">Administrador</option>
            </select>
        `;
        this.userForm.appendChild(roleGroup);
    }

    bindEvents() {
        document.getElementById('btnRefresh').onclick = () => this.loadUsers();
        document.getElementById('addUserBtn').onclick = () => this.openModal();
        document.getElementById('closeModal').onclick = () => this.closeModal();
        document.getElementById('btnCancel').onclick = () => this.closeModal();
        document.getElementById('btnSave').onclick = () => this.saveUser();
    }

    async loadUsers() {
        try {
            console.log('Solicitando listagem de usuários...');
            const response = await fetch(`${API_BASE_URL}/usuarios`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Erro da API:', errorData);
                throw new Error(errorData.message || 'Erro ao carregar usuários');
            }

            const result = await response.json();
            console.log('Dados recebidos:', result);

            if (result && Array.isArray(result.items)) {
                this.renderTable(result.items);
            } else {
                console.warn('Formato de dados inesperado:', result);
                this.tableBody.innerHTML = `<tr><td colspan="4" class="text-center">Nenhum usuário encontrado.</td></tr>`;
            }
        } catch (err) {
            console.error('Falha no loadUsers:', err);
            this.tableBody.innerHTML = `<tr><td colspan="4" class="text-error" style="color:red; text-align:center; padding: 20px;">
                Erro: ${err.message}
            </td></tr>`;
        }
    }

    renderTable(users) {
        this.tableBody.innerHTML = users.map(user => `
            <tr>
                <td>
                    <div class="flex items-center gap-2">
                        <img src="https://ui-avatars.com/api/?name=${user.nome_completo}&background=random" class="avatar-mini" alt="">
                        <strong>${user.nome_completo}</strong>
                    </div>
                </td>
                <td class="hide-mobile">${user.email}</td>
                <td><span class="badge role-${user.role}">${user.role.toUpperCase()}</span></td>
                <td class="text-right">
                    <button class="btn-icon" onclick="alert('Editar ID: ${user.id}')"><i class="fas fa-edit"></i></button>
                    <button class="btn-icon text-danger" onclick="alert('Desativar ID: ${user.id}')"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `).join('');
    }

    async saveUser() {
        const formData = {
            nome_completo: document.getElementById('nome_completo').value,
            email: document.getElementById('email').value,
            username: document.getElementById('username').value,
            password: document.getElementById('password').value,
            role: document.getElementById('role').value,
            ativo: true
        };

        try {
            const response = await fetch(`${API_BASE_URL}/usuarios`, {
                method: 'POST',
                headers: { 
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Erro ao salvar');
            }

            alert('Usuário criado com sucesso!');
            this.closeModal();
            await this.loadUsers();
        } catch (err) {
            alert(err.message);
        }
    }

    openModal() { this.userModal.style.display = 'flex'; }
    closeModal() { this.userModal.style.display = 'none'; }
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => new UsersController());
