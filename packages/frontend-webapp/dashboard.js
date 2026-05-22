/**
 * DASHBOARD CONTROLLER - GrindX (Versão Dinâmica)
 * Gerencia a navegação baseada na estrutura vinda da API.
 */

class DashboardController extends window.grindx.controllers.BaseController {
    constructor() {
        super();
        this.sidebar = document.getElementById('sidebar');
        this.mainNav = document.getElementById('mainNav');
        this.viewport = document.getElementById('moduleViewport');
        this.loader = document.getElementById('moduleLoader');

        this.init();
    }

    async init() {
        this.checkAuth();
        this.checkSidebarState();
        this.setupEvents();
        await this.loadCurrentUserProfile();
        await this.loadDynamicMenu();
        this.loadInitialView();
        this.loadCompanySkin();
    }

    checkAuth() {
        if (!this.token) {
            window.location.href = 'index.html';
            return;
        }

        const user = {
            ...this.parseJwt(this.token),
            ...this.getStoredUserProfile()
        };
        this.user = user;
        this.updateUserUI(user);
    }

    async loadCurrentUserProfile() {
        try {
            const result = await window.grindx.api.get('/usuarios');
            const users = Array.isArray(result?.items) ? result.items : [];
            const profile = users.find(user => String(user.id) === String(this.user?.sub))
                || users.find(user => user.username === this.user?.username);

            if (!profile) return;

            this.user = { ...this.user, ...profile };
            window.grindx.session.setUserProfile(profile);
            this.updateUserUI(this.user);
        } catch (err) {
            console.warn('Não foi possível carregar o perfil do usuário logado:', err);
        }
    }

        setupEvents() {
            document.getElementById('openSidebar')?.addEventListener('click', () => this.toggleSidebar(true));
            document.getElementById('closeSidebar')?.addEventListener('click', () => this.toggleSidebar(false));
            this.mainNav.addEventListener('click', (e) => this.handleNavigation(e));
            document.getElementById('logoutBtn')?.addEventListener('click', () => this.logout());

            document.getElementById('themeToggle')?.addEventListener('click', () => {
                window.grindx.theme.toggle();
                this.updateThemeIcon();
                this.syncIframeTheme();
            });

            document.getElementById('toggleCollapse')?.addEventListener('click', () => this.toggleSidebarCollapse());

            // Preview banner events
            document.getElementById('applyPermanentBtn')?.addEventListener('click', () => this.applyPreviewSkinPermanently());
            document.getElementById('closePreviewBtn')?.addEventListener('click', () => {
                this.hideSkinPreviewBanner();
                window.skinLoader.exitPreviewMode();
                // Reload normal skin
                const companyId = this.user?.company_id;
                if (companyId && window.skinLoader) {
                    window.skinLoader.load(parseInt(companyId));
                }
            });

        }

    toggleSidebarCollapse() {
        this.sidebar.classList.toggle('collapsed');
        // Salvar estado no localStorage para persistência
        window.grindx.storage.set('sidebar_collapsed', this.sidebar.classList.contains('collapsed'));
    }

    checkSidebarState() {
        if (window.grindx.storage.get('sidebar_collapsed') === 'true') {
            this.sidebar.classList.add('collapsed');
        }
    }


    async loadDynamicMenu() {
        try {
            const menuData = await window.grindx.api.get('/portal/menu');
            this.renderSidebar(menuData);
        } catch (err) {
            console.error('Falha ao carregar menu dinâmico:', err);
        }
    }

