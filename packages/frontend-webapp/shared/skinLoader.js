/**
 * SKIN LOADER - GrindX
 * Runtime do sistema de skins/theming.
 * Carrega e aplica skins do DB (via API) ou JSON fallback.
 */

const SKIN_DEFAULTS = {
    colors: {
        '--skin-primary': '#00c2e0',
        '--skin-primary-hover': '#00a8c4',
        '--skin-danger': '#ef4444',
        '--skin-success': '#10b981',
        '--skin-warning': '#f59e0b',
        '--skin-bg-main': '#f8fafc',
        '--skin-bg-card': '#ffffff',
        '--skin-text-main': '#1e293b',
        '--skin-text-muted': '#64748b',
        '--skin-border-color': '#e2e8f0',
        '--skin-focus-ring': 'rgba(0, 194, 224, 0.35)',
        '--skin-bg-main-dark': '#0f172a',
        '--skin-bg-card-dark': '#1e293b',
        '--skin-text-main-dark': '#f8fafc',
        '--skin-text-muted-dark': '#94a3b8',
        '--skin-border-color-dark': 'rgba(255, 255, 255, 0.05)',
    },
    fonts: { heading: 'Barlow Condensed', body: 'DM Sans' },
    icon_library: 'fontawesome',
    tokens: {
        '--skin-radius-sm': '0.25rem',
        '--skin-radius-md': '0.5rem',
        '--skin-radius-lg': '0.75rem',
        '--skin-radius-xl': '1.5rem',
        '--skin-shadow-card': '0 10px 25px rgba(0,0,0,0.1)',
        '--skin-shadow-modal': '0 20px 25px -5px rgba(0,0,0,0.2)',
    },
    company_name: 'GrindX',
    copyright_text: '© 2026 GrindX. Desenvolvido por Alex Grellet.',
    logo_url: null,
    logo_short_url: null,
};

const ICON_CDN_MAP = {
    fontawesome: 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
    lucide: 'https://unpkg.com/lucide@latest/dist/umd/lucide.min.js',
    material: 'https://fonts.googleapis.com/icon?family=Material+Icons',
};

const FONT_CDN_MAP = {
    Inter: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
    Roboto: 'https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap',
    'Open Sans': 'https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap',
};

class SkinLoader {
    constructor() {
        this.currentSkin = null;
        this._iconLinkEl = null;
        this._fontLinkEl = null;
    }

    async load(companyId) {
        let skin = null;

        // 1. Tenta API
        if (companyId) {
            skin = await this._fetchFromAPI(companyId);
        }

        // 2. Fallback para JSON local
        if (!skin) {
            skin = await this._fetchFromJSON('grindx-default');
        }

        // 3. Merge com defaults
        const merged = this._deepMerge(SKIN_DEFAULTS, skin || {});
        this.currentSkin = merged;

        // 4. Aplica
        this._applyColors(merged.colors);
        this._applyTokens(merged.tokens);
        this._applyFonts(merged.fonts);
        this._loadIconLibrary(merged.icon_library);
        this._updateBranding(merged.company_name, merged.copyright_text);
        this._updateLogos(merged.logo_url, merged.logo_short_url);
    }

    async reload(companyId) {
        await this.load(companyId);
    }

    async _fetchFromAPI(companyId) {
        try {
            const token = window.grindx?.session?.getToken();
            const headers = token ? { Authorization: `Bearer ${token}` } : {};
            const baseUrl = window.grindx?.config?.API_BASE_URL || 'http://127.0.0.1:8002/v1';
            const resp = await fetch(`${baseUrl}/themes/active`, { headers });
            if (!resp.ok) return null;
            return await resp.json();
        } catch (e) {
            console.warn('SkinLoader: API indisponível, usando fallback', e);
            return null;
        }
    }

    async _fetchFromJSON(skinName) {
        try {
            const resp = await fetch(`skins/${skinName}.json`);
            if (!resp.ok) return null;
            return await resp.json();
        } catch (e) {
            console.warn('SkinLoader: JSON fallback indisponível', e);
            return null;
        }
    }

