/**
 * Módulo de Gestão de Estrutura - Versão Full CRUD
 * Gerencia Abas e Módulos com Edição e Exclusão.
 */

class StructureController extends window.grindx.controllers.BaseController {
    constructor() {
        super();
        this.container = document.getElementById('structureContainer');
        
        // Modais
        this.abaModal = document.getElementById('abaModal');
        this.moduloModal = document.getElementById('moduloModal');
        this.abaModalController = new window.grindx.components.ReusableModal(this.abaModal, {
            initialFocusSelector: '#abaNome',
            onClose: () => this.resetForms()
        });
        this.moduloModalController = new window.grindx.components.ReusableModal(this.moduloModal, {
            initialFocusSelector: '#modAbaId',
            onClose: () => this.resetForms()
        });
        
        // Forms
        this.abaForm = document.getElementById('abaForm');
        this.moduloForm = document.getElementById('moduloForm');

        // Estado de Edição
        this.currentAbaId = null;
        this.currentModuloId = null;
        
        this.init();
    }

    async init() {
        if (!this.requireAuth('../../index.html')) return;
        this.setupForms();
        this.bindEvents();
        await this.loadStructure();
    }

    setupForms() {
        const abaFields = [
            { label: 'Nome da Aba', id: 'abaNome', required: true },
            { label: 'Ordem', id: 'abaOrdem', type: 'number', value: 0 }
        ];

        const moduleFields = [
            { label: 'Nome do Módulo', id: 'modNome', required: true },
            { label: 'URL do Arquivo', id: 'modUrl', required: true },
            { label: 'Identificador (Slug)', id: 'modSlug', required: true }
        ];

        this.abaForm.innerHTML = '';
        window.grindx.components.FormField.appendFields(this.abaForm, abaFields);
        this.abaForm.appendChild(window.grindx.components.FormField.createIconSelect({
            id: 'abaIcone',
            label: 'Ícone da Aba'
        }));
        this.abaForm.appendChild(window.grindx.components.FormField.createSelect({
            id: 'abaParentId',
            label: 'Sub-aba de (opcional)',
            options: []
        }));

        this.moduloForm.innerHTML = '';
        this.moduloForm.appendChild(window.grindx.components.FormField.createSelect({
            id: 'modAbaId',
            label: 'Aba Destino'
        }));
        window.grindx.components.FormField.appendFields(this.moduloForm, moduleFields);
        this.moduloForm.appendChild(window.grindx.components.FormField.createIconSelect({
            id: 'modIcone',
            label: 'Ícone do Módulo'
        }));
    }

    bindEvents() {
        document.getElementById('btnAddAba').onclick = () => this.openAbaModal();
        document.getElementById('btnAddModulo').onclick = () => this.openModuloModal();
        document.getElementById('btnSaveAba').onclick = () => this.saveAba();
        document.getElementById('btnSaveModulo').onclick = () => this.saveModulo();
        document.getElementById('btnCancelAba').onclick = () => this.abaModalController.close();
        document.getElementById('btnCancelModulo').onclick = () => this.moduloModalController.close();
        document.getElementById('btnRefresh').onclick = () => this.loadStructure();
        
        // Eventos delegados para botões dinâmicos
        this.container.addEventListener('click', (e) => this.handleActionClick(e));
    }

    async loadStructure() {
        window.grindx.components.LoadingSpinner.setContainerState(
            this.container,
            window.grindx.components.LoadingSpinner.create('Carregando estrutura...')
        );

        try {
            this.data = await window.grindx.api.get('/portal/menu');
            if (Array.isArray(this.data) && this.data.length) {
                this.renderStructure(this.data);
            } else {
                window.grindx.components.LoadingSpinner.setContainerState(
                    this.container,
                    window.grindx.components.LoadingSpinner.createEmpty({
                        icon: 'fas fa-folder-open',
                        title: 'Nenhuma estrutura cadastrada.'
                    })
                );
            }
            this.updateAbaSelect(this.data || []);
            this.updateAbaParentSelect(this.data || []);
        } catch (err) {
            console.error('Falha ao carregar estrutura:', err);
            window.grindx.components.LoadingSpinner.setContainerState(
                this.container,
                window.grindx.components.LoadingSpinner.createEmpty({
                    icon: 'fas fa-triangle-exclamation',
                    title: window.grindx.components.LoadingSpinner.toUserMessage(err)
                })
            );
        }
    }

    renderStructure(abas) {
        this.container.innerHTML = abas.map(aba => this._renderAbaCard(aba, 0)).join('');
    }

