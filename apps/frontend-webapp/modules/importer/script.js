class ImporterController extends window.grindx.controllers.BaseController {
    constructor() {
        super();
        this.dataTable = null;
        this.importModal = null;
        this.currentSlug = null;
        this.isReimport = false;
        this.modules = [];
        this.init();
    }

    async init() {
        if (!this.requireAuth()) return;
        this.importModal = new window.grindx.components.ReusableModal(document.getElementById('importModal'));
        this.dataTable = new window.grindx.components.DataTable('dataTableContainer', {
            columns: [
                { key: 'module_name', label: 'Módulo' },
                { key: 'version', label: 'Versão', width: '80px' },
                { key: 'schema_name', label: 'Schema', width: '100px' },
                {
                    key: 'ja_importado', label: 'Status', width: '120px',
                    render: function(v) {
                        return v ? '<span class="badge badge-success">Importado</span>' : '<span class="badge badge-info">Novo</span>';
                    }
                },
                {
                    key: 'acoes', label: 'Ações', width: '140px',
                    render: function(v, row) {
                        var slug = (row.slug || '').replace(/[&<>"']/g, '');
                        if (row.ja_importado) {
                            return '<button class="btn btn-sm btn-warning" data-action="reimport" data-slug="' + slug + '">Reimportar</button>';
                        }
                        return '<button class="btn btn-sm btn-primary" data-action="import" data-slug="' + slug + '">Importar</button>';
                    }
                }
            ],
        });
        this.bindEvents();
        await this.carregar();
    }

    bindEvents() {
        document.getElementById('btnRefresh').addEventListener('click', () => this.carregar());
        document.getElementById('btnConfirm').addEventListener('click', () => this.confirmarImport());
        document.getElementById('btnCancel').addEventListener('click', () => this.importModal.close());
        document.getElementById('btnModalClose').addEventListener('click', () => this.importModal.close());

        document.getElementById('dataTableContainer').addEventListener('click', (e) => {
            var btn = e.target.closest('[data-action]');
            if (!btn) return;
            var slug = btn.dataset.slug;
            var action = btn.dataset.action;
            if (action === 'import' || action === 'reimport') {
                this.abrirModal(slug, action === 'reimport');
            }
        });
    }

    async carregar() {
        try {
            window.grindx.components.LoadingSpinner.setContainerState('dataTableContainer', 'loading');
            var data = await window.grindx.api.get('/v1/import/scan');
            var modules = data.modules || [];
            if (modules.length === 0) {
                this.dataTable.renderEmpty('Nenhum módulo encontrado. Coloque um .zip na pasta import/ do servidor.');
            } else {
                this.dataTable.render(modules);
            }
        } catch (err) {
            this.toastError(err);
        }
    }

    abrirModal(slug, isReimport) {
        this.currentSlug = slug;
        this.isReimport = isReimport;
        var safeSlug = (slug || '').replace(/[&<>"']/g, '');
        var body = document.getElementById('modalBody');
        body.innerHTML =
            '<p><strong>Módulo:</strong> ' + safeSlug + '</p>' +
            '<p>' + (isReimport ? 'O módulo já existe. Reimportar sobrescreverá os arquivos atuais.' : 'Confirme para importar este módulo.') + '</p>' +
            '<div id="importLog" class="import-log hidden"></div>';
        document.getElementById('modalTitle').textContent = isReimport ? 'Reimportar Módulo' : 'Importar Módulo';
        document.getElementById('btnConfirm').textContent = isReimport ? 'Reimportar' : 'Importar';
        this.importModal.open();
    }

    async confirmarImport() {
        var btn = document.getElementById('btnConfirm');
        var logDiv = document.getElementById('importLog');
        btn.disabled = true;
        btn.textContent = 'Importando...';
        logDiv.classList.remove('hidden');
        logDiv.innerHTML = '<div class="loading-spinner"></div>';

        try {
            var result = await window.grindx.api.post('/v1/import/' + this.currentSlug + '?force=' + this.isReimport);

            logDiv.innerHTML = '';
            var steps = result.steps || [];
            steps.forEach(function(step) {
                var div = document.createElement('div');
                div.className = result.success ? 'log-step success' : 'log-step error';
                div.textContent = (result.success ? '✓ ' : '✗ ') + step;
                logDiv.appendChild(div);
            });

            if (result.success) {
                var div = document.createElement('div');
                div.className = 'log-step success';
                div.style.fontWeight = 'bold';
                div.textContent = 'Modulo importado com sucesso!';
                logDiv.appendChild(div);
                setTimeout(() => {
                    this.importModal.close();
                    this.carregar();
                }, 1500);
            } else {
                var errDiv = document.createElement('div');
                errDiv.className = 'log-step error';
                errDiv.style.fontWeight = 'bold';
                errDiv.textContent = 'Falha: ' + (result.error || 'Erro desconhecido');
                logDiv.appendChild(errDiv);
                btn.disabled = false;
                btn.textContent = this.isReimport ? 'Reimportar' : 'Importar';
            }
        } catch (err) {
            logDiv.innerHTML = '<div class="log-step error" style="font-weight:bold">Falha: ' + (err.message || 'Erro desconhecido') + '</div>';
            btn.disabled = false;
            btn.textContent = this.isReimport ? 'Reimportar' : 'Importar';
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    new ImporterController();
});
