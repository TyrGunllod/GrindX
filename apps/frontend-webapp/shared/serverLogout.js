/**
 * Shared Server Logout — GrindX
 *
 * Notifica o servidor sobre o logout (fire-and-forget) para registrar o
 * tempo de uso do usuário. Tolerante a falhas: nunca bloqueia nem impede
 * o logout local — qualquer erro de rede é silenciosamente ignorado.
 *
 * Uso no browser: carregado após apiService.js, expõe window.grindx.serverLogout.
 * Uso em testes: module.exports = { ServerLogout } (Node test runner).
 */

(function initServerLogout(globalScope) {
    const AUTH_LOGOUT_ENDPOINT = '/auth/logout';

    class ServerLogout {
        constructor(options = {}) {
            this.window = options.window || globalScope.window || null;
            this.fetchImpl = options.fetch
                || (this.window && this.window.fetch ? this.window.fetch.bind(this.window) : null)
                || (typeof fetch !== 'undefined' ? fetch.bind(null) : null);
        }

        buildUrl() {
            const w = this.window;
            if (!w) return null;
            if (w.grindx && w.grindx.api && w.grindx.api.buildApiUrl) {
                return w.grindx.api.buildApiUrl(AUTH_LOGOUT_ENDPOINT);
            }
            const hostname = w.location.hostname;
            const isLocal = hostname === 'localhost' || hostname === '127.0.0.1';
            return (isLocal ? `http://${hostname}:8002/v1` : '/v1') + AUTH_LOGOUT_ENDPOINT;
        }

        notify() {
            const w = this.window;
            if (!w || !this.fetchImpl) return Promise.resolve();

            const token = w.grindx && w.grindx.session && w.grindx.session.getToken
                ? w.grindx.session.getToken()
                : null;
            if (!token) return Promise.resolve();

            const url = this.buildUrl();
            if (!url) return Promise.resolve();

            try {
                return this.fetchImpl(url, {
                    method: 'POST',
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                    body: '{}',
                    keepalive: true,
                }).catch(() => {});
            } catch (e) {
                return Promise.resolve();
            }
        }
    }

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = { ServerLogout };
    }

    if (globalScope && globalScope.window) {
        globalScope.grindx = globalScope.grindx || {};
        globalScope.grindx.serverLogout = new ServerLogout();
    }
})(typeof window !== 'undefined' ? window : (typeof globalThis !== 'undefined' ? globalThis : this));