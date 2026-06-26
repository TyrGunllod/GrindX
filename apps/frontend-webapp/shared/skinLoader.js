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
    layout_mode: 'topbar',
};

const FONT_CDN_MAP = {
    Inter: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
    Roboto: 'https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap',
    'Open Sans': 'https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap',
    'Barlow Condensed': 'https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;500;600;700&display=swap',
    'DM Sans': 'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap',
    Lato: 'https://fonts.googleapis.com/css2?family=Lato:wght@400;500;600;700&display=swap',
    Montserrat: 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap',
    Poppins: 'https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap',
    Nunito: 'https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700&display=swap',
    'Source Sans Pro': 'https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;500;600;700&display=swap',
};

class SkinLoader {
    constructor() {
        this.currentSkin = null;
        this._fontLinkEls = [];
        this._previewMode = false;
        this._originalSkin = null;
    }

    _resolveUrl(path) {
        if (!path) return path;
        if (path.startsWith('http://') || path.startsWith('https://')) return path;
        const apiUrl = window.grindx?.config?.API_BASE_URL || (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
            ? `http://${window.location.hostname}:8002/v1`
            : `/v1`);
        const base = apiUrl.replace(/\/v1$/, '');
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
            const baseUrl = window.grindx?.config?.API_BASE_URL || (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
                ? `http://${window.location.hostname}:8002/v1`
                : `/v1`);
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
        if (skin.fonts?.icons) {
            this._applyIconFont(skin.fonts.icons);
        } else {
            this._removeIconFont();
        }
        this._updateBranding(skin.company_name, skin.copyright_text);
        this._updateLogos(skin.logo_url, skin.logo_short_url);
        if (skin.layout_mode) {
            this.applyLayout(skin.layout_mode);
        }
    }

    /**
     * Aplica a classe de layout no <html> e dispara evento
     * @param {string} mode - 'sidebar' ou 'topbar'
     */
    applyLayout(mode) {
        const root = document.documentElement;
        root.classList.remove('layout-sidebar', 'layout-topbar');
        const validMode = ['sidebar', 'topbar'].includes(mode) ? mode : 'topbar';
        root.classList.add(`layout-${validMode}`);
        window.dispatchEvent(new CustomEvent('layoutchange', {
            detail: { mode: validMode }
        }));
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

        // Remove todos os links de font anteriores
        for (const el of this._fontLinkEls) {
            el.remove();
        }
        this._fontLinkEls = [];

        // Aplica @font-face para fontes customizadas
        if (fonts.custom && Array.isArray(fonts.custom)) {
            const style = document.createElement('style');
            style.id = 'skin-custom-fonts';
            const rules = fonts.custom.map(f => {
                const format = f.format || 'woff2';
                const src = f.url || f.data || '';
                return `@font-face { font-family: '${f.name}'; src: url('${src}') format('${format}'); font-display: swap; }`;
            }).join('\n');
            style.textContent = rules;
            document.head.appendChild(style);
            this._fontLinkEls.push(style);
        }

        // Carrega Google Fonts se necessário
        const fontNames = [fonts.heading, fonts.body].filter(Boolean);
        for (const name of fontNames) {
            if (FONT_CDN_MAP[name]) {
                const link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = FONT_CDN_MAP[name];
                document.head.appendChild(link);
                this._fontLinkEls.push(link);
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

    _applyIconFont(iconFont) {
        if (!iconFont || !iconFont.url) return;

        const existing = document.getElementById('skin-icon-font');
        if (existing) existing.remove();

        const style = document.createElement('style');
        style.id = 'skin-icon-font';
        const format = iconFont.format || 'woff2';
        style.textContent = `@font-face { font-family: '${iconFont.name}'; src: url('${iconFont.url}') format('${format}'); font-display: swap; }`;
        document.head.appendChild(style);

        document.documentElement.style.setProperty('--skin-font-icons', `'${iconFont.name}'`);
    }

    _removeIconFont() {
        const existing = document.getElementById('skin-icon-font');
        if (existing) existing.remove();
        document.documentElement.style.removeProperty('--skin-font-icons');
    }

    _updateBranding(companyName, copyrightText) {
        if (!companyName) return;

        // Atualiza título da página
        document.title = document.title.replace('GrindX', companyName);

        // Atualiza logo no sidebar
        const logoEl = document.querySelector('.logo-grindx');
        if (logoEl) {
            const textEl = logoEl.querySelector('.logo-text');
            if (textEl) textEl.textContent = companyName;
        }

        // Atualiza logo no topbar
        const topbarLogoEl = document.querySelector('.topbar-logo');
        if (topbarLogoEl) {
            const textEl = topbarLogoEl.querySelector('.logo-text');
            if (textEl) textEl.textContent = companyName;
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
        const updateLogoElement = (container) => {
            if (!container) return;
            const name = (this.currentSkin && this.currentSkin.company_name) || 'GrindX';
            const fullUrl = this._resolveUrl(logoUrl);
            let img = container.querySelector('.logo-img');
            const textEl = container.querySelector('.logo-text');
            if (!img) {
                img = document.createElement('img');
                img.className = 'logo-img';
                img.alt = 'Logo';
                img.style.maxHeight = '32px';
                img.style.width = 'auto';
                container.insertBefore(img, textEl);
            }
            img.src = fullUrl;
            if (textEl) textEl.textContent = name;
            img.onerror = function () {
                img.remove();
                if (textEl) textEl.textContent = name;
            };
        };

        if (logoUrl) {
            updateLogoElement(document.querySelector('.logo-grindx'));
            updateLogoElement(document.querySelector('.topbar-logo'));
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

    clearCache(companyId) {
        try {
            if (!window.localStorage) return;
            window.localStorage.removeItem(`skin_cache_${companyId}`);
        } catch (e) {
            console.warn('SkinLoader: Erro ao limpar cache', e);
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
                // Notifica o dashboard para re-sincronizar iframes
                window.dispatchEvent(new CustomEvent('skinupdated', { detail: { companyId } }));
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
