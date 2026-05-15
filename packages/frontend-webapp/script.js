/**
 * LOGIN MODULE - GrindX
 * Boas Práticas: Clean Code, SOLID, i18n
 */

class AuthController {
    constructor() {
        this.form = document.getElementById('loginForm');
        this.errorMsg = document.getElementById('errorMessage');
        this.init();
    }

    init() {
        this.localize();
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    localize() {
         // Exemplo de i18n em ação
         document.getElementById('btnSubmit').querySelector('span').textContent = window.grindx.i18n.t('login');
     }

    async handleSubmit(e) {
        e.preventDefault();
        if (!this.validateForm()) return;

        this.setLoading(true);

        const credentials = Object.fromEntries(new FormData(this.form));

        try {
            const data = await this.performLogin(credentials);
            this.handleSuccess(data, credentials);
        } catch (err) {
            this.handleError(err);
        } finally {
            this.setLoading(false);
        }
    }

    async performLogin({ username, password }) {
        return window.grindx.api.post('/auth/token', { username, password }, { auth: false });
    }

    handleSuccess(result, credentials) {
        window.grindx.session.setTokens({
            accessToken: result.access_token,
            refreshToken: result.refresh_token
        });
        window.grindx.session.setUserProfile({
            ...(result.user || result.usuario || result.profile || {}),
            username: credentials.username
        });
        
        // Feedback visual amigável (A11y)
        this.errorMsg.className = 'alert alert-success';
        this.errorMsg.textContent = 'Sucesso! Redirecionando...';
        
        setTimeout(() => window.location.href = 'dashboard.html', 800);
    }

    handleError(err) {
        this.errorMsg.textContent = window.grindx.components.LoadingSpinner.toUserMessage(err);
        this.errorMsg.style.display = 'block';
    }

    validateForm() {
        const result = window.grindx.validation.validateSchema('login');

        this.errorMsg.style.display = result.valid ? 'none' : 'block';
        this.errorMsg.textContent = result.valid ? '' : 'Preencha os campos destacados.';
        return result.valid;
    }

     setLoading(isLoading) {
         const btn = document.getElementById('btnSubmit');
         btn.disabled = isLoading;
         btn.style.opacity = isLoading ? '0.7' : '1';
         btn.querySelector('span').textContent = isLoading ? 'Aguarde...' : window.grindx.i18n.t('login');
     }
}

// Bootstrap
document.addEventListener('DOMContentLoaded', () => new AuthController());
