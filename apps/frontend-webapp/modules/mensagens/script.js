/**
 * MENSAGENS MODULE — GrindX
 * Lista, envia e responde mensagens internas; marca como lida; arquiva; anexa arquivos.
 */

class MensagensController extends window.grindx.controllers.BaseController {
    constructor() {
        super();
        this.PAGE_SIZE = 20;
        this.page = 1;
        this.totalPages = 0;
        this.status = 'todas';
        this.ordem = 'decrescente';
        this.threadId = null;
        this.composeFiles = [];
        this.replyFiles = [];
        this.init();
    }

    async init() {
        if (!this.requireAuth('../../index.html')) return;
        this.setBadgeVersao();
        this.bindEvents();
        await this.carregarDestinatarios();
        await this.loadLista();
    }

    bindEvents() {
        document.getElementById('statusFilter').addEventListener('change', (e) => {
            this.status = e.target.value;
            this.page = 1;
            this.loadLista();
        });
        document.getElementById('ordemFilter').addEventListener('change', (e) => {
            this.ordem = e.target.value;
            this.page = 1;
            this.loadLista();
        });
        document.getElementById('listaPrev').addEventListener('click', () => this.changePage(-1));
        document.getElementById('listaNext').addEventListener('click', () => this.changePage(1));
        document.getElementById('novaMensagemBtn').addEventListener('click', () => this.abrirModal());
        document.getElementById('fecharModalBtn').addEventListener('click', () => this.fecharModal());
        document.getElementById('cancelarModalBtn').addEventListener('click', () => this.fecharModal());
        document.getElementById('enviarMensagemBtn').addEventListener('click', () => this.enviarMensagem());
        document.getElementById('categoriaSelect').addEventListener('change', () => this.toggleBroadcastGroup());
        document.getElementById('broadcastCheckbox').addEventListener('change', () => this.atualizarEstadoDestinatario());
        document.getElementById('voltarBtn').addEventListener('click', () => this.voltarLista());
        document.getElementById('enviarRespostaBtn').addEventListener('click', () => this.enviarResposta());
        document.getElementById('composeAnexos').addEventListener('change', (e) => {
            this.composeFiles = Array.from(e.target.files || []);
            this.renderArquivosPendentes('composeArquivos', this.composeFiles);
        });
        document.getElementById('respostaAnexos').addEventListener('change', (e) => {
            this.replyFiles = Array.from(e.target.files || []);
            this.renderArquivosPendentes('respostaArquivos', this.replyFiles);
        });
    }

    async carregarDestinatarios() {
        try {
            const data = await window.grindx.api.get('/mensagens/destinatarios', { page_size: 100 });
            const me = window.grindx.session.getUserProfile();
            const items = (data.items || []).filter((u) => String(u.id) !== String(me.id));
            const select = document.getElementById('destinatarioSelect');
            select.innerHTML = items.map((u) =>
                `<option value="${u.id}">${u.nome_completo || u.username}</option>`
            ).join('');
        } catch (err) {
            console.error('Erro ao carregar destinatários:', err);
        }
    }

    async loadLista() {
        try {
            const data = await window.grindx.api.get('/mensagens', {
                status: this.status,
                ordem: this.ordem,
                page: this.page,
                page_size: this.PAGE_SIZE
            });
            this.renderLista(data);
        } catch (err) {
            console.error('Erro ao carregar mensagens:', err);
            document.getElementById('listaMensagens').innerHTML =
                '<div class="msg-empty">Erro ao carregar mensagens.</div>';
        }
    }

