/**
 * Módulo de Gestão de Estrutura - Versão Full CRUD
 * Gerencia Abas e Módulos com Edição e Exclusão.
 */

const API_BASE_URL = 'http://localhost:8002/v1';

class StructureController {
    constructor() {
        this.container = document.getElementById('structureContainer');
        this.token = localStorage.getItem('access_token');
        
        // Modais
        this.abaModal = document.getElementById('abaModal');
        this.moduloModal = document.getElementById('moduloModal');
        
        // Forms
        this.abaForm = document.getElementById('abaForm');
        this.moduloForm = document.getElementById('moduloForm');

        // Estado de Edição
        this.currentAbaId = null;
        this.currentModuloId = null;
        
        this.init();
    }

    async init() {
        if (!this.token) return;
        this.setupForms();
        this.bindEvents();
        await this.loadStructure();
    }

    setupForms() {
        const abaFields = [
            { label: 'Nome da Aba', id: 'abaNome', required: true },
            { label: 'Ícone', id: 'abaIcone', placeholder: 'fas fa-folder' },
            { label: 'Ordem', id: 'abaOrdem', type: 'number', value: 0 }
        ];

        const modFields = [
            { label: 'Nome do Módulo', id: 'modNome', required: true },
            { label: 'URL do Arquivo', id: 'modUrl', required: true },
            { label: 'Identificador (Slug)', id: 'modSlug', required: true }
        ];

        this.abaForm.innerHTML = '';
        abaFields.forEach(f => this.abaForm.appendChild(window.sgi.ui.createInput(f)));

        this.moduloForm.innerHTML = '';
        const selectGroup = document.createElement('div');
        selectGroup.className = 'form-group';
        selectGroup.innerHTML = `<label>Aba Destino</label><select id="modAbaId" class="form-control"></select>`;
        this.moduloForm.appendChild(selectGroup);
        modFields.forEach(f => this.moduloForm.appendChild(window.sgi.ui.createInput(f)));
    }

    bindEvents() {
        document.getElementById('btnAddAba').onclick = () => this.openAbaModal();
        document.getElementById('btnAddModulo').onclick = () => this.openModuloModal();
        document.getElementById('btnSaveAba').onclick = () => this.saveAba();
        document.getElementById('btnSaveModulo').onclick = () => this.saveModulo();
        document.getElementById('btnRefresh').onclick = () => this.loadStructure();
        
        // Eventos delegados para botões dinâmicos
        this.container.addEventListener('click', (e) => this.handleActionClick(e));
    }

    async loadStructure() {
        const response = await fetch(`${API_BASE_URL}/portal/menu`, {
            headers: { 'Authorization': `Bearer ${this.token}` }
        });
        this.data = await response.json();
        this.renderStructure(this.data);
        this.updateAbaSelect(this.data);
    }

