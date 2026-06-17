/**
 * DASHBOARD CONTROLLER - GrindX (Versão Dinâmica)
 * Gerencia a navegação baseada na estrutura vinda da API.
 */

function debounce(fn, ms) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), ms);
  };
}

class DashboardController extends window.grindx.controllers.BaseController {
    constructor() {
        super();
        this.sidebar = document.getElementById('sidebar');
        this.mainNav = document.getElementById('mainNav');
        this.viewport = document.getElementById('moduleViewport');
        this.loader = document.getElementById('moduleLoader');
        this.topbar = document.getElementById('topbar');
        this.topbarNav = document.getElementById('topbarNav');
        this.currentLayout = 'topbar';

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
            if (profile.theme_preference) {
                window.grindx.theme.syncFromProfile(profile.theme_preference);
            }
        } catch (err) {
            console.warn('Não foi possível carregar o perfil do usuário logado:', err);
        }
    }

        setupEvents() {
            document.getElementById('openSidebar')?.addEventListener('click', () => this.toggleSidebar(true));
            document.getElementById('closeSidebar')?.addEventListener('click', () => this.toggleSidebar(false));
            document.getElementById('sidebarOverlay')?.addEventListener('click', () => this.handleSidebarOverlayClick());
            window.addEventListener('resize', debounce(() => this.handleSidebarResize(), 150));
            this.mainNav.addEventListener('click', (e) => this.handleNavigation(e));

            document.getElementById('toggleCollapse')?.addEventListener('click', () => this.toggleSidebarCollapse());

            // Preview banner events
            document.getElementById('applyPermanentBtn')?.addEventListener('click', () => this.applyPreviewSkinPermanently());
            document.getElementById('closePreviewBtn')?.addEventListener('click', () => {
                this.hideSkinPreviewBanner();
                window.skinLoader.exitPreviewMode();
                const companyId = this.user?.company_id;
                if (companyId && window.skinLoader) {
                    window.skinLoader.load(parseInt(companyId));
                }
            });

            window.addEventListener('message', (e) => {
                if (e.data === 'sidebar-update') this.loadDynamicMenu();
                if (e.data === 'profile-saved') this.loadCurrentUserProfile();
            });

            window.addEventListener('layoutchange', (e) => {
                this.applyLayout(e.detail.mode);
            });

            // Logo click handlers using event delegation
            document.addEventListener('click', (e) => {
                const logo = e.target.closest('.logo-clickable');
                if (logo) {
                    e.stopPropagation();
                    logo.classList.toggle('open');
                    logo.classList.remove('hover');
                } else {
                    document.querySelectorAll('.logo-clickable.open').forEach(el => {
                        el.classList.remove('open');
                    });
                }
            });

            // Logo hover handlers with timer to bridge gap to dropdown
            let logoHoverTimeout;
            document.querySelectorAll('.logo-clickable').forEach(el => {
                el.addEventListener('mouseenter', () => {
                    clearTimeout(logoHoverTimeout);
                    if (!el.classList.contains('open')) {
                        el.classList.add('hover');
                    }
                });
                el.addEventListener('mouseleave', () => {
                    logoHoverTimeout = setTimeout(() => {
                        el.classList.remove('hover');
                    }, 150);
                });
                const dd = el.querySelector('.user-dropdown');
                if (dd) {
                    dd.addEventListener('mouseenter', () => clearTimeout(logoHoverTimeout));
                    dd.addEventListener('mouseleave', () => {
                        logoHoverTimeout = setTimeout(() => {
                            el.classList.remove('hover');
                        }, 150);
                    });
                }
            });

            document.querySelectorAll('[data-profile="true"]').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.loadProfileModule();
                    document.querySelectorAll('.logo-clickable.open').forEach(el => {
                        el.classList.remove('open');
                    });
                });
            });

            document.getElementById('logoutBtnSidebar')?.addEventListener('click', () => this.logout());
            document.getElementById('logoutBtnTopbar')?.addEventListener('click', () => this.logout());
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
            this.renderTopbarNav(menuData);
        } catch (err) {
            console.error('Falha ao carregar menu dinâmico:', err);
        }
    }

    renderSidebar(abas) {
        this.mainNav.innerHTML = abas.map(aba => this._renderNavGroup(aba)).join('');
        this.moduleViewport = document.getElementById('moduleViewport');
    }

    renderTopbarNav(abas) {
        this._lastAbas = abas;
        if (this.currentLayout !== 'topbar') return;

        const trunc = (s, n) => s && s.length > n ? s.substring(0, n) + '...' : s;

        const groupsHtml = abas.map((aba, idx) => {
            const modulos = (aba.modulos || []).filter(mod => {
                if (mod.role_minima === 'admin' && this.user.role !== 'admin') return false;
                return true;
            });

            const childrenHtml = (aba.children || []).map(child => {
                const childMods = (child.modulos || []).filter(mod => {
                    if (mod.role_minima === 'admin' && this.user.role !== 'admin') return false;
                    return true;
                });
                return childMods.map(mod => `
                    <button class="nav-dropdown-item" data-module="${mod.slug}" data-url="${mod.url}">
                        <i class="${mod.icone || 'fas fa-cube'}"></i> <span class="nav-dropdown-text" title="${mod.nome}">${trunc(mod.nome, 16)}</span>
                    </button>
                `).join('');
            }).join('');

            const directModsHtml = modulos.map(mod => `
                <button class="nav-dropdown-item" data-module="${mod.slug}" data-url="${mod.url}">
                    <i class="${mod.icone || 'fas fa-cube'}"></i> <span class="nav-dropdown-text" title="${mod.nome}">${trunc(mod.nome, 16)}</span>
                </button>
            `).join('');

            const separator = idx < abas.length - 1 ? '<div class="nav-separator"></div>' : '';

            return `
                <div class="nav-group-topbar" data-group="${aba.id}">
                    <button class="nav-group-trigger" aria-haspopup="true" aria-expanded="false">
                        <i class="${aba.icone || 'fas fa-folder'} icon"></i>
                        <span title="${aba.nome}">${trunc(aba.nome, 16)}</span>
                        <i class="fas fa-chevron-down chevron"></i>
                        <span class="active-dot"></span>
                    </button>
                    <div class="nav-dropdown" role="menu">
                        ${childrenHtml}
                        ${directModsHtml}
                    </div>
                </div>
                ${separator}
            `;
        }).join('');

        this.topbarNav.innerHTML = `<div class="topbar-nav-scroll">${groupsHtml}</div>`;

        this._bindTopbarDropdowns();
        this._bindTopbarNavClicks();
    }

    _bindTopbarDropdowns() {
        const groups = this.topbarNav.querySelectorAll('.nav-group-topbar');
        const DROPDOWN_MARGIN = 8;

        const positionDropdown = (trigger, dropdown) => {
            const rect = trigger.getBoundingClientRect();
            const ddWidth = dropdown.offsetWidth || 300;
            let left = rect.left;
            if (left + ddWidth > window.innerWidth - DROPDOWN_MARGIN) {
                left = window.innerWidth - ddWidth - DROPDOWN_MARGIN;
            }
            if (left < DROPDOWN_MARGIN) left = DROPDOWN_MARGIN;
            dropdown.style.top = (rect.bottom + 6) + 'px';
            dropdown.style.left = left + 'px';
        };

        groups.forEach(group => {
            const trigger = group.querySelector('.nav-group-trigger');
            const dropdown = group.querySelector('.nav-dropdown');

            trigger.addEventListener('click', (e) => {
                e.stopPropagation();
                const isOpen = group.classList.contains('open');
                groups.forEach(g => {
                    g.classList.remove('open');
                    const t = g.querySelector('.nav-group-trigger');
                    if (t) t.setAttribute('aria-expanded', 'false');
                });
                if (!isOpen) {
                    positionDropdown(trigger, dropdown);
                    group.classList.add('open');
                    trigger.setAttribute('aria-expanded', 'true');
                }
            });
        });

        document.addEventListener('click', () => {
            groups.forEach(g => {
                g.classList.remove('open');
                const t = g.querySelector('.nav-group-trigger');
                if (t) t.setAttribute('aria-expanded', 'false');
            });
        });
    }

    _bindTopbarNavClicks() {
        this.topbarNav.querySelectorAll('.nav-dropdown-item[data-module]').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();

                this.topbarNav.querySelectorAll('.nav-dropdown-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');

                this.topbarNav.querySelectorAll('.nav-group-topbar').forEach(g => g.classList.remove('has-active'));
                item.closest('.nav-group-topbar')?.classList.add('has-active');

                this.navigateToModule(item.dataset.url);

                const group = item.closest('.nav-group-topbar');
                if (group) {
                    group.classList.remove('open');
                    group.querySelector('.nav-group-trigger').setAttribute('aria-expanded', 'false');
                }

                document.getElementById('activeModuleTitle').textContent = item.textContent.trim();
            });
        });
    }

    applyLayout(mode) {
        if (window.innerWidth < 1024) {
            mode = 'sidebar';
        }
        this.currentLayout = mode;
        const body = document.body;
        body.classList.remove('layout-sidebar', 'layout-topbar');
        body.classList.add(`layout-${mode}`);

        if (mode === 'topbar') {
            this.sidebar.style.display = 'none';
            this.topbar.style.display = 'flex';
            if (this._lastAbas) this.renderTopbarNav(this._lastAbas);
        } else {
            this.sidebar.style.display = '';
            this.topbar.style.display = 'none';
        }
    }

    _renderNavGroup(aba) {
        const hasChildren = aba.children && aba.children.length > 0;
        const modulesHtml = (aba.modulos || []).map(mod => {
            if (mod.role_minima === 'admin' && this.user.role !== 'admin') return '';
            return `
                <button type="button" class="nav-link" data-module="${mod.slug}" data-url="${mod.url}">
                    <i class="${mod.icone || 'fas fa-cube'} icon-sm"></i> <span>${mod.nome}</span>
                </button>
            `;
        }).join('');

        const childrenHtml = hasChildren ? aba.children.map(child => `
            <div class="nav-subgroup" id="subgroup-${child.id}">
                <div class="nav-subtitle" onclick="window.dashboard.toggleSubgroup('${child.id}')">
                    <div class="nav-title-label">
                        <i class="${child.icone || 'fas fa-folder'} icon-sm"></i>
                        <span>${child.nome}</span>
                    </div>
                    <i class="fas fa-chevron-down chevron"></i>
                </div>
                <div class="nav-links-container">
                    ${(child.modulos || []).map(mod => {
                        if (mod.role_minima === 'admin' && this.user.role !== 'admin') return '';
                        return `
                            <button type="button" class="nav-link" data-module="${mod.slug}" data-url="${mod.url}">
                                <i class="${mod.icone || 'fas fa-cube'} icon-sm"></i> <span>${mod.nome}</span>
                            </button>
                        `;
                    }).join('')}
                </div>
            </div>
        `).join('') : '';

        return `
            <div class="nav-group collapsed" id="group-${aba.id}">
                <div class="nav-title" onclick="window.dashboard.toggleGroup('${aba.id}')">
                    <div class="nav-title-label">
                        <i class="${aba.icone || 'fas fa-folder'} icon-lg"></i>
                        <span>${aba.nome}</span>
                    </div>
                    <i class="fas fa-chevron-down chevron"></i>
                </div>
                <div class="nav-links-container">
                    ${childrenHtml}
                    ${modulesHtml}
                </div>
            </div>
        `;
    }

    toggleGroup(abaId) {
        const group = document.getElementById(`group-${abaId}`);
        if (!group) return;

        const wasCollapsed = group.classList.contains('collapsed');

        this.mainNav.querySelectorAll('.nav-group').forEach(g => {
            g.classList.add('collapsed');
        });

        if (wasCollapsed) {
            group.classList.remove('collapsed');
        }
    }

    toggleSubgroup(abaId) {
        const group = document.getElementById(`subgroup-${abaId}`);
        if (!group) return;

        const wasCollapsed = group.classList.contains('collapsed');
        const parent = group.closest('.nav-links-container');

        if (parent) {
            parent.querySelectorAll('.nav-subgroup').forEach(g => {
                g.classList.add('collapsed');
            });
        }

        if (wasCollapsed) {
            group.classList.remove('collapsed');
        }
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
        const overlay = document.getElementById('sidebarOverlay');
        if (overlay) {
            overlay.classList.toggle('is-visible', isOpen);
        }
        document.body.style.overflow = isOpen ? 'hidden' : '';
    }

    handleSidebarOverlayClick() {
        this.toggleSidebar(false);
    }

    handleSidebarResize() {
        if (window.innerWidth >= 1024) {
            this.sidebar.classList.remove('open');
            const overlay = document.getElementById('sidebarOverlay');
            if (overlay) overlay.classList.remove('is-visible');
            document.body.style.overflow = '';
        }
    }

     updateUserUI(user) {
         const displayName = this.getUserDisplayName(user);
         const roleLabel = this.formatRole(user.role);
         // Sidebar dropdown
         document.getElementById('userNameSidebar').textContent = displayName;
         document.getElementById('userRoleSidebar').textContent = roleLabel;
         // Topbar dropdown
         document.getElementById('userNameTopbarDropdown').textContent = displayName;
         document.getElementById('userRoleTopbarDropdown').textContent = roleLabel;
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
        setTimeout(() => {
            const firstLink = this.mainNav.querySelector('.nav-link')
                || this.topbarNav.querySelector('.nav-dropdown-item');
            if (firstLink) firstLink.click();
        }, 500);
    }

    loadProfileModule() {
        const viewport = document.getElementById('moduleViewport');
        if (!viewport) return;
        this.showLoader(true);
        const iframe = document.createElement('iframe');
        iframe.src = 'modules/profile/index.html';
        iframe.className = 'module-frame';
        iframe.setAttribute('frameborder', '0');
        iframe.setAttribute('aria-label', 'Meu Perfil');
        viewport.innerHTML = '';
        viewport.appendChild(iframe);
        document.getElementById('activeModuleTitle').textContent = 'Meu Perfil';
        iframe.addEventListener('load', () => {
            this.showLoader(false);
            this.applySkinToIframe(iframe);
        });
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
                const isDev = window.location.port === '5500' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
                const baseUrl = window.grindx?.config?.API_BASE_URL || (isDev ? `http://${window.location.hostname}:8002/v1` : `/v1`);
                
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