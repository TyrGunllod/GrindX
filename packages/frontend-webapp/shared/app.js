/**
 * CORE APP FRAMEWORK - SGI
 * Boas Práticas: i18n, SOLID, Clean Code
 */

const SGI_CONFIG = {
    DEFAULT_LANG: 'pt-BR',
    SUPPORTED_LANGS: ['pt-BR', 'en-US', 'es-ES'],
    API_BASE_URL: 'http://127.0.0.1:8002/v1'
};

// 1. i18n / Localization System
const TRANSLATIONS = {
    'pt-BR': {
        login: 'Entrar',
        welcome: 'Bem-vindo ao SGI',
        user: 'Usuário',
        pass: 'Senha',
        logout: 'Sair',
        save: 'Salvar',
        cancel: 'Cancelar'
    },
    'en-US': {
        login: 'Login',
        welcome: 'Welcome to SGI',
        user: 'Username',
        pass: 'Password',
        logout: 'Logout',
        save: 'Save',
        cancel: 'Cancel'
    }
};

class I18nManager {
    constructor() {
        this.lang = localStorage.getItem('sgi_lang') || SGI_CONFIG.DEFAULT_LANG;
    }

    t(key) {
        return TRANSLATIONS[this.lang]?.[key] || key;
    }

    setLang(lang) {
        if (SGI_CONFIG.SUPPORTED_LANGS.includes(lang)) {
            localStorage.setItem('sgi_lang', lang);
            location.reload();
        }
    }
}

// 2. Component-Driven UI Factory (SOLID)
const UIFactory = {
    createButton({ text, icon, variant = 'primary', onClick, ariaLabel }) {
        const btn = document.createElement('button');
        btn.className = `btn btn-${variant}`;
        if (ariaLabel) btn.setAttribute('aria-label', ariaLabel);
        
        const iconHtml = icon ? `<i class="${icon}"></i>` : '';
        btn.innerHTML = `${iconHtml} <span>${text}</span>`;
        
        if (onClick) btn.onclick = onClick;
        return btn;
    },

    createInput({ type = 'text', label, id, placeholder, required = false }) {
        const container = document.createElement('div');
        container.className = 'form-group';
        
        const labelEl = document.createElement('label');
        labelEl.setAttribute('for', id);
        labelEl.textContent = label;
        
        const input = document.createElement('input');
        input.type = type;
        input.id = id;
        input.placeholder = placeholder;
        input.required = required;
        input.className = 'form-control';
        
        container.appendChild(labelEl);
        container.appendChild(input);
        return container;
    }
};

class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('sgi_theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        this.apply();
        this.initSync();
    }

    initSync() {
        // Sincronizar entre janelas/iframes (Cross-context theme sync)
        window.addEventListener('storage', (e) => {
            if (e.key === 'sgi_theme') {
                this.theme = e.newValue;
                this.apply();
            }
        });
    }

    toggle() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        localStorage.setItem('sgi_theme', this.theme);
        this.apply();
    }

    apply() {
        document.body.classList.remove('light-theme', 'dark-theme');
        document.body.classList.add(`${this.theme}-theme`);
    }
}

// Export Singleton Instance
const sgi = {
    config: SGI_CONFIG,
    i18n: new I18nManager(),
    ui: UIFactory,
    theme: new ThemeManager()
};

window.sgi = sgi; // Global accessibility
