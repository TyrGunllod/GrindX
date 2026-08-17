/**
 * Shared controller base class.
 */

(function initBaseController() {
    class BaseController {
        constructor() {
            this.token = window.grindx.session.getToken();
        }

        requireAuth(redirectTo = 'index.html') {
            if (this.token) return true;

            window.location.href = redirectTo;
            return false;
        }

        setBadgeVersao() {
            const el = document.getElementById('viz-version');
            if (!el) return;
            window.grindx.version.get((v) => {
                if (v) {
                    el.textContent = v;
                    el.setAttribute('aria-label', `Versão do sistema ${v}`);
                } else {
                    el.style.display = 'none';
                }
            });
        }

        toastSuccess(message) {
            window.grindx.components.LoadingSpinner.toast(message, 'success');
        }

        toastWarning(message) {
            window.grindx.components.LoadingSpinner.toast(message, 'warning');
        }

        toastError(error) {
            window.grindx.components.LoadingSpinner.toast(
                window.grindx.components.LoadingSpinner.toUserMessage(error),
                'error'
            );
        }
    }

    window.grindx = window.grindx || {};
    window.grindx.controllers = {
        ...(window.grindx.controllers || {}),
        BaseController
    };
})();