    _renderAbaCard(aba, depth) {
        const indent = depth * 16;
        const hasChildren = aba.children && aba.children.length > 0;
        return `
            <div class="aba-card" style="margin-left: ${indent}px${depth > 0 ? '; border-left: 3px solid var(--primary)' : ''}">
                <header class="aba-header">
                    <h3><i class="${aba.icone}"></i> ${aba.nome}</h3>
                    <div class="actions-group">
                        <button class="btn-icon" data-action="edit-aba" data-id="${aba.id}" title="Editar"><i class="fas fa-edit"></i></button>
                        ${this.isProtectedAba(aba.nome) ? '' :
                            `<button class="btn-icon text-danger" data-action="delete-aba" data-id="${aba.id}" title="Excluir"><i class="fas fa-trash"></i></button>`}
                    </div>
                </header>
                ${hasChildren ? `<div class="sub-abas-section">${aba.children.map(child => this._renderAbaCard(child, depth + 1)).join('')}</div>` : ''}
                <div class="modulos-list">
                    ${aba.modulos.map(mod => `
                        <div class="modulo-item">
                            <div class="modulo-info">
                                <strong>${mod.nome}</strong>
                                <span class="modulo-url">${mod.url}</span>
                            </div>
                            <div class="actions-group">
                                <button class="btn-icon" data-action="edit-mod" data-id="${mod.id}" data-aba-id="${aba.id}"><i class="fas fa-pen"></i></button>
                                ${this.isProtectedModule(mod.nome) || this.isProtectedAba(aba.nome) ? '' :
                                    `<button class="btn-icon text-danger" data-action="delete-mod" data-id="${mod.id}"><i class="fas fa-trash"></i></button>`}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
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
        const findAba = (list) => {
            for (const a of list) {
                if (a.id == id) return a;
                if (a.children) {
                    const found = findAba(a.children);
                    if (found) return found;
                }
            }
            return null;
        };
        const aba = findAba(this.data);
        if (!aba) return;
        this.currentAbaId = id;
        document.getElementById('abaNome').value = aba.nome;
        const iconeSelect = document.getElementById('abaIcone');
        iconeSelect.value = aba.icone || 'fas fa-folder';
        iconeSelect.dispatchEvent(new Event('change'));
        document.getElementById('abaOrdem').value = aba.ordem;
        document.getElementById('abaParentId').value = aba.parent_id || '';
        this.openAbaModal('Editar Aba');
    }

    async saveAba() {
        if (!this.validateAbaForm()) return;

        const nome = document.getElementById('abaNome').value;
        const icone = document.getElementById('abaIcone').value;
        const ordem = document.getElementById('abaOrdem').value;
        const parent_id = document.getElementById('abaParentId').value || null;

        const method = this.currentAbaId ? 'PUT' : 'POST';
        const endpoint = this.currentAbaId ? `/portal/abas/${this.currentAbaId}` : '/portal/abas';
        const params = { nome, icone, ordem };
        if (parent_id) params.parent_id = parent_id;
        try {
            await window.grindx.api.request(endpoint, { method, params });
            await this.loadStructure();
            this.toastSuccess('Aba salva com sucesso.');
            this.closeModals();
            window.parent.postMessage('sidebar-update', '*');
        } catch (err) {
            this.toastError(err);
        }
    }

    async deleteAba(id) {
        const findAba = (list) => {
            for (const a of list) {
                if (a.id == id) return a;
                if (a.children) {
                    const found = findAba(a.children);
                    if (found) return found;
                }
            }
            return null;
        };
        const aba = findAba(this.data);
        if (aba && this.isProtectedAba(aba.nome)) {
            window.grindx.components.LoadingSpinner.toast(
                `A aba "${aba.nome}" é essencial para o sistema e não pode ser excluída.`,
                'warning'
            );
            return;
        }
        if (!confirm('Excluir esta aba e todos os seus módulos?')) return;
        try {
            await window.grindx.api.delete(`/portal/abas/${id}`);
            await this.loadStructure();
            this.toastSuccess('Aba excluída com sucesso.');
            window.parent.postMessage('sidebar-update', '*');
        } catch (err) {
            this.toastError(err);
        }
    }

    // --- Lógica de Módulos ---

    editModulo(id, abaId) {
        const findAba = (list) => {
            for (const a of list) {
                if (a.id == abaId) return a;
                if (a.children) {
                    const found = findAba(a.children);
                    if (found) return found;
                }
            }
            return null;
        };
        const aba = findAba(this.data);
        if (!aba) return;
        const mod = aba.modulos.find(m => m.id == id);
        if (!mod) return;
        this.currentModuloId = id;
        document.getElementById('modAbaId').value = abaId;
        document.getElementById('modNome').value = mod.nome;
        document.getElementById('modUrl').value = mod.url;
        document.getElementById('modSlug').value = mod.slug;
        const iconeSelect = document.getElementById('modIcone');
        iconeSelect.value = mod.icone || 'fas fa-cube';
        iconeSelect.dispatchEvent(new Event('change'));
        this.openModuloModal('Editar Módulo');
    }

