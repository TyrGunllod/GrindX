/**
 * Notification Bridge — GrindX
 *
 * Comunicação módulo (iframe) -> janela pai via postMessage.
 *  - notifyMensagens(): avisa o pai para recalcular o contador de não lidas.
 *  - navegarPara(url): pede ao pai para navegar o iframe para um caminho interno.
 *
 * Uso no browser: carregado após apiService.js. Expõe window.grindx.notifyMensagens
 * e window.grindx.navegarPara.
 * Uso em testes: module.exports = { NotificationBridge } (Node test runner).
 */

(function initNotificationBridge(globalScope) {
    function isIframe(win) {
        if (!win) return true;
        try {
            return win.self !== win.top;
        } catch (e) {
            return true;
        }
    }

    class NotificationBridge {
        constructor(options = {}) {
            const win = options.window || globalScope.window || null;
            this.window = win;
            this.parent = options.parent || (win ? win.parent : null);
            this.origin = options.origin || '*';
            this._isIframe = options.isIframe !== undefined
                ? options.isIframe
                : isIframe(win);
        }

        notifyMensagens() {
            return this._post('grindx:mensagens-atualizar');
        }

        navegarPara(url) {
            return this._post('grindx:navegar', { url });
        }

        _post(type, payload) {
            if (!this._isIframe || !this.parent || typeof this.parent.postMessage !== 'function') {
                return false;
            }
            this.parent.postMessage(Object.assign({ type }, payload || {}), this.origin);
            return true;
        }
    }

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = { NotificationBridge };
    }

    if (globalScope && globalScope.document) {
        globalScope.grindx = globalScope.grindx || {};
        const bridge = new NotificationBridge({ window: globalScope });
        globalScope.grindx.notifyMensagens = function () {
            return bridge.notifyMensagens();
        };
        globalScope.grindx.navegarPara = function (url) {
            return bridge.navegarPara(url);
        };
    }
})(typeof window !== 'undefined' ? window : (typeof globalThis !== 'undefined' ? globalThis : this));