    renderSidebar(abas) {
        this.mainNav.innerHTML = abas.map(aba => `
            <div class="nav-group collapsed" id="group-${aba.id}">
                <div class="nav-title" onclick="window.dashboard.toggleGroup('${aba.id}')">
                    <div class="nav-title-label">
                        <i class="${aba.icone || 'fas fa-folder'} icon-lg"></i>
                        <span>${aba.nome}</span>
                    </div>
                    <i class="fas fa-chevron-down chevron"></i>
                </div>
                <div class="nav-links-container">
                    ${aba.modulos.map(mod => {
                        if (mod.role_minima === 'admin' && this.user.role !== 'admin') return '';
                        return `
                            <a href="#" class="nav-link" data-module="${mod.slug}" data-url="${mod.url}" role="button">
                                <i class="${mod.icone || 'fas fa-cube'} icon-sm"></i> <span>${mod.nome}</span>
                            </a>
                        `;
                    }).join('')}
                </div>
            </div>
        `).join('');

        const lib = window.skinLoader?.currentSkin?.icon_library;
        if (lib && lib !== 'fontawesome' && window.skinLoader) {
            window.skinLoader._replacePageIcons(lib);
        }
    }

    toggleGroup(abaId) {
        const group = document.getElementById(`group-${abaId}`);
        if (group) group.classList.toggle('collapsed');
    }


    handleNavigation(e) {
        const link = e.target.closest('.nav-link');
        if (!link) return;

        e.preventDefault();
        this.mainNav.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        link.classList.add('active');

        // Atualizar título no topo
        const moduleName = link.querySelector('span').textContent;
        document.getElementById('activeModuleTitle').textContent = moduleName;

        this.navigateToModule(link.dataset.url);
        if (window.innerWidth < 1024) this.toggleSidebar(false);
    }

     navigateToModule(url) {
         if (!url) return;
         this.showLoader(true);

         const iframe = document.createElement('iframe');
         iframe.src = url;
         iframe.onload = () => {
             this.showLoader(false);
             this.syncIframeTheme(iframe);
         };

         this.viewport.innerHTML = '';
         this.viewport.appendChild(iframe);
     }

    syncIframeTheme(targetIframe) {
         const iframe = targetIframe || this.viewport.querySelector('iframe');
         if (iframe && iframe.contentDocument) {
             const theme = window.grindx.theme.theme;
             const doc = iframe.contentDocument;
             if (doc.documentElement) {
                 doc.documentElement.classList.remove('light-theme', 'dark-theme');
                 doc.documentElement.classList.add(`${theme}-theme`);
             }
             if (doc.body) {
                 doc.body.classList.remove('light-theme', 'dark-theme');
                 doc.body.classList.add(`${theme}-theme`);
             }
         }
     }

    toggleSidebar(isOpen) {
        this.sidebar.classList.toggle('open', isOpen);
    }

     updateUserUI(user) {
         const displayName = this.getUserDisplayName(user);
         document.getElementById('userName').textContent = displayName;
         document.getElementById('userRole').textContent = this.formatRole(user.role);
         document.getElementById('userAvatar').innerHTML = '<i class="fas fa-user"></i>';
     }

    getUserDisplayName(user) {
        return user?.nome_completo
            || user.name
            || user.username
            || user.email
            || (user.sub === '1' ? 'Administrador' : 'Usuário');
    }

    getInitials(name) {
        return name
            .split(' ')
            .filter(Boolean)
            .slice(0, 2)
            .map(part => part[0])
            .join('')
            .toUpperCase();
    }

    formatRole(role) {
        const labels = {
            admin: 'Administrador',
            operador: 'Operador',
            leitura: 'Leitura'
        };
        return labels[role] || String(role || 'Usuário').toUpperCase();
    }

    updateThemeIcon() {
        const icon = document.querySelector('#themeToggle i');
        if (icon) icon.className = window.grindx.theme.theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }

    showLoader(show) {
        if (this.loader) this.loader.style.display = show ? 'flex' : 'none';
    }

    logout() {
        window.grindx.session.clear();
        window.location.href = 'index.html';
    }

    parseJwt(token) {
        try {
            const payload = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
            return JSON.parse(atob(payload));
        } catch (e) {
            return {};
        }
    }

    getStoredUserProfile() {
        return window.grindx.session.getUserProfile();
    }

    loadInitialView() {
        // Tenta carregar o primeiro módulo disponível ou o dashboard
        setTimeout(() => {
            const firstLink = this.mainNav.querySelector('.nav-link');
            if (firstLink) firstLink.click();
        }, 500);
    }