    _deepMerge(target, source) {
        const result = { ...target };
        for (const key of Object.keys(source)) {
            if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
                result[key] = this._deepMerge(target[key] || {}, source[key]);
            } else if (source[key] !== undefined && source[key] !== null) {
                result[key] = source[key];
            }
        }
        return result;
    }

    _applyColors(colors) {
        if (!colors) return;
        const root = document.documentElement;
        for (const [key, value] of Object.entries(colors)) {
            if (key.startsWith('--skin-')) {
                root.style.setProperty(key, value);
            }
        }
    }

    _applyTokens(tokens) {
        if (!tokens) return;
        const root = document.documentElement;
        for (const [key, value] of Object.entries(tokens)) {
            if (key.startsWith('--skin-')) {
                root.style.setProperty(key, value);
            }
        }
    }

    _applyFonts(fonts) {
        if (!fonts) return;

        // Remove font link anterior
        if (this._fontLinkEl) {
            this._fontLinkEl.remove();
            this._fontLinkEl = null;
        }

        // Carrega Google Fonts se necessário
        const fontNames = [fonts.heading, fonts.body].filter(Boolean);
        for (const name of fontNames) {
            if (FONT_CDN_MAP[name]) {
                const link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = FONT_CDN_MAP[name];
                document.head.appendChild(link);
                this._fontLinkEl = link;
            }
        }

        // Aplica font-family
        const root = document.documentElement;
        if (fonts.heading) {
            root.style.setProperty('--skin-font-heading', `'${fonts.heading}', 'Arial Narrow', sans-serif`);
        }
        if (fonts.body) {
            root.style.setProperty('--skin-font-body', `'${fonts.body}', system-ui, -apple-system, sans-serif`);
        }
    }

    _loadIconLibrary(library) {
        if (!library || library === 'fontawesome') return;

        // Remove link anterior
        if (this._iconLinkEl) {
            this._iconLinkEl.remove();
            this._iconLinkEl = null;
        }

        const cdnUrl = ICON_CDN_MAP[library];
        if (!cdnUrl) return;

        if (library === 'lucide') {
            const script = document.createElement('script');
            script.src = cdnUrl;
            script.onload = () => {
                if (window.lucide) {
                    window.lucide.createIcons();
                }
            };
            document.head.appendChild(script);
            this._iconLinkEl = script;
        } else {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = cdnUrl;
            document.head.appendChild(link);
            this._iconLinkEl = link;
        }
    }

    _updateBranding(companyName, copyrightText) {
        if (!companyName) return;

        // Atualiza título da página
        document.title = document.title.replace('GrindX', companyName);

        // Atualiza logo no sidebar
        const logoEl = document.querySelector('.logo-grindx');
        if (logoEl) {
            logoEl.innerHTML = companyName.substring(0, 1) + '<span class="logo-full">' + companyName.substring(1) + '</span>';
        }

        // Atualiza copyright no sidebar
        const copyrightEl = document.querySelector('.copyright-text');
        if (copyrightEl && copyrightText) {
            copyrightEl.textContent = copyrightText;
        }

        // Atualiza copyright no login
        const loginCopyright = document.querySelector('.login-page .text-center[style*="font-size: 0.7rem"]');
        if (loginCopyright && copyrightText) {
            loginCopyright.textContent = copyrightText;
        }
    }

    _updateLogos(logoUrl, logoShortUrl) {
        if (logoUrl) {
            const logoEl = document.querySelector('.logo-grindx');
            if (logoEl) {
                logoEl.innerHTML = `<img src="${logoUrl}" alt="Logo" style="max-height: 32px; width: auto;">`;
            }
        }
        if (logoShortUrl) {
            const favicon = document.querySelector('link[rel="icon"]');
            if (favicon) {
                favicon.href = logoShortUrl;
            }
        }
    }

    // Live preview para admin module
    applyPreviewColors(colors) {
        if (!colors) return;
        const root = document.documentElement;
        for (const [key, value] of Object.entries(colors)) {
            if (key.startsWith('--skin-')) {
                root.style.setProperty(key, value);
            }
        }
    }

    resetToDefaults() {
        const root = document.documentElement;
        for (const [key, value] of Object.entries(SKIN_DEFAULTS.colors)) {
            root.style.setProperty(key, value);
        }
        for (const [key, value] of Object.entries(SKIN_DEFAULTS.tokens)) {
            root.style.setProperty(key, value);
        }
    }
}

// Instância global
window.skinLoader = new SkinLoader();
