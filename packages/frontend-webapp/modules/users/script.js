/**
 * USERS MODULE CONTROLLER
 * Boas Práticas: Component-Driven (UIFactory), Clean Code
 */

class UsersModule {
    constructor() {
        this.tableBody = document.getElementById('userTableBody');
        this.formContainer = document.getElementById('userForm');
        this.modal = document.getElementById('userModal');
        
        this.init();
    }

    init() {
        this.renderTable();
        this.setupForm();
        this.bindEvents();
    }

    renderTable() {
        // Mock data
        const users = [
            { name: 'Admin', email: 'admin@sgi.com', role: 'admin' },
            { name: 'Operador', email: 'op@sgi.com', role: 'operador' }
        ];

        this.tableBody.innerHTML = users.map(user => `
            <tr>
                <td><strong>${user.name}</strong></td>
                <td class="hide-mobile">${user.email}</td>
                <td><span class="badge">${user.role}</span></td>
                <td class="text-right">
                    <button class="btn-icon" aria-label="Editar"><i class="fas fa-edit"></i></button>
                </td>
            </tr>
        `).join('');
    }

    setupForm() {
        // Usando UIFactory para criar campos de forma consistente (Component-Driven)
        const nameField = window.sgi.ui.createInput({
            label: 'Nome Completo',
            id: 'nome',
            placeholder: 'Nome do usuário',
            required: true
        });

        const emailField = window.sgi.ui.createInput({
            label: 'E-mail Corporativo',
            type: 'email',
            id: 'email',
            placeholder: 'email@sgi.com',
            required: true
        });

        this.formContainer.appendChild(nameField);
        this.formContainer.appendChild(emailField);
    }

    bindEvents() {
        document.getElementById('addUserBtn').onclick = () => this.toggleModal(true);
        document.getElementById('closeModal').onclick = () => this.toggleModal(false);
        document.getElementById('btnCancel').onclick = () => this.toggleModal(false);
    }

    toggleModal(show) {
        this.modal.style.display = show ? 'flex' : 'none';
    }
}

// Bootstrap do módulo
document.addEventListener('DOMContentLoaded', () => new UsersModule());