    renderStructure(abas) {
        this.container.innerHTML = abas.map(aba => `
            <div class="aba-card">
                <header class="aba-header">
                    <h3><i class="${aba.icone}"></i> ${aba.nome}</h3>
                    <div class="flex gap-1">
                        <button class="btn-icon" data-action="edit-aba" data-id="${aba.id}" title="Editar Aba"><i class="fas fa-edit"></i></button>
                        ${(aba.nome.toLowerCase() === 'principal' || aba.nome.toLowerCase() === 'gestão' || aba.nome.toLowerCase() === 'gestao') 
                            ? '' 
                            : `<button class="btn-icon text-danger" data-action="delete-aba" data-id="${aba.id}" title="Excluir Aba"><i class="fas fa-trash"></i></button>`}
                    </div>
                </header>
                <div class="modulos-list">
                    ${aba.modulos.map(mod => `
                        <div class="modulo-item">
                            <div class="modulo-info">
                                <strong>${mod.nome}</strong>
                                <span class="modulo-url">${mod.url}</span>
                            </div>
                            <div class="flex gap-1">
                                <button class="btn-icon" data-action="edit-mod" data-id="${mod.id}" data-aba-id="${aba.id}"><i class="fas fa-pen"></i></button>
                                <button class="btn-icon text-danger" data-action="delete-mod" data-id="${mod.id}"><i class="fas fa-trash"></i></button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');
    }

    handleActionClick(e) {
        const btn = e.target.closest('button');
        if (!btn) return;

        const { action, id, abaId } = btn.dataset;
        if (action === 'edit-aba') this.editAba(id);
        if (action === 'delete-aba') this.deleteAba(id);
        if (action === 'edit-mod') this.editModulo(id, abaId);
        if (action === 'delete-mod') this.deleteModulo(id);
    }

    // --- Lógica de Abas ---

    editAba(id) {
        const aba = this.data.find(a => a.id == id);
        this.currentAbaId = id;
        document.getElementById('abaNome').value = aba.nome;
        document.getElementById('abaIcone').value = aba.icone;
        document.getElementById('abaOrdem').value = aba.ordem;
        this.openAbaModal('Editar Aba');
    }

    async saveAba() {
        const nome = document.getElementById('abaNome').value;
        const icone = document.getElementById('abaIcone').value;
        const ordem = document.getElementById('abaOrdem').value;
        
        const method = this.currentAbaId ? 'PUT' : 'POST';
        const url = this.currentAbaId 
            ? `${API_BASE_URL}/portal/abas/${this.currentAbaId}?nome=${encodeURIComponent(nome)}&icone=${encodeURIComponent(icone)}&ordem=${ordem}`
            : `${API_BASE_URL}/portal/abas?nome=${encodeURIComponent(nome)}&icone=${encodeURIComponent(icone)}&ordem=${ordem}`;

        await fetch(url, { method, headers: { 'Authorization': `Bearer ${this.token}` } });
        this.closeModals();
        this.loadStructure();
    }

    async deleteAba(id) {
        const aba = this.data.find(a => a.id == id);
        if (aba && (aba.nome.toLowerCase() === 'principal' || aba.nome.toLowerCase() === 'gestão' || aba.nome.toLowerCase() === 'gestao')) {
            alert('A aba "' + aba.nome + '" é essencial para o sistema e não pode ser excluída.');
            return;
        }
        if (!confirm('Excluir esta aba e todos os seus módulos?')) return;
        await fetch(`${API_BASE_URL}/portal/abas/${id}`, { 
            method: 'DELETE', 
            headers: { 'Authorization': `Bearer ${this.token}` } 
        });
        this.loadStructure();
    }

    // --- Lógica de Módulos ---

    editModulo(id, abaId) {
        const aba = this.data.find(a => a.id == abaId);
        const mod = aba.modulos.find(m => m.id == id);
        this.currentModuloId = id;
        document.getElementById('modAbaId').value = abaId;
        document.getElementById('modNome').value = mod.nome;
        document.getElementById('modUrl').value = mod.url;
        document.getElementById('modSlug').value = mod.slug;
        this.openModuloModal('Editar Módulo');
    }

    async saveModulo() {
        const abaId = document.getElementById('modAbaId').value;
        const nome = document.getElementById('modNome').value;
        const url_mod = document.getElementById('modUrl').value;
        const slug = document.getElementById('modSlug').value;

        const method = this.currentModuloId ? 'PUT' : 'POST';
        const url = this.currentModuloId
            ? `${API_BASE_URL}/portal/modulos/${this.currentModuloId}?nome=${encodeURIComponent(nome)}&slug=${slug}&url=${encodeURIComponent(url_mod)}&icone=fas fa-cube`
            : `${API_BASE_URL}/portal/modulos?aba_id=${abaId}&nome=${encodeURIComponent(nome)}&slug=${slug}&url=${encodeURIComponent(url_mod)}&icone=fas fa-cube`;

        await fetch(url, { method, headers: { 'Authorization': `Bearer ${this.token}` } });
        this.closeModals();
        this.loadStructure();
    }

    async deleteModulo(id) {
        if (!confirm('Excluir este módulo?')) return;
        await fetch(`${API_BASE_URL}/portal/modulos/${id}`, { 
            method: 'DELETE', 
            headers: { 'Authorization': `Bearer ${this.token}` } 
        });
        this.loadStructure();
    }

    updateAbaSelect(abas) {
        const select = document.getElementById('modAbaId');
        if (select) select.innerHTML = abas.map(a => `<option value="${a.id}">${a.nome}</option>`).join('');
    }

    openAbaModal(title = 'Nova Aba') {
        document.getElementById('abaModalTitle').textContent = title;
        this.abaModal.style.display = 'flex';
    }

    openModuloModal(title = 'Novo Módulo') {
        document.getElementById('moduloModalTitle').textContent = title;
        this.moduloModal.style.display = 'flex';
    }

    closeModals() {
        this.abaModal.style.display = 'none';
        this.moduloModal.style.display = 'none';
        this.abaForm.reset();
        this.moduloForm.reset();
        this.currentAbaId = null;
        this.currentModuloId = null;
    }
}

document.addEventListener('DOMContentLoaded', () => new StructureController());
