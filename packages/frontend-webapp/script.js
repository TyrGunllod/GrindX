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
        const userProfile = {
            ...(result.user || result.usuario || result.profile || {}),
            username: credentials.username
        };
        window.grindx.session.setUserProfile(userProfile);

        // Salvar company_id para skin do próximo login
        if (userProfile?.empresa_id) {
            window.grindx.storage.set('last_skin_company_id', String(userProfile.empresa_id));
        }

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

// Forgot Password
class ForgotPasswordController {
    constructor() {
        this.modal = document.getElementById('forgotModal');
        this.form = document.getElementById('forgotForm');
        this.message = document.getElementById('forgotMessage');
        this.btn = document.getElementById('btnForgot');
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    open() {
        this.modal.classList.remove('hidden');
        this.message.className = 'alert';
        this.message.textContent = '';
        this.form.reset();
    }

    close() {
        this.modal.classList.add('hidden');
    }

    async handleSubmit(e) {
        e.preventDefault();
        this.btn.disabled = true;
        this.btn.querySelector('span').textContent = 'Enviando...';

        const username = document.getElementById('forgotUsername').value;

        try {
            await window.grindx.api.post('/auth/forgot-password', { username }, { auth: false });
            this.message.className = 'alert alert-success';
            this.message.textContent = 'Nova senha enviada para o e-mail cadastrado.';
        } catch (err) {
            const msg = window.grindx.components.LoadingSpinner.toUserMessage(err);
            this.message.className = 'alert alert-error';
            this.message.textContent = msg;
        } finally {
            this.btn.disabled = false;
            this.btn.querySelector('span').textContent = 'Enviar Nova Senha';
        }
    }
}

// Bootstrap
document.addEventListener('DOMContentLoaded', () => {
    const controller = new AuthController();
    window.auth = controller;

    const forgotCtrl = new ForgotPasswordController();
    controller.openForgotModal = (e) => { e.preventDefault(); forgotCtrl.open(); };
    controller.closeForgotModal = () => forgotCtrl.close();

    // Aplicar skin da última empresa usada
    const lastCompanyId = window.grindx?.storage?.get('last_skin_company_id');
    if (lastCompanyId && window.skinLoader) {
        window.skinLoader.load(parseInt(lastCompanyId));
    }
});
