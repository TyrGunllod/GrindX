class RecursosController extends window.grindx.controllers.BaseController {
    constructor() {
        super();
        this.baseUrl = '/v1/recursos';
        this.dataTable = null;
        this.modal = null;
        this.init();
    }

    async init() {
        if (!this.requireAuth()) return;
        this.modal = new window.grindx.components.ReusableModal('modalAlocar');
        this.dataTable = new window.grindx.components.DataTable('dataTableContainer', {
            columns: [
                {
                    key: 'nome',
                    label: 'Nome',
                    render: (v, row) =>
                        `<div class="user-avatar" style="background:${row.cor}">${this._getInitials(v)}</div>
                         <span>${v}</span>`
                },
                { key: 'email', label: 'Email' },
                { key: 'cargo_contexto', label: 'Cargo' },
                { key: 'tarefas_ativas', label: 'Tarefas Ativas', width: '100px' },
                { key: 'tarefas_concluidas', label: 'Conclu\u00eddas', width: '100px' },
            ],
            actions: [
                { label: 'Editar', class: 'btn-sm', onClick: (row) => this.editar(row) },
                { label: 'Desalocar', class: 'btn-sm btn-danger', onClick: (row) => this.desalocar(row) },
            ],
            onPageChange: (page) => this.carregar(page),
        });
        this.bindEvents();
        this.carregar();
    }

    bindEvents() {
        document.getElementById('btnAlocar').addEventListener('click', () => this.abrirModal());
        document.getElementById('formAlocar').addEventListener('submit', (e) => this.salvar(e));
        document.getElementById('btnModalClose').addEventListener('click', () => this.modal.close());
        document.getElementById('btnCancelar').addEventListener('click', () => this.modal.close());
        document.getElementById('colorPicker').addEventListener('click', (e) => {
            const swatch = e.target.closest('.color-swatch');
            if (swatch) {
                document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
                swatch.classList.add('selected');
                document.getElementById('cor').value = swatch.dataset.color;
            }
        });
    }

    async carregar(page = 1) {
        try {
            const data = await window.grindx.api.get(`${this.baseUrl}?page=${page}&page_size=20`);
            this.dataTable.render(data.items, {
                page: data.page,
                total: data.total,
                totalPages: data.total_pages
            });
            this._atualizarResumo(data.items);
            this._renderizarGrafico(data.items);
        } catch (err) {
            this.toastError(err);
        }
    }

    async abrirModal() {
        document.getElementById('modalTitle').textContent = 'Alocar Recurso';
        document.getElementById('formAlocar').reset();
        try {
            const users = await window.grindx.api.get('/v1/iam/usuarios');
            const select = document.getElementById('userSelect');
            select.innerHTML = '<option value="">Selecione um usu\u00e1rio...</option>';
            users.forEach(u => {
                const opt = document.createElement('option');
                opt.value = u.id;
                opt.textContent = `${u.nome_completo} (${u.email})`;
                select.appendChild(opt);
            });
        } catch (err) {
            this.toastError('Erro ao carregar usu\u00e1rios');
        }
        this.modal.open();
    }

    async salvar(e) {
        e.preventDefault();
        const data = {
            user_id: parseInt(document.getElementById('userSelect').value),
            projeto_id: this._getProjetoId(),
            cargo_contexto: document.getElementById('cargoContexto').value || null,
            cor: document.getElementById('cor').value,
        };
        try {
            await window.grindx.api.post(this.baseUrl, data);
            this.modal.close();
            this.carregar();
            this.toastSuccess('Recurso alocado com sucesso');
        } catch (err) {
            this.toastError(err);
        }
    }

    editar(row) {
        document.getElementById('modalTitle').textContent = 'Editar Recurso';
        document.getElementById('cargoContexto').value = row.cargo_contexto || '';
        document.getElementById('cor').value = row.cor || '#3b82f6';
        document.querySelectorAll('.color-swatch').forEach(s => {
            s.classList.toggle('selected', s.dataset.color === row.cor);
        });
        this.modal.open();
    }

    async desalocar(row) {
        if (!confirm(`Desalocar ${row.nome}? As tarefas atribu\u00eddas ficar\u00e3o sem respons\u00e1vel.`)) return;
        try {
            await window.grindx.api.delete(`${this.baseUrl}/${row.id}`);
            this.carregar();
            this.toastSuccess('Recurso desalocado');
        } catch (err) {
            this.toastError(err);
        }
    }

    _atualizarResumo(items) {
        document.getElementById('totalAlocados').textContent = items.length;
    }

    _renderizarGrafico(items) {
        const container = document.getElementById('workloadChart');
        if (!items || items.length === 0) {
            container.innerHTML = '<p class="text-muted">Nenhum recurso alocado</p>';
            return;
        }
        const maxTarefas = Math.max(...items.map(i => i.tarefas_ativas || 0), 1);
        container.innerHTML = items.map(item => `
            <div class="workload-item">
                <div class="workload-label">
                    <span class="color-dot" style="background:${item.cor}"></span>
                    <span>${item.nome}</span>
                </div>
                <div class="workload-bar">
                    <div class="workload-fill" style="width:${((item.tarefas_ativas || 0) / maxTarefas) * 100}%;background:${item.cor}"></div>
                </div>
                <span class="workload-count">${item.tarefas_ativas || 0} ativa(s)</span>
            </div>
        `).join('');
    }

    _getInitials(name) {
        if (!name) return '?';
        return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
    }

    _getProjetoId() {
        const params = new URLSearchParams(window.location.search);
        return parseInt(params.get('projeto_id')) || 1;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new RecursosController();
});