    async saveModulo() {
        if (!this.validateModuloForm()) return;

        const abaId = document.getElementById('modAbaId').value;
        const nome = document.getElementById('modNome').value;
        const moduleUrl = document.getElementById('modUrl').value;
        const slug = document.getElementById('modSlug').value;
        const icone = document.getElementById('modIcone').value;

        const method = this.currentModuloId ? 'PUT' : 'POST';
        const endpoint = this.currentModuloId ? `/portal/modulos/${this.currentModuloId}` : '/portal/modulos';
        const params = { nome, slug, url: moduleUrl, icone, aba_id: abaId };
        try {
            await window.grindx.api.request(endpoint, { method, params });
            await this.loadStructure();
            this.toastSuccess('Módulo salvo com sucesso.');
            this.closeModals();
            window.parent.postMessage('sidebar-update', '*');
        } catch (err) {
            this.toastError(err);
        }
    }

    async deleteModulo(id) {
        const findAbaWithMod = (list) => {
            for (const a of list) {
                if (a.modulos && a.modulos.some(m => m.id == id)) return a;
                if (a.children) {
                    const found = findAbaWithMod(a.children);
                    if (found) return found;
                }
            }
            return null;
        };
        const aba = findAbaWithMod(this.data);
        const mod = aba?.modulos?.find(m => m.id == id);
        if (mod) {
            if (this.isProtectedModule(mod.nome) || (aba && this.isProtectedAba(aba.nome))) {
                window.grindx.components.LoadingSpinner.toast(
                    `O módulo "${mod.nome}" é protegido e não pode ser excluído.`,
                    'warning'
                );
                return;
            }
        }
        if (!confirm('Excluir este módulo?')) return;
        try {
            await window.grindx.api.delete(`/portal/modulos/${id}`);
            await this.loadStructure();
            this.toastSuccess('Módulo excluído com sucesso.');
            window.parent.postMessage('sidebar-update', '*');
        } catch (err) {
            this.toastError(err);
        }
    }

    updateAbaSelect(abas) {
        const select = document.getElementById('modAbaId');
        if (!select) return;
        const buildOptions = (list, depth = 0) => {
            return list.map(a => {
                const prefix = '-- '.repeat(depth);
                let html = `<option value="${a.id}">${prefix}${a.nome}</option>`;
                if (a.children && a.children.length) {
                    html += buildOptions(a.children, depth + 1);
                }
                return html;
            }).join('');
        };
        select.innerHTML = buildOptions(abas || []);
    }

    updateAbaParentSelect(abas) {
        const select = document.getElementById('abaParentId');
        if (!select) return;
        select.innerHTML = '<option value="">Nenhuma (aba raiz)</option>' +
            (abas || []).filter(a => !a.parent_id).map(a =>
                `<option value="${a.id}">${a.nome}</option>`
            ).join('');
    }

    isProtectedAba(nome) {
        return window.grindx.constants.PROTECTED_ABA_NAMES.includes(nome.toLowerCase());
    }

    isProtectedModule(nome) {
        return window.grindx.constants.PROTECTED_MODULE_NAMES.includes(nome.toLowerCase());
    }

    renderStructureOrEmpty() {
        if (this.data.length) {
            this.renderStructure(this.data);
            return;
        }

        window.grindx.components.LoadingSpinner.setContainerState(
            this.container,
            window.grindx.components.LoadingSpinner.createEmpty({
                icon: 'fas fa-folder-open',
                title: 'Nenhuma estrutura cadastrada.'
            })
        );
    }

    validateAbaForm() {
        const result = window.grindx.validation.validateSchema('portalAba');

        if (!result.valid) {
            window.grindx.components.LoadingSpinner.toast('Revise os campos destacados.', 'warning');
        }

        return result.valid;
    }

    validateModuloForm() {
        const result = window.grindx.validation.validateSchema('portalModulo');

        if (!result.valid) {
            window.grindx.components.LoadingSpinner.toast('Revise os campos destacados.', 'warning');
        }

        return result.valid;
    }

    openAbaModal(title = 'Nova Aba') {
        document.getElementById('abaModalTitle').textContent = title;
        this.abaModalController.open();
    }

    openModuloModal(title = 'Novo Módulo') {
        document.getElementById('moduloModalTitle').textContent = title;
        this.moduloModalController.open();
    }

    closeModals() {
        this.abaModalController.close();
        this.moduloModalController.close();
    }

    resetForms() {
        window.grindx.validation.clearForm(this.abaForm);
        window.grindx.validation.clearForm(this.moduloForm);
        this.abaForm.reset();
        this.moduloForm.reset();
        this.currentAbaId = null;
        this.currentModuloId = null;
        const parentSelect = document.getElementById('abaParentId');
        if (parentSelect) parentSelect.value = '';
    }
}

document.addEventListener('DOMContentLoaded', () => new StructureController());