    renderLista(data) {
        const container = document.getElementById('listaMensagens');
        const items = data.items || [];
        if (items.length === 0) {
            container.innerHTML = '<div class="msg-empty">Nenhuma mensagem encontrada.</div>';
        } else {
            container.innerHTML = items.map((m) => this.cardHtml(m)).join('');
            container.querySelectorAll('[data-abrir]').forEach((el) => {
                el.addEventListener('click', () => this.abrirThread(el.dataset.abrir));
            });
            container.querySelectorAll('[data-arquivar]').forEach((el) => {
                el.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.toggleArquivar(el.dataset.arquivar);
                });
            });
        }
        this.totalPages = data.total_pages || 0;
        this.updatePagination(data);
        if (window.grindx.mensagens) window.grindx.mensagens.refresh();
    }

    getCurrentUserId() {
        try {
            const p = window.grindx.session.getUserProfile();
            return String(p.id || p.sub || '');
        } catch (_) { return ''; }
    }

    isMensagemNaoLida(m) {
        return !m.lida_em && String(m.destinatario_id) === this.getCurrentUserId();
    }

    cardHtml(m) {
        const naoLida = this.temAtividadeNaoLida(m);
        const catClass = (m.categoria || 'DIRETA').toUpperCase();
        return `
            <article class="msg-card ${naoLida ? 'nao-lida' : ''}" data-abrir="${m.id}" tabindex="0" role="button"
                     aria-label="Abrir mensagem ${m.titulo}">
                <div class="msg-card-head">
                    ${naoLida ? '<span class="msg-nao-lida" aria-label="Não lida"><i class="fas fa-exclamation-circle" aria-hidden="true"></i></span>' : ''}
                    <span class="msg-categoria ${catClass}">${catClass}</span>
                    <h3 class="msg-card-title">${this.escapeHtml(m.titulo)}</h3>
                </div>
                <div class="msg-card-meta">
                    <span>${m.remetente_nome || 'Sistema'}</span>
                    <span>${this.formatDate(m.criado_em)}</span>
                    ${m.quantidade_respostas > 0
                        ? `<span class="msg-card-replies"><i class="fas fa-reply"></i> ${m.quantidade_respostas}</span>` : ''}
                    ${m.anexos_count > 0
                        ? `<span class="msg-card-replies"><i class="fas fa-paperclip"></i> ${m.anexos_count}</span>` : ''}
                </div>
                <p class="msg-card-texto">${this.escapeHtml(m.texto)}</p>
                <div class="msg-card-actions">
                    ${m.arquivada_em
                        ? `<button class="btn btn-outline btn-sm" data-arquivar="${m.id}"><i class="fas fa-undo"></i> Restaurar</button>`
                        : `<button class="btn btn-outline btn-sm" data-arquivar="${m.id}"><i class="fas fa-archive"></i> Arquivar</button>`}
                </div>
            </article>
        `;
    }

    temAtividadeNaoLida(m) {
        // Backend calcula corretamente para remetente e destinatário (inclui respostas)
        if (typeof m.nao_lida === 'boolean') return m.nao_lida;
        return !m.lida_em;
    }

    updatePagination(data) {
        const info = document.getElementById('listaPageInfo');
        info.textContent = `Página ${data.page} de ${data.total_pages || 0}`;
        document.getElementById('listaPrev').disabled = data.page <= 1;
        document.getElementById('listaNext').disabled = data.page >= (data.total_pages || 0);
    }

    changePage(delta) {
        const next = this.page + delta;
        if (next < 1 || next > this.totalPages) return;
        this.page = next;
        this.loadLista();
    }

    async abrirThread(mensagemId) {
        this.threadId = mensagemId;
        try {
            const itens = await window.grindx.api.get(`/mensagens/${mensagemId}/thread`);
            this.renderThread(itens);
            const raiz = itens.find((m) => m.id === Number(mensagemId))
                || itens.find((m) => !m.resposta_a_id)
                || itens[0];
            this.mostrarBotaoAcao(raiz);
            // Marca lida em background e esconde a exclamação danger
            window.grindx.api.patch(`/mensagens/${mensagemId}/thread/lida`).then(() => {
                if (window.grindx.notifyMensagens) window.grindx.notifyMensagens();
                const container = document.getElementById('threadMensagens');
                if (container) {
                    container.querySelectorAll('.msg-nao-lida').forEach((el) => el.remove());
                    container.querySelectorAll('.msg-thread-item.nao-lida').forEach((el) => el.classList.remove('nao-lida'));
                }
                this.loadLista();
            }).catch((err) => console.warn('Falha ao marcar thread lida:', err));
        } catch (err) {
            console.error('Erro ao abrir thread:', err);
        }
    }

    renderThread(itens) {
        document.getElementById('listaView').style.display = 'none';
        document.getElementById('threadView').style.display = 'block';
        const raizTitulo = (itens.find((m) => m.id === Number(this.threadId))
            || itens.find((m) => !m.resposta_a_id)
            || itens[0]);
        document.getElementById('threadTitulo').textContent = raizTitulo ? raizTitulo.titulo : '';
        const container = document.getElementById('threadMensagens');
        container.innerHTML = itens.map((m) => this.threadItemHtml(m)).join('');
        container.querySelectorAll('[data-download]').forEach((el) => {
            el.addEventListener('click', () => {
                const [mid, aid, nome] = el.dataset.download.split('::');
                this.downloadAnexo(mid, aid, nome);
            });
        });
        if (window.grindx.notifyMensagens) window.grindx.notifyMensagens();
    }

    threadItemHtml(m) {
        const catClass = (m.categoria || 'DIRETA').toUpperCase();
        const naoLida = this.isMensagemNaoLida(m);
        const anexos = (m.anexos || []).map((a) =>
            `<span class="msg-anexo-chip">
                <i class="fas fa-paperclip"></i> ${this.escapeHtml(a.nome_arquivo_original)}
                <button type="button" data-download="${m.id}::${a.id}::${this.escapeHtml(a.nome_arquivo_original)}"
                        aria-label="Baixar ${this.escapeHtml(a.nome_arquivo_original)}">
                    <i class="fas fa-download"></i>
                </button>
             </span>`
        ).join('');
        return `
            <article class="msg-thread-item ${naoLida ? 'nao-lida' : ''}">
                <div class="msg-card-head">
                    ${naoLida ? '<span class="msg-nao-lida" aria-label="Não lida"><i class="fas fa-exclamation-circle" aria-hidden="true"></i></span>' : ''}
                    <span class="msg-categoria ${catClass}">${catClass}</span>
                    <h3 class="msg-card-title">${this.escapeHtml(m.titulo)}</h3>
                </div>
                <div class="msg-card-meta">
                    <span>${m.remetente_nome || 'Sistema'}</span>
                    <span>${this.formatDate(m.criado_em)}</span>
                    ${m.id === Number(this.threadId) ? '<span class="msg-card-replies">(mensagem principal)</span>' : ''}
                </div>
                <p class="msg-card-texto">${this.escapeHtml(m.texto)}</p>
                ${anexos ? `<div class="msg-anexos-pendentes">${anexos}</div>` : ''}
            </article>
        `;
    }

    mostrarBotaoAcao(raiz) {
        const container = document.getElementById('threadMensagens');
        const existente = container.querySelector('.msg-acao-btn');
        if (existente) existente.remove();
        if (!raiz.url_acao) return;
        const btn = document.createElement('button');
        btn.className = 'btn btn-primary btn-sm msg-acao-btn';
        btn.innerHTML = '<i class="fas fa-external-link-alt"></i> Ir para a ação';
        btn.addEventListener('click', () => {
            if (window.grindx.navegarPara) window.grindx.navegarPara(raiz.url_acao);
        });
        container.appendChild(btn);
    }

    voltarLista() {
        document.getElementById('threadView').style.display = 'none';
        document.getElementById('listaView').style.display = 'block';
        this.threadId = null;
        this.loadLista();
    }

    async toggleArquivar(mensagemId) {
        try {
            const msg = await window.grindx.api.patch(`/mensagens/${mensagemId}/arquivar`, {
                arquivar: !this.estaArquivada(mensagemId)
            });
            if (msg && window.grindx.mensagens) window.grindx.mensagens.refresh();
            this.loadLista();
        } catch (err) {
            this.toastError(err);
        }
    }

    estaArquivada(mensagemId) {
        const card = document.querySelector(`[data-abrir="${mensagemId}"]`);
        return !!(card && card.textContent.indexOf('Restaurar') !== -1);
    }

    abrirModal() {
        document.getElementById('composeModal').style.display = 'flex';
        this.composeFiles = [];
        this.renderArquivosPendentes('composeArquivos', []);
        document.getElementById('composeForm').reset();
        document.getElementById('broadcastCheckbox').checked = false;
        this.aplicarPermissaoCategoria();
        this.toggleBroadcastGroup();
        this.atualizarEstadoDestinatario();
    }

    fecharModal() {
        document.getElementById('composeModal').style.display = 'none';
    }

    aplicarPermissaoCategoria() {
        const me = window.grindx.session.getUserProfile();
        const select = document.getElementById('categoriaSelect');
        if (me.role !== 'admin') {
            select.innerHTML = '<option value="DIRETA">Direta</option>';
        }
    }

    toggleBroadcastGroup() {
        const me = window.grindx.session.getUserProfile();
        const categoria = document.getElementById('categoriaSelect').value;
        const canBroadcast = me.role === 'admin' && (categoria === 'SISTEMA' || categoria === 'AVISO');
        document.getElementById('broadcastGroup').style.display = canBroadcast ? 'block' : 'none';
        if (!canBroadcast) document.getElementById('broadcastCheckbox').checked = false;
        this.atualizarEstadoDestinatario();
    }

    atualizarEstadoDestinatario() {
        const broadcast = document.getElementById('broadcastCheckbox').checked;
        const dest = document.getElementById('destinatarioSelect');
        if (dest) dest.disabled = broadcast;
    }

    async enviarMensagem() {
        const destinatario_id = Number(document.getElementById('destinatarioSelect').value);
        const titulo = document.getElementById('tituloInput').value.trim();
        const texto = document.getElementById('textoInput').value.trim();
        const categoria = document.getElementById('categoriaSelect').value;
        const url_acao = document.getElementById('urlAcaoInput').value.trim() || null;
        const broadcast = document.getElementById('broadcastCheckbox').checked;

        if (!titulo || !texto) {
            this.toastWarning('Preencha título e texto.');
            return;
        }
        try {
            if (broadcast) {
                const data = await window.grindx.api.post('/mensagens/broadcast', {
                    titulo, texto, categoria, url_acao
                });
                this.fecharModal();
                this.toastSuccess(`Mensagem enviada para ${data.count} usuário(s)!`);
                if (window.grindx.notifyMensagens) window.grindx.notifyMensagens();
                if (this.status !== 'todas') {
                    this.status = 'todas';
                    document.getElementById('statusFilter').value = 'todas';
                }
                await this.loadLista();
                return;
            }
            if (!destinatario_id) {
                this.toastWarning('Selecione o destinatário.');
                return;
            }
            const msg = await window.grindx.api.post('/mensagens', {
                destinatario_id, titulo, texto, categoria, url_acao
            });
            await this.uploadAnexos(msg.id, this.composeFiles);
            this.fecharModal();
            this.toastSuccess('Mensagem enviada!');
            if (window.grindx.notifyMensagens) window.grindx.notifyMensagens();
            if (this.status !== 'todas') {
                this.status = 'todas';
                document.getElementById('statusFilter').value = 'todas';
            }
            await this.loadLista();
        } catch (err) {
            this.toastError(err);
        }
    }

    async enviarResposta() {
        const texto = document.getElementById('respostaTexto').value.trim();
        if (!texto) {
            this.toastWarning('Escreva a resposta.');
            return;
        }
        try {
            const resp = await window.grindx.api.post(`/mensagens/${this.threadId}/respostas`, { texto });
            await this.uploadAnexos(resp.id, this.replyFiles);
            document.getElementById('respostaTexto').value = '';
            this.replyFiles = [];
            this.renderArquivosPendentes('respostaArquivos', []);
            if (window.grindx.notifyMensagens) window.grindx.notifyMensagens();
            await this.abrirThread(this.threadId);
        } catch (err) {
            this.toastError(err);
        }
    }

    async uploadAnexos(mensagemId, files) {
        for (const file of files) {
            const form = new FormData();
            form.append('file', file);
            const url = window.grindx.api.buildApiUrl(`/mensagens/${mensagemId}/anexos`);
            const resp = await fetch(url, {
                method: 'POST',
                headers: { Authorization: `Bearer ${this.token}` },
                body: form
            });
            if (!resp.ok) throw new Error(`Falha ao anexar ${file.name}`);
        }
    }

    async downloadAnexo(mensagemId, anexoId, nome) {
        try {
            const url = window.grindx.api.buildApiUrl(`/mensagens/${mensagemId}/anexos/${anexoId}/download`);
            const resp = await fetch(url, {
                headers: { Authorization: `Bearer ${this.token}` }
            });
            if (!resp.ok) throw new Error('Falha ao baixar anexo.');
            const blob = await resp.blob();
            const objUrl = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = objUrl;
            a.download = nome;
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(objUrl);
        } catch (err) {
            this.toastError(err);
        }
    }

    renderArquivosPendentes(containerId, files) {
        const container = document.getElementById(containerId);
        container.innerHTML = files.map((f, i) =>
            `<span class="msg-anexo-chip"><i class="fas fa-paperclip"></i> ${this.escapeHtml(f.name)}
                <button type="button" data-remove-pendente="${i}" aria-label="Remover anexo">&times;</button>
             </span>`
        ).join('') || '';
        container.querySelectorAll('[data-remove-pendente]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const idx = Number(btn.dataset.removePendente);
                if (containerId === 'composeArquivos') {
                    this.composeFiles.splice(idx, 1);
                } else {
                    this.replyFiles.splice(idx, 1);
                }
                this.renderArquivosPendentes(containerId, containerId === 'composeArquivos' ? this.composeFiles : this.replyFiles);
            });
        });
    }

    formatDate(value) {
        if (!value) return '—';
        const date = new Date(value);
        return isNaN(date.getTime()) ? '—' : date.toLocaleString('pt-BR');
    }

    escapeHtml(value) {
        return String(value == null ? '' : value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.mensagensController = new MensagensController();
});