    loadCompanySkin() {
        // Check if we're in preview mode via query parameter
        const urlParams = new URLSearchParams(window.location.search);
        const skinPreviewId = urlParams.get('skin_preview');
        
        if (skinPreviewId && window.skinLoader) {
            // Show preview banner
            this.showSkinPreviewBanner();
            
            // Load theme in preview mode (doesn't update cache or permanent settings)
            window.skinLoader.load(null, false).then(() => {
                // Fetch the specific theme for preview
                const token = window.grindx?.session?.getToken();
                const headers = token ? { Authorization: `Bearer ${token}` } : {};
                const baseUrl = window.grindx?.config?.API_BASE_URL || 'http://127.0.0.1:8002/v1';
                
                fetch(`${baseUrl}/themes/${skinPreviewId}`, { headers })
                    .then(resp => {
                        if (!resp.ok) throw new Error('Failed to fetch theme');
                        return resp.json();
                    })
                    .then(theme => {
                        // Update banner text with theme name
                        document.getElementById('skinPreviewBannerText').textContent = 
                            `🔍 Preview da skin '${theme.name || 'Sem nome'}'`;
                        
                        // Apply preview colors without saving to cache
                        window.skinLoader.applyPreviewColors(theme.colors);
                        window.skinLoader._applyTokens(theme.tokens);
                        window.skinLoader._applyFonts(theme.fonts);
                        window.skinLoader._loadIconLibrary(theme.icon_library);
                        window.skinLoader._replacePageIcons(theme.icon_library);
                        window.skinLoader._updateBranding(theme.company_name, theme.copyright_text);
                        window.skinLoader._updateLogos(theme.logo_url, theme.logo_short_url);
                    })
                    .catch(err => {
                        console.warn('Failed to load preview skin:', err);
                        // Fallback to regular skin load
                        const companyId = this.user?.company_id;
                        if (companyId) {
                            window.skinLoader.load(parseInt(companyId)).then(() => {
                                window.grindx.storage.set('last_skin_company_id', String(companyId));
                            });
                        }
                        
                        // Hide banner on error
                        this.hideSkinPreviewBanner();
                    });
            });
            return;
        }
        
        // Normal skin loading
        const companyId = this.user?.company_id;
        if (companyId && window.skinLoader) {
            window.skinLoader.load(parseInt(companyId)).then(() => {
                window.grindx.storage.set('last_skin_company_id', String(companyId));
            });
        }
    }

    /**
     * Shows the skin preview banner
     */
    showSkinPreviewBanner() {
        const banner = document.getElementById('skinPreviewBanner');
        if (banner) {
            banner.style.display = 'flex';
            // Adjust top-bar padding to account for banner
            const topBar = document.querySelector('.top-bar');
            if (topBar) {
                topBar.style.paddingTop = '60px'; // 48px banner + 12px spacing
            }
        }
    }

    /**
     * Hides the skin preview banner
     */
    hideSkinPreviewBanner() {
        const banner = document.getElementById('skinPreviewBanner');
        if (banner) {
            banner.style.display = 'none';
            // Reset top-bar padding
            const topBar = document.querySelector('.top-bar');
            if (topBar) {
                topBar.style.paddingTop = '15px';
            }
        }
    }

    /**
     * Applies the preview skin permanently
     */
    applyPreviewSkinPermanently() {
        if (!window.skinLoader._previewMode || !window.skinLoader.currentSkin) return;
        
        const companyId = this.user?.company_id;
        if (!companyId) return;
        
        // Get the current preview skin data
        const previewSkin = window.skinLoader.currentSkin;
        
        // Update the theme permanently via API
        // We need to find or create a theme with these settings
        // For simplicity, we'll just apply it and save to cache
        window.skinLoader.exitPreviewMode();
        window.skinLoader.load(companyId, false); // Reload from API to get current state
        window.skinLoader._saveToCache(companyId, previewSkin);
        
        // Hide banner
        this.hideSkinPreviewBanner();
        
        // Show success message
        alert('Skin aplicada permanentemente!');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new DashboardController();
});