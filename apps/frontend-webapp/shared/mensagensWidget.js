/**
 * Mensagens Widget Manager — GrindX
 *
 * Gerencia o estado do contador de mensagens não lidas no mascote:
 * badge (contagem) e balão de fala clicável.
 *
 * Uso no browser: widget.js cria os elementos DOM e instancia este manager,
 * expondo window.grindx.mensagens.
 * Uso em testes: module.exports = { MensagensWidget } (Node test runner).
 */

(function initMensagensWidget(globalScope) {
    const DEFAULT_POLL_INTERVAL = 10 * 60 * 1000; // 10 minutos

    class MensagensWidget {
        constructor(options = {}) {
            this.badge = options.badge || null;
            this.balloon = options.balloon || null;
            this.api = options.api || null;
            this.onOpenRecados = options.onOpenRecados || null;
            this.onCountChange = options.onCountChange || null;
            this.POLL_INTERVAL = options.pollInterval || DEFAULT_POLL_INTERVAL;

            this.count = 0;
            this.seen = false;
            this.intervalId = null;

            this.getUnread = options.getUnread || this._defaultGetUnread.bind(this);

            if (options.autoInit !== false) this.init();
        }

        _defaultGetUnread() {
            if (!this.api || typeof this.api.get !== 'function') {
                return Promise.resolve(0);
            }
            return this.api
                .get('/mensagens/nao-lidas/count')
                .then((data) => (data && typeof data.count === 'number') ? data.count : 0)
                .catch(() => 0);
        }

        init() {
            this.refresh();
            this.startPolling();
        }

        startPolling() {
            if (this.intervalId) clearInterval(this.intervalId);
            this.intervalId = setInterval(() => this.refresh(), this.POLL_INTERVAL);
        }

        stopPolling() {
            if (this.intervalId) {
                clearInterval(this.intervalId);
                this.intervalId = null;
            }
        }

        async refresh() {
            const next = await this.getUnread();
            if (next > this.count) this.seen = false;
            this.count = next;
            this.render();
            if (this.onCountChange) this.onCountChange(next);
            return next;
        }

        markSeen() {
            this.seen = true;
            this.render();
        }

        openRecados() {
            this.markSeen();
            if (this.onOpenRecados) this.onOpenRecados();
        }

        render() {
            if (this.badge) {
                this.badge.textContent = this.count > 0 ? String(this.count) : '';
                this.badge.classList.toggle('visible', this.count > 0);
                this.badge.setAttribute('aria-hidden', this.count > 0 ? 'false' : 'true');
            }
            if (this.balloon) {
                const show = this.count > 0 && !this.seen;
                this.balloon.classList.toggle('visible', show);
                this.balloon.setAttribute('aria-hidden', show ? 'false' : 'true');
            }
        }
    }

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = { MensagensWidget };
    }

    if (globalScope && globalScope.document) {
        globalScope.grindx = globalScope.grindx || {};
        globalScope.grindx.MensagensWidget = MensagensWidget;
    }
})(typeof window !== 'undefined' ? window : (typeof globalThis !== 'undefined' ? globalThis : this));
