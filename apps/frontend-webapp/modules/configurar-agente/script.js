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
        document.getElementById('importBtn').addEventListener('click', () => this.importManuais());
        document.getElementById('fileInput').addEventListener('change', (e) => this.updateFileList(e));
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

    updateFileList(e) {
        const list = document.getElementById('fileList');
        const files = Array.from(e.target.files || []);
        list.innerHTML = '';
        files.forEach((f) => {
            const li = document.createElement('li');
            li.textContent = f.name;
            list.appendChild(li);
        });
    }

    async importManuais() {
        const module = document.getElementById('moduleSelect').value;
        const files = Array.from(document.getElementById('fileInput').files || []);
        const textarea = document.getElementById('manualText').value.trim();

        if (!module) { this.toastWarning('Selecione o módulo do ERP.'); return; }
        if (!files.length && !textarea) {
            this.toastWarning('Selecione ao menos um arquivo ou cole o conteúdo do manual.');
            return;
        }

        const tasks = [];
        if (textarea) {
            tasks.push(this.ingest(module, 'manual-' + module + '.md', textarea));
        }
        files.forEach((f) => {
            tasks.push(this.readFile(f).then((content) => this.ingest(module, f.name, content)));
        });

        const btn = document.getElementById('importBtn');
        btn.disabled = true;
        try {
            const settled = await Promise.allSettled(tasks);
            const ok = settled.filter((s) => s.status === 'fulfilled').length;
            const fail = settled.filter((s) => s.status === 'rejected').length;
            this.toastSuccess(ok + ' manual(is) importado(s)' + (fail ? ', ' + fail + ' falha(s)' : '') + '.');

            document.getElementById('fileInput').value = '';
            document.getElementById('manualText').value = '';
            document.getElementById('fileList').innerHTML = '';
            await this.loadIndexedManuals();
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
            tbody.innerHTML = '<tr><td colspan="3" class="text-muted">' +
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
            tr.appendChild(tdModulo);
            tr.appendChild(tdArquivo);
            tr.appendChild(tdChunks);
            tbody.appendChild(tr);
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.configurarAgenteController = new ConfigurarAgenteController();
});
