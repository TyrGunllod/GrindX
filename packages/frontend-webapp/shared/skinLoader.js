/**
 * SKIN LOADER - GrindX
 * Runtime do sistema de skins/theming.
 * Carrega e aplica skins do DB (via API) ou JSON fallback.
 * Inclui cache localStorage e modo preview.
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
    copyright_text: '© 2026 GrindX. Todos os direitos reservados.',
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
        this._previewMode = false;
        this._originalSkin = null;
    }

    _resolveUrl(path) {
        if (!path) return path;
        if (path.startsWith('http://') || path.startsWith('https://')) return path;
        const base = (window.grindx?.config?.API_BASE_URL || 'http://127.0.0.1:8002/v1').replace(/\/v1$/, '');
        return base + path;
    }

    /**
     * Carrega uma skin com cache localStorage
     * @param {number|string} companyId - ID da empresa
     * @param {boolean} useCache - Se deve usar cache (padrão: true)
     */
    async load(companyId, useCache = true) {
        // 1. Tentar cache localStorage primeiro (se habilitado)
        if (useCache) {
            const cached = this._getFromCache(companyId);
            if (cached) {
                // Aplicar cache imediatamente (zero flash)
                const merged = this._deepMerge(SKIN_DEFAULTS, cached);
                this.currentSkin = merged;
                this._applySkin(merged);
                
                // Atualizar em background
                this._fetchAndUpdateCache(companyId, merged).catch(() => {});
                return;
            }
        }

        // 2. Tenta API
        let skin = null;
        if (companyId) {
            skin = await this._fetchFromAPI(companyId);
        }

        // 3. Fallback para JSON local
        if (!skin) {
            skin = await this._fetchFromJSON('grindx-default');
        }

        // 4. Merge com defaults
        const merged = this._deepMerge(SKIN_DEFAULTS, skin || {});
        this.currentSkin = merged;

        // 5. Aplicar e atualizar cache
        this._applySkin(merged);
        this._saveToCache(companyId, merged);
    }

    /**
     * Recarrega a skin, ignorando cache
     * @param {number|string} companyId - ID da empresa
     */
    async reload(companyId) {
        await this.load(companyId, false); // Ignorar cache
    }

    /**
     * Aplica cores em modo preview (sem salvar no cache)
     * @param {Object} colors - Objeto de cores para aplicar
     */
    applyPreviewColors(colors) {
        if (!colors) return;
        this._previewMode = true;
        this._originalSkin = this.currentSkin;
        
        const root = document.documentElement;
        for (const [key, value] of Object.entries(colors)) {
            if (key.startsWith('--skin-')) {
                root.style.setProperty(key, value);
            }
        }
    }

    /**
     * Sai do modo preview e restaura a skin original
     */
    exitPreviewMode() {
        if (!this._previewMode || !this._originalSkin) return;
        
        this._previewMode = false;
        this._applySkin(this._originalSkin);
        this._originalSkin = null;
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

    _applySkin(skin) {
        this._applyColors(skin.colors);
        this._applyTokens(skin.tokens);
        this._applyFonts(skin.fonts);
        this._loadIconLibrary(skin.icon_library);
        this._updateBranding(skin.company_name, skin.copyright_text);
        this._updateLogos(skin.logo_url, skin.logo_short_url);
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
        if (!library) return;

        // Remove biblioteca dinâmica carregada anteriormente
        if (this._iconLinkEl) {
            this._iconLinkEl.remove();
            this._iconLinkEl = null;
        }

        // Remove quaisquer links do Font Awesome do DOM
        const faLinks = document.querySelectorAll('link[href*="font-awesome"]');
        faLinks.forEach(el => el.remove());

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

        // Auto-genera copyright se não fornecido
        if (!copyrightText) {
            const year = new Date().getFullYear();
            copyrightText = `© ${year} ${companyName}. Todos os direitos reservados.`;
        }

        // Atualiza copyright no sidebar
        const copyrightEl = document.querySelector('.copyright-text');
        if (copyrightEl) {
            copyrightEl.textContent = copyrightText;
        }

        // Atualiza copyright no login
        const loginCopyright = document.querySelector('.login-page .text-center[style*="font-size: 0.7rem"]');
        if (loginCopyright) {
            loginCopyright.textContent = copyrightText;
        }
    }

    _updateLogos(logoUrl, logoShortUrl) {
        if (logoUrl) {
            const logoEl = document.querySelector('.logo-grindx');
            if (logoEl) {
                const name = (this.currentSkin && this.currentSkin.company_name) || 'GrindX';
                const initial = name.substring(0, 1);
                const rest = name.substring(1);
                const fullUrl = this._resolveUrl(logoUrl);
                logoEl.innerHTML = '';
                const img = document.createElement('img');
                img.src = fullUrl;
                img.alt = 'Logo';
                img.style.maxHeight = '32px';
                img.style.width = 'auto';
                img.onerror = function () {
                    this.outerHTML = initial + '<span class="logo-full">' + rest + '</span>';
                };
                logoEl.appendChild(img);
            }
        }
        if (logoShortUrl) {
            const favicon = document.querySelector('link[rel="icon"]');
            if (favicon) {
                favicon.href = logoShortUrl;
            }
        }
    }

    _getFromCache(companyId) {
        try {
            if (!window.localStorage) return null;
            const cacheKey = `skin_cache_${companyId}`;
            const cached = window.localStorage.getItem(cacheKey);
            if (!cached) return null;
            
            const parsed = JSON.parse(cached);
            // Cache válido por 5 minutos
            if (Date.now() - parsed.timestamp > 5 * 60 * 1000) {
                window.localStorage.removeItem(cacheKey);
                return null;
            }
            return parsed.data;
        } catch (e) {
            console.warn('SkinLoader: Erro ao ler cache', e);
            return null;
        }
    }

    _saveToCache(companyId, skinData) {
        try {
            if (!window.localStorage) return;
            const cacheKey = `skin_cache_${companyId}`;
            const cacheData = {
                timestamp: Date.now(),
                data: skinData
            };
            window.localStorage.setItem(cacheKey, JSON.stringify(cacheData));
        } catch (e) {
            console.warn('SkinLoader: Erro ao salvar cache', e);
        }
    }

    async _fetchAndUpdateCache(companyId, currentSkin) {
        try {
            const skin = await this._fetchFromAPI(companyId);
            if (!skin) return;
            
            const merged = this._deepMerge(SKIN_DEFAULTS, skin);
            // Só atualizar se houver diferenças significativas
            if (JSON.stringify(merged) !== JSON.stringify(currentSkin)) {
                this.currentSkin = merged;
                this._applySkin(merged);
                this._saveToCache(companyId, merged);
            }
        } catch (e) {
            // Silencioso - manter cache atual
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
