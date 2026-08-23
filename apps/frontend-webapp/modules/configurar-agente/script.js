/**
 * Módulo Configurar Agente — importa manuais Markdown para o assistente de IA.
 *
 * Chama diretamente a API do Agente de IA (porta 8003), configurável via
 * window.__GRINDX_AGENT_URL no deploy.
 */
class ConfigurarAgenteController extends window.grindx.controllers.BaseController {
    constructor() {
        super();
        this.agentUrl = (window.__GRINDX_AGENT_URL || 'http://localhost:8003').replace(/\/+$/, '');
        this.init();
    }

    async init() {
        if (!this.requireAuth('../../index.html')) return;

        this.setBadgeVersao();
        this.bindEvents();
        await this.loadModules();
        await this.loadIndexedManuals();
    }

    bindEvents() {
        document.getElementById('importBtn').addEventListener('click', () => this.importManual());
    }

    async loadModules() {
        const select = document.getElementById('moduleSelect');
        try {
            const menu = await window.grindx.api.get('/portal/menu');
            select.innerHTML = '<option value="">Selecione o módulo...</option>';
            const seen = new Set();
            const addOption = (m) => {
                if (!m || !m.slug || seen.has(m.slug)) return;
                seen.add(m.slug);
                const opt = document.createElement('option');
                opt.value = m.slug;
                opt.textContent = m.nome;
                select.appendChild(opt);
            };
            (menu || []).forEach((aba) => {
                (aba.modulos || []).forEach(addOption);
                (aba.children || []).forEach((child) => (child.modulos || []).forEach(addOption));
            });
        } catch (e) {
            select.innerHTML = '<option value="">Erro ao carregar módulos</option>';
            this.toastError(e);
        }
    }

    async importManual() {
        const module = document.getElementById('moduleSelect').value;
        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files && fileInput.files[0];

        if (!module) { this.toastWarning('Selecione o módulo do ERP.'); return; }
        if (!file) { this.toastWarning('Selecione o arquivo do manual.'); return; }

        const btn = document.getElementById('importBtn');
        btn.disabled = true;
        try {
            const content = await this.readFile(file);
            await this.ingest(module, file.name, content);
            this.toastSuccess('Manual "' + file.name + '" importado.');
            fileInput.value = '';
            await this.loadIndexedManuals();
        } catch (e) {
            this.toastError(e);
        } finally {
            btn.disabled = false;
        }
    }

    readFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(new Error('Falha ao ler ' + file.name));
            reader.readAsText(file);
        });
    }

    async ingest(module, filename, content) {
        const resp = await fetch(this.agentUrl + '/v1/agente/manuais', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ module, filename, content })
        });
        if (!resp.ok) {
            let detail = 'HTTP ' + resp.status;
            try { detail = (await resp.json()).detail || detail; } catch (e) { /* ignore */ }
            throw new Error(detail);
        }
        return resp.json();
    }

    async loadIndexedManuals() {
        const tbody = document.getElementById('manuaisBody');
        try {
            const resp = await fetch(this.agentUrl + '/v1/agente/manuais');
            if (!resp.ok) throw new Error('HTTP ' + resp.status);
            const data = await resp.json();
            this.renderIndexed(data.manuais || []);
        } catch (e) {
            this.renderIndexed([], 'Não foi possível conectar ao Agente de IA (porta 8003).');
        }
    }

    renderIndexed(manuais, emptyMsg) {
        const tbody = document.getElementById('manuaisBody');
        tbody.innerHTML = '';
        if (!manuais || !manuais.length) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-muted">' +
                (emptyMsg || 'Nenhum manual indexado ainda.') + '</td></tr>';
            return;
        }
        manuais.forEach((m) => {
            const tr = document.createElement('tr');
            const tdModulo = document.createElement('td');
            tdModulo.textContent = m.module;
            const tdArquivo = document.createElement('td');
            tdArquivo.textContent = m.filename;
            const tdChunks = document.createElement('td');
            tdChunks.textContent = m.chunks;
            const tdAcoes = document.createElement('td');

            const btn = document.createElement('button');
            btn.className = 'btn-icon danger-btn';
            btn.title = 'Remover manual';
            btn.setAttribute('aria-label', 'Remover manual');
            btn.innerHTML = '<i class="fas fa-trash" aria-hidden="true"></i>';
            btn.addEventListener('click', () => this.deleteManual(m.module, m.filename));
            tdAcoes.appendChild(btn);

            tr.appendChild(tdModulo);
            tr.appendChild(tdArquivo);
            tr.appendChild(tdChunks);
            tr.appendChild(tdAcoes);
            tbody.appendChild(tr);
        });
    }

    async deleteManual(module, filename) {
        if (!window.confirm('Remover o manual "' + filename + '" do módulo "' + module + '"?')) return;
        try {
            const url = this.agentUrl + '/v1/agente/manuais?module=' +
                encodeURIComponent(module) + '&filename=' + encodeURIComponent(filename);
            const resp = await fetch(url, { method: 'DELETE' });
            if (!resp.ok) throw new Error('HTTP ' + resp.status);
            this.toastSuccess('Manual removido.');
            await this.loadIndexedManuals();
        } catch (e) {
            this.toastError(e);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.configurarAgenteController = new ConfigurarAgenteController();
});
