/**
 * CORE APP FRAMEWORK - GrindX
 * Boas Práticas: i18n, SOLID, Clean Code
 */

const DEFAULT_GRINDX_CONFIG = {
    DEFAULT_LANG: 'pt-BR',
    SUPPORTED_LANGS: ['pt-BR', 'en-US', 'es-ES'],
    API_BASE_URL: window.GRINDX_CONFIG?.API_BASE_URL || `http://${window.location.hostname}:8002/v1`
};

const GRINDX_CONFIG = {
    ...DEFAULT_GRINDX_CONFIG,
    ...(window.GRINDX_CONFIG || {})
};

class StorageManager {
    constructor() {
        this.cache = new Map();
        this.initSync();
    }

    get(key, fallback = null) {
        if (this.cache.has(key)) return this.cache.get(key);

        const value = localStorage.getItem(key);
        const resolvedValue = value ?? fallback;
        this.cache.set(key, resolvedValue);
        return resolvedValue;
    }

    set(key, value) {
        localStorage.setItem(key, value);
        this.cache.set(key, value);
    }

    remove(key) {
        localStorage.removeItem(key);
        this.cache.delete(key);
    }

    clear() {
        localStorage.clear();
        this.cache.clear();
    }

    getJson(key, fallback = null) {
        const value = this.get(key);
        if (!value) return fallback;

        try {
            return JSON.parse(value);
        } catch (e) {
            return fallback;
        }
    }

    setJson(key, value) {
        this.set(key, JSON.stringify(value));
    }

    initSync() {
        window.addEventListener('storage', (event) => {
            if (!event.key) {
                this.cache.clear();
                return;
            }

            if (event.newValue === null) {
                this.cache.delete(event.key);
            } else {
                this.cache.set(event.key, event.newValue);
            }
        });
    }
}

class SessionManager {
    constructor(storage) {
        this.storage = storage;
    }

    getToken() {
        return this.storage.get('access_token');
    }

    setTokens({ accessToken, refreshToken }) {
        this.storage.set('access_token', accessToken);
        this.storage.set('refresh_token', refreshToken);
    }

    getUserProfile() {
        return this.storage.getJson('grindx_user_profile', {});
    }

    setUserProfile(profile) {
        this.storage.setJson('grindx_user_profile', profile);
    }

    clear() {
        this.storage.remove('access_token');
        this.storage.remove('refresh_token');
        this.storage.remove('grindx_user_profile');
    }
}

// 1. i18n / Localization System
const TRANSLATIONS = {
    'pt-BR': {
        login: 'Entrar',
        welcome: 'Bem-vindo ao GrindX',
        user: 'Usuário',
        pass: 'Senha',
        logout: 'Sair',
        save: 'Salvar',
        cancel: 'Cancelar'
    },
    'en-US': {
        login: 'Login',
        welcome: 'Welcome to GrindX',
        user: 'Username',
        pass: 'Password',
        logout: 'Logout',
        save: 'Save',
        cancel: 'Cancel'
    }
};

class I18nManager {
    constructor(storage) {
        this.storage = storage;
        this.lang = this.storage.get('grindx_lang', GRINDX_CONFIG.DEFAULT_LANG);
    }

    t(key) {
        return TRANSLATIONS[this.lang]?.[key] || key;
    }

    setLang(lang) {
        if (GRINDX_CONFIG.SUPPORTED_LANGS.includes(lang)) {
            this.storage.set('grindx_lang', lang);
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

    createInput({ type = 'text', label, id, placeholder, required = false, value }) {
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
        if (value !== undefined) input.value = value;
        
        container.appendChild(labelEl);
        container.appendChild(input);
        return container;
    }
};

class ThemeManager {
    constructor(storage) {
        this.storage = storage;
        this.theme = this.storage.get('grindx_theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        this.apply();
        this.initSync();
    }

    initSync() {
        // Sincronizar entre janelas/iframes (Cross-context theme sync)
        window.addEventListener('storage', (e) => {
            if (e.key === 'grindx_theme') {
                this.theme = e.newValue || this.theme;
                this.apply();
            }
        });
    }

    syncFromProfile(themePreference) {
        if (themePreference && themePreference !== this.theme) {
            this.theme = themePreference;
            this.storage.set('grindx_theme', this.theme);
            this.apply();
        }
    }

    toggle() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        this.storage.set('grindx_theme', this.theme);
        this.apply();
    }

    apply() {
        document.documentElement.classList.remove('light-theme', 'dark-theme');
        document.body.classList.remove('light-theme', 'dark-theme');
        document.documentElement.classList.add(`${this.theme}-theme`);
        document.body.classList.add(`${this.theme}-theme`);
    }
}

const storage = new StorageManager();
const session = new SessionManager(storage);

/**
 * GLOBAL API - GrindX
 *
 * Ponto de acesso central para todas as funcionalidades do frontend.
 * Módulos devem usar window.grindx para acessar:
 *   - grindx.config — Configurações da aplicação
 *   - grindx.session — Gerenciamento de sessão (tokens JWT)
 *   - grindx.storage — Armazenamento local com cache
 *   - grindx.i18n — Internacionalização
 *   - grindx.ui — Factory de componentes UI
 *   - grindx.theme — Gerenciamento de temas/skins
 *   - grindx.api — Serviço HTTP para chamadas à API
 *
 * ATENÇÃO: Este é um global singleton. Módulos NÃO devem criar
 * instâncias próprias dos managers — devem usar window.grindx.
 *
 * Ordem de carregamento:
 * 1. config.js (define window.GRINDX_CONFIG)
 * 2. app.js (usa GRINDX_CONFIG para criar grindx)
 * 3. apiService.js (adiciona grindx.api)
 * 4. Módulos (usam window.grindx.*)
 */
const grindx = {
    config: GRINDX_CONFIG,
    storage,
    session,
    i18n: new I18nManager(storage),
    ui: UIFactory,
    theme: new ThemeManager(storage),
};

window.grindx = grindx;
