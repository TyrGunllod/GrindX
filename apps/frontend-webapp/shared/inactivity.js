/**
 * Shared Inactivity Tracker — GrindX
 *
 * Detecta inatividade do usuário, transmite atividade de iframes para o
 * dashboard pai e força logout automático após 5min com aviso nos 60s finais.
 *
 * Contextos:
 *  - Janela principal (dashboard): gerencia o timer único e executa logout.
 *  - Iframe (módulo): apenas transmite eventos de atividade ao pai via
 *    postMessage (não gerencia timer/logout próprio).
 *
 * Uso no browser: carregado após app.js, expõe window.grindx.inactivityTracker.
 * Uso em testes: module.exports = { InactivityTracker } (Node test runner).
 */

(function initInactivity(globalScope) {
    const EVENTS = ['mousemove', 'mousedown', 'keypress', 'keydown', 'scroll', 'touchstart'];
    const ACTIVITY_TYPE = 'grindx-activity';

    class InactivityTracker {
        constructor(options = {}) {
            const win = options.window || globalScope.window;
            const doc = options.document || (win ? win.document : null);

            this.window = win || null;
            this.document = doc;
            this.i18n = options.i18n || null;
            this.components = options.components || null;
            this.session = options.session || null;
            this.onLogout = options.onLogout || null;
            this.onWarning = options.onWarning || null;

            this.lastActivity = Date.now();
            this.timeoutId = null;
            this.warningTimeoutId = null;
            this.WARNING_TIME = options.warningTime || 60000;
            this.LOGOUT_TIME = options.logoutTime || 300000;
            this.isWarningShown = false;
            this.isIframe = !!(win && win.self !== win.top);

            if (options.autoInit !== false && this.document) {
                this.init();
            }
        }

        init() {
            this.bindEvents();
            if (!this.isIframe) {
                this.startTimer();
            }
        }

        destroy() {
            clearTimeout(this.timeoutId);
            clearTimeout(this.warningTimeoutId);
            this.timeoutId = null;
            this.warningTimeoutId = null;
        }

        bindEvents() {
            const doc = this.document;
            const win = this.window;
            if (!doc) return;

            EVENTS.forEach((evt) => {
                doc.addEventListener(evt, () => this.onActivity(), true);
            });

            if (win) {
                win.addEventListener('message', (e) => {
                    if (e.origin !== win.location.origin) return;
                    if (e.data && e.data.type === ACTIVITY_TYPE) {
                        this.onActivity();
                    }
                });
            }
        }

        onActivity() {
            if (this.isIframe && this.window) {
                this.window.parent.postMessage({ type: ACTIVITY_TYPE, timestamp: Date.now() }, this.window.location.origin);
                return;
            }
            this.resetTimer();
        }

        startTimer() {
            clearTimeout(this.timeoutId);
            clearTimeout(this.warningTimeoutId);
            this.warningTimeoutId = setTimeout(() => this.showWarning(), this.LOGOUT_TIME - this.WARNING_TIME);
            this.timeoutId = setTimeout(() => this.handleLogout(), this.LOGOUT_TIME);
        }

        resetTimer() {
            this.lastActivity = Date.now();
            this.isWarningShown = false;
            this.startTimer();
        }

        showWarning() {
            this.isWarningShown = true;
            const msg = (this.i18n && this.i18n.t) ? this.i18n.t('inactivity_warning')
                : 'Sua sessão será encerrada em 60 segundos';

            if (this.onWarning) {
                this.onWarning(msg);
                return;
            }
            if (this.components && this.components.LoadingSpinner) {
                this.components.LoadingSpinner.toast(msg, 'warning');
            }
            if (this.document && this.document.dispatchEvent) {
                this.document.dispatchEvent(new this.window.CustomEvent('grindx:inactivity-warning', { detail: { message: msg } }));
            }
        }

        handleLogout() {
            clearTimeout(this.timeoutId);
            clearTimeout(this.warningTimeoutId);

            if (this.onLogout) {
                this.onLogout();
                return;
            }
            if (globalScope.grindx && globalScope.grindx.serverLogout) {
                globalScope.grindx.serverLogout.notify();
            }
            if (this.session && this.session.clear) {
                this.session.clear();
            }
            if (this.document && this.document.dispatchEvent) {
                this.document.dispatchEvent(new this.window.CustomEvent('grindx:inactivity-logout'));
            }
            if (this.window) {
                this.window.location.href = 'index.html';
            }
        }
    }

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = { InactivityTracker };
    }

    if (globalScope && globalScope.document) {
        const attach = () => {
            globalScope.grindx = globalScope.grindx || {};
            const win = globalScope;
            globalScope.grindx.inactivityTracker = new InactivityTracker({
                window: win,
                document: win.document,
                i18n: win.grindx.i18n,
                components: win.grindx.components,
                session: win.grindx.session
            });
        };

        if (globalScope.document.readyState === 'loading') {
            globalScope.document.addEventListener('DOMContentLoaded', attach);
        } else {
            attach();
        }
    }
})(typeof window !== 'undefined' ? window : (typeof globalThis !== 'undefined' ? globalThis : this));