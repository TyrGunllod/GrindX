class ImporterController extends window.grindx.controllers.BaseController {
    constructor() {
        super();
        this.dataTable = null;
        this.importModal = null;
        this.currentSlug = null;
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
                            return '<button class="btn btn-sm btn-danger" data-action="remove" data-slug="' + slug + '">Remover</button>';
                        }
                        return '<button class="btn btn-sm btn-primary" data-action="import" data-slug="' + slug + '">Importar</button>';
                    }
                }
            ],
            rowClassName: () => 'module-row',
            rowDataset: (item) => ({ slug: item.slug })
        });
        this.bindEvents();
    }

    bindEvents() {
        document.getElementById('btnScan').addEventListener('click', () => this.carregar());
        document.getElementById('btnConfirm').addEventListener('click', () => this.confirmarImport());
        document.getElementById('btnCancel').addEventListener('click', () => this.importModal.close());
        document.getElementById('btnModalClose').addEventListener('click', () => this.importModal.close());

        document.getElementById('dataTableContainer').addEventListener('click', (e) => {
            var btn = e.target.closest('[data-action]');
            if (btn) {
                var slug = btn.dataset.slug;
                var action = btn.dataset.action;
                if (action === 'import') {
                    this.abrirModalImportar(slug);
                } else if (action === 'remove') {
                    this.abrirModalRemover(slug);
                }
                return;
            }
        });
    }

    async carregar() {
        try {
            var container = document.getElementById('dataTableContainer');
            window.grindx.components.LoadingSpinner.setContainerState(container, window.grindx.components.LoadingSpinner.create());
            var data = await window.grindx.api.get('/import/scan');
            this.modules = data.modules || [];
            if (this.modules.length === 0) {
                this.dataTable.renderEmpty('Nenhum módulo encontrado. Coloque um .zip na pasta import/ do servidor.');
            } else {
                this.dataTable.render(this.modules);
            }
        } catch (err) {
            this.toastError(err);
        }
    }

    abrirModalImportar(slug) {
        this.currentSlug = slug;
        var safeSlug = (slug || '').replace(/[&<>"']/g, '');
        var body = document.getElementById('modalBody');
        body.innerHTML =
            '<p><strong>Módulo:</strong> ' + safeSlug + '</p>' +
            '<p>Confirme para importar este módulo.</p>' +
            '<div id="importLog" class="import-log hidden"></div>';
        document.getElementById('modalTitle').textContent = 'Importar Módulo';
        document.getElementById('btnConfirm').textContent = 'Importar';
        this.importModal.open();
    }

    abrirModalRemover(slug) {
        this.currentSlug = slug;
        var safeSlug = (slug || '').replace(/[&<>"']/g, '');
        var body = document.getElementById('modalBody');
        body.innerHTML =
            '<p><strong>Módulo:</strong> ' + safeSlug + '</p>' +
            '<p>Tem certeza que deseja remover este módulo? Os arquivos backend e frontend serão deletados.</p>' +
            '<div id="importLog" class="import-log hidden"></div>';
        document.getElementById('modalTitle').textContent = 'Remover Módulo';
        document.getElementById('btnConfirm').textContent = 'Remover';
        this.importModal.open();
    }

    async confirmarImport() {
        var btn = document.getElementById('btnConfirm');
        var logDiv = document.getElementById('importLog');
        var isRemove = document.getElementById('modalTitle').textContent === 'Remover Módulo';
        btn.disabled = true;
        btn.textContent = isRemove ? 'Removendo...' : 'Importando...';
        logDiv.classList.remove('hidden');
        logDiv.innerHTML = '<div class="loading-spinner"></div>';

        try {
            var result;
            if (isRemove) {
                result = await window.grindx.api.delete('/import/' + this.currentSlug);
            } else {
                result = await window.grindx.api.post('/import/' + this.currentSlug);
            }

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
                div.textContent = isRemove ? 'Módulo removido com sucesso!' : 'Módulo importado com sucesso!';
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
                btn.textContent = isRemove ? 'Remover' : 'Importar';
            }
        } catch (err) {
            if (!isRemove) {
                logDiv.innerHTML = '<div class="log-step info" style="font-weight:bold">Aguardando servidor reiniciar...</div><div class="loading-spinner" style="margin-top: 10px;"></div>';
                await this.aguardarServidor(this.currentSlug, logDiv, btn);
            } else {
                logDiv.innerHTML = '<div class="log-step error" style="font-weight:bold">Falha: ' + (err.message || 'Erro desconhecido') + '</div>';
                btn.disabled = false;
                btn.textContent = 'Remover';
            }
        }
    }

    async aguardarServidor(slug, logDiv, btn) {
        var maxTentativas = 30;
        var tentativa = 0;

        while (tentativa < maxTentativas) {
            await new Promise(r => setTimeout(r, 2000));
            tentativa++;

            try {
                var data = await window.grindx.api.get('/import/scan');
                var modulo = (data.modules || []).find(m => m.slug === slug);

                if (modulo && modulo.ja_importado) {
                    logDiv.innerHTML = '<div class="log-step success" style="font-weight:bold">✓ Módulo importado com sucesso!</div>';
                    btn.disabled = false;
                    btn.textContent = 'Importar';
                    setTimeout(() => {
                        this.importModal.close();
                        this.carregar();
                    }, 1500);
                    return;
                }
            } catch (e) {
                logDiv.innerHTML = '<div class="log-step info" style="font-weight:bold">Aguardando servidor reiniciar... (' + tentativa + '/' + maxTentativas + ')</div><div class="loading-spinner" style="margin-top: 10px;"></div>';
            }
        }

        logDiv.innerHTML = '<div class="log-step error" style="font-weight:bold">Timeout: servidor não respondeu. Recarregue a página.</div>';
        btn.disabled = false;
        btn.textContent = 'Importar';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    new ImporterController();
});
