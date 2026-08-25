/**
 * AUDITORIA MODULE — GrindX
 * Exibe logs de alterações no banco e o tempo de uso (sessões) dos usuários.
 * Somente leitura — consome GET /v1/audit/logs e GET /v1/audit/sessoes.
 */

class AuditoriaController extends window.grindx.controllers.BaseController {
    constructor() {
        super();
        this.PAGE_SIZE = 20;

        this.logsTable = new window.grindx.components.DataTable('logsBody', [
            { dataLabel: 'Data', render: (l) => this.formatDate(l.criado_em) },
            { className: 'hide-mobile', dataLabel: 'Usuário', render: (l) => (l.user_id ? (l.usuario_nome_completo || l.usuario_username || `#${l.user_id}`) : '—') },
            { dataLabel: 'Entidade', render: (l) => this.formatEntidade(l) },
            {
                dataLabel: 'Ação',
                render: (l) => `<span class="badge badge-${this.acaoClass(l.acao)}">${this.acaoLabel(l.acao)}</span>`,
            },
            { dataLabel: 'Campos Alterados', render: (l) => this.formatCampos(l.campos_alterados) },
            { className: 'hide-mobile', dataLabel: 'IP', render: (l) => l.ip || '—' },
        ]);

        this.sessoesTable = new window.grindx.components.DataTable('sessoesBody', [
            { dataLabel: 'Login', render: (s) => this.formatDate(s.login_at) },
            {
                dataLabel: 'Logout',
                render: (s) => (s.logout_at
                    ? this.formatDate(s.logout_at)
                    : '<span class="badge badge-success">Em uso</span>'),
            },
            { dataLabel: 'Duração', render: (s) => this.formatDuracao(s.duracao_segundos) },
            { className: 'hide-mobile', dataLabel: 'Usuário', render: (s) => (s.usuario_nome_completo || s.usuario_username || `#${s.user_id}`) },
            { className: 'hide-mobile', dataLabel: 'IP', render: (s) => s.ip || '—' },
            { dataLabel: 'Motivo', render: (s) => (s.logout_motivo ? this.motivoLabel(s.logout_motivo) : '—') },
        ]);

        this.logsPage = 1;
        this.sessoesPage = 1;
        this.logsTotalPages = 0;
        this.sessoesTotalPages = 0;

        this.init();
    }

    async init() {
        if (!this.requireAuth('../../index.html')) return;
        this.setBadgeVersao();
        this.bindEvents();
        await Promise.all([this.loadLogs(), this.loadSessoes()]);
    }

    bindEvents() {
        document.getElementById('logsPrev').addEventListener('click', () => this.changeLogsPage(-1));
        document.getElementById('logsNext').addEventListener('click', () => this.changeLogsPage(1));
        document.getElementById('sessoesPrev').addEventListener('click', () => this.changeSessoesPage(-1));
        document.getElementById('sessoesNext').addEventListener('click', () => this.changeSessoesPage(1));
    }

    async loadLogs() {
        try {
            const data = await window.grindx.api.get('/audit/logs', { page: this.logsPage, page_size: this.PAGE_SIZE });
            this.renderLogs(data);
        } catch (err) {
            console.error('Erro ao carregar logs de auditoria:', err);
            this.logsTable.renderEmpty('Erro ao carregar logs de auditoria.', 6);
        }
    }

    renderLogs(data) {
        if (!data || !data.items || data.items.length === 0) {
            this.logsTable.renderEmpty('Nenhum log registrado.', 6);
        } else {
            this.logsTable.render(data.items);
        }
        this.logsTotalPages = data.total_pages || 0;
        document.getElementById('logsTotal').textContent = `${data.total} registro(s)`;
        this.updatePageInfo('logs', data);
    }

    async loadSessoes() {
        try {
            const data = await window.grindx.api.get('/audit/sessoes', { page: this.sessoesPage, page_size: this.PAGE_SIZE });
            this.renderSessoes(data);
        } catch (err) {
            console.error('Erro ao carregar sessões de uso:', err);
            this.sessoesTable.renderEmpty('Erro ao carregar sessões de uso.', 6);
        }
    }

    renderSessoes(data) {
        if (!data || !data.items || data.items.length === 0) {
            this.sessoesTable.renderEmpty('Nenhuma sessão registrada.', 6);
        } else {
            this.sessoesTable.render(data.items);
        }
        this.sessoesTotalPages = data.total_pages || 0;
        document.getElementById('sessoesTotal').textContent = `${data.total} sessão(ões)`;
        this.updatePageInfo('sessoes', data);
    }

    updatePageInfo(kind, data) {
        const el = document.getElementById(`${kind}PageInfo`);
        el.textContent = `Página ${data.page} de ${data.total_pages || 0}`;
        document.getElementById(`${kind}Prev`).disabled = data.page <= 1;
        document.getElementById(`${kind}Next`).disabled = data.page >= (data.total_pages || 0);
    }

    changeLogsPage(delta) {
        const next = this.logsPage + delta;
        if (next < 1 || next > this.logsTotalPages) return;
        this.logsPage = next;
        this.loadLogs();
    }

    changeSessoesPage(delta) {
        const next = this.sessoesPage + delta;
        if (next < 1 || next > this.sessoesTotalPages) return;
        this.sessoesPage = next;
        this.loadSessoes();
    }

    formatDate(value) {
        if (!value) return '—';
        const date = new Date(value);
        return isNaN(date.getTime()) ? '—' : date.toLocaleString('pt-BR');
    }

    formatDuracao(segundos) {
        if (segundos === null || segundos === undefined) return '—';
        const total = Math.max(0, Math.round(segundos));
        const h = Math.floor(total / 3600);
        const m = Math.floor((total % 3600) / 60);
        const s = total % 60;
        if (h > 0) return `${h}h ${m}min`;
        if (m > 0) return `${m}min ${s}s`;
        return `${s}s`;
    }

    formatEntidade(log) {
        return log.entidade_id ? `${log.entidade} #${log.entidade_id}` : log.entidade;
    }

    formatCampos(campos) {
        if (!campos || campos.length === 0) return '—';
        const badges = campos.map((c) => `<span class="campo-badge">${c}</span>`).join(' ');
        return `<div class="campos-list">${badges}</div>`;
    }

    acaoLabel(acao) {
        const labels = { insert: 'Inserção', update: 'Alteração', delete: 'Exclusão' };
        return labels[acao] || acao;
    }

    acaoClass(acao) {
        const classes = { insert: 'success', update: 'warning', delete: 'danger' };
        return classes[acao] || 'muted';
    }

    motivoLabel(motivo) {
        const labels = { logout: 'Logout', inativo: 'Inatividade', expirado: 'Sessão expirada' };
        return labels[motivo] || motivo;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.auditoriaController = new AuditoriaController();
});
