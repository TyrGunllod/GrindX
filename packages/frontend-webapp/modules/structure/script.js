/**
 * Módulo de Gestão de Estrutura
 * Permite configurar abas e módulos dinamicamente.
 */

const API_BASE_URL = 'http://localhost:8002/v1';

class StructureController {
    constructor() {
        this.container = document.getElementById('structureContainer');
        this.token = localStorage.getItem('access_token');
        this.init();
    }

    async init() {
        await this.loadStructure();
        this.bindEvents();
    }

    async loadStructure() {
        try {
            const response = await fetch(`${API_BASE_URL}/portal/menu`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const data = await response.json();
            this.renderStructure(data);
            this.updateAbaSelect(data);
        } catch (err) {
            this.container.innerHTML = 'Erro ao carregar estrutura.';
        }
    }

    renderStructure(abas) {
        if (abas.length === 0) {
            this.container.innerHTML = '<div class="loading-state">Nenhuma aba cadastrada.</div>';
            return;
        }

        this.container.innerHTML = abas.map(aba => `
            <div class="aba-card">
                <header class="aba-header">
                    <h3><i class="${aba.icone || 'fas fa-folder'}"></i> ${aba.nome}</h3>
                    <span class="badge">Ordem: ${aba.id}</span>
                </header>
                <div class="modulos-list">
                    ${aba.modulos.map(mod => `
                        <div class="modulo-item">
                            <div class="modulo-info">
                                <strong>${mod.nome}</strong>
                                <span class="modulo-url">${mod.url}</span>
                            </div>
                            <button class="btn-icon text-danger" onclick="alert('Excluir módulo ${mod.id}')">
                                <i class="fas fa-trash-alt"></i>
                            </button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');
    }

    updateAbaSelect(abas) {
        const select = document.getElementById('modAba');
        select.innerHTML = abas.map(a => `<option value="${a.id}">${a.nome}</option>`).join('');
    }

    bindEvents() {
        // Aba
        document.getElementById('btnAddAba').onclick = () => document.getElementById('abaModal').style.display='flex';
        document.getElementById('btnSaveAba').onclick = () => this.saveAba();

        // Módulo
        document.getElementById('btnAddModulo').onclick = () => document.getElementById('moduloModal').style.display='flex';
        document.getElementById('btnSaveModulo').onclick = () => this.saveModulo();
    }

    async saveAba() {
        const nome = document.getElementById('abaNome').value;
        const icone = document.getElementById('abaIcone').value;
        const ordem = document.getElementById('abaOrdem').value;

        const url = `${API_BASE_URL}/portal/abas?nome=${encodeURIComponent(nome)}&icone=${encodeURIComponent(icone)}&ordem=${ordem}`;
        
        await fetch(url, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${this.token}` }
        });

        document.getElementById('abaModal').style.display = 'none';
        this.loadStructure();
    }

    async saveModulo() {
        const aba_id = document.getElementById('modAba').value;
        const nome = document.getElementById('modNome').value;
        const url_mod = document.getElementById('modUrl').value;
        const slug = document.getElementById('modSlug').value;

        const endpoint = `${API_BASE_URL}/portal/modulos?aba_id=${aba_id}&nome=${encodeURIComponent(nome)}&slug=${slug}&url=${encodeURIComponent(url_mod)}&icone=fas fa-cube`;

        await fetch(endpoint, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${this.token}` }
        });

        document.getElementById('moduloModal').style.display = 'none';
        this.loadStructure();
    }
}

document.addEventListener('DOMContentLoaded', () => new StructureController());
