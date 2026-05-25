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
            const profile = await window.grindx.api.get('/auth/me');

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
                this.viewport.querySelectorAll('iframe').forEach(f => this.applySkinToIframe(f));
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

            document.getElementById('userAvatar')?.addEventListener('click', () => this.openPasswordModal());

            window.addEventListener('message', (e) => {
                if (e.data === 'sidebar-update') this.loadDynamicMenu();
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

        this.moduleViewport = document.getElementById('moduleViewport');
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
             this.applySkinToIframe(iframe);
         };

         this.viewport.innerHTML = '';
         this.viewport.appendChild(iframe);
     }

    applySkinToIframe(iframe) {
        if (!iframe) return;

        // Skip cross-origin iframes (external sites) — cannot access contentDocument
        let doc, root;
        try {
            doc = iframe.contentDocument;
            if (!doc) return;
            root = doc.documentElement;
            if (!root) return;
        } catch (_) {
            return;
        }

        // Sync dark/light theme class
        const theme = window.grindx.theme.theme;
        root.classList.remove('light-theme', 'dark-theme');
        root.classList.add(`${theme}-theme`);

        // Copy skin CSS variables from parent :root to iframe
        const parentRoot = document.documentElement;
        const computed = getComputedStyle(parentRoot);
        const skinVars = [
            '--skin-primary', '--skin-primary-hover', '--skin-danger', '--skin-success', '--skin-warning',
            '--skin-bg-main', '--skin-bg-card', '--skin-text-main', '--skin-text-muted',
            '--skin-border-color', '--skin-focus-ring',
            '--skin-bg-main-dark', '--skin-bg-card-dark', '--skin-text-main-dark', '--skin-text-muted-dark',
            '--skin-border-color-dark',
            '--skin-sidebar-bg', '--skin-sidebar-text', '--skin-sidebar-active',
            '--skin-header-bg', '--skin-header-text',
            '--skin-font-heading', '--skin-font-body',
            '--skin-radius-sm', '--skin-radius-md', '--skin-radius-lg', '--skin-radius-xl',
            '--skin-shadow-card', '--skin-shadow-modal',
        ];
        skinVars.forEach(v => {
            const val = computed.getPropertyValue(v).trim();
            if (val) root.style.setProperty(v, val);
        });

        // Inject fonts into iframe so modules render with the correct font faces
        const fonts = window.skinLoader?.currentSkin?.fonts;
        if (!fonts) return;

        const fontCdnMap = {
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

        // Inject Google Fonts <link> for heading and body
        [fonts.heading, fonts.body].forEach(name => {
            if (name && fontCdnMap[name]) {
                const existing = doc.querySelector(`link[href="${fontCdnMap[name]}"]`);
                if (!existing) {
                    const link = doc.createElement('link');
                    link.rel = 'stylesheet';
                    link.href = fontCdnMap[name];
                    doc.head.appendChild(link);
                }
            }
        });

        // Inject @font-face for custom fonts
        if (fonts.custom && fonts.custom.length > 0) {
            const existingStyle = doc.getElementById('skin-custom-fonts-iframe');
            if (existingStyle) existingStyle.remove();

            const style = doc.createElement('style');
            style.id = 'skin-custom-fonts-iframe';
            style.textContent = fonts.custom.map(f => {
                const fmt = f.format || 'woff2';
                const src = f.url || f.data || '';
                return `@font-face{font-family:'${f.name}';src:url('${src}')format('${fmt}');font-display:swap}`;
            }).join('\n');
            doc.head.appendChild(style);
        }
    }

    toggleSidebar(isOpen) {
        this.sidebar.classList.toggle('open', isOpen);
    }

     updateUserUI(user) {
         const displayName = this.getUserDisplayName(user);
         document.getElementById('userName').textContent = displayName;
         document.getElementById('userRole').textContent = this.formatRole(user.role);
         const icons = { admin: 'user-cog', operador: 'user-tie', leitura: 'user' };
         document.getElementById('userAvatar').innerHTML = `<i class="fas fa-${icons[user.role] || 'user'}"></i>`;
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

    openPasswordModal() {
        const modalEl = document.getElementById('passwordModal');
        if (!modalEl) return;
        this._passwordModal = new (window.grindx.components.ReusableModal)(modalEl, {
            onClose: () => {
                document.getElementById('passwordForm')?.reset();
                document.querySelectorAll('#passwordForm .field-error').forEach(e => e.remove());
                document.querySelectorAll('#passwordForm .is-invalid').forEach(e => e.classList.remove('is-invalid'));
            }
        });
        this._passwordModal.open();
        document.getElementById('savePasswordBtn')?.addEventListener('click', () => this.savePassword(), { once: true });
        document.getElementById('cancelPasswordBtn')?.addEventListener('click', () => this._passwordModal?.close(), { once: true });
    }

    async savePassword() {
        const currentPassword = document.getElementById('currentPassword')?.value;
        const newPassword = document.getElementById('newPassword')?.value;
        const confirmPassword = document.getElementById('confirmPassword')?.value;

        if (!currentPassword || !newPassword || !confirmPassword) {
            this.showPasswordError('Preencha todos os campos.');
            return;
        }
        if (newPassword !== confirmPassword) {
            this.showPasswordError('Nova senha e confirmação não conferem.');
            return;
        }
        if (newPassword.length < 6) {
            this.showPasswordError('Nova senha deve ter no mínimo 6 caracteres.');
            return;
        }

        try {
            await window.grindx.api.post('/auth/change-password', {
                current_password: currentPassword,
                new_password: newPassword,
            });
            this._passwordModal?.close();
            this.showToast('Senha alterada com sucesso.', 'success');
        } catch (err) {
            this.showPasswordError(err.message || 'Erro ao alterar senha.');
        }
    }

    showPasswordError(msg) {
        const footer = document.querySelector('#passwordModal .modal-footer');
        if (!footer) return;
        const existing = footer.querySelector('.field-error');
        if (existing) existing.remove();
        const err = document.createElement('p');
        err.className = 'field-error';
        err.textContent = msg;
        footer.parentElement.insertBefore(err, footer);
    }

    showToast(message, type = 'success') {
        const region = document.getElementById('toastRegion') || (() => {
            const r = document.createElement('div');
            r.id = 'toastRegion';
            r.className = 'toast-region';
            document.body.appendChild(r);
            return r;
        })();
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        region.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
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
                        window.skinLoader._updateBranding(theme.company_name, theme.copyright_text);
                        window.skinLoader._updateLogos(theme.logo_url, theme.logo_short_url);
                        this.viewport.querySelectorAll('iframe').forEach(f => this.applySkinToIframe(f));
                    })
                    .catch(err => {
                        console.warn('Failed to load preview skin:', err);
                        // Fallback to regular skin load
                        const companyId = this.user?.company_id;
                        if (companyId) {
                            window.skinLoader.load(parseInt(companyId)).then(() => {
                                window.grindx.storage.set('last_skin_company_id', String(companyId));
                                this.viewport.querySelectorAll('iframe').forEach(f => this.applySkinToIframe(f));
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
                this.viewport.querySelectorAll('iframe').forEach(f => this.applySkinToIframe(f));
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