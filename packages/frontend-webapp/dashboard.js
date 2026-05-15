/**
 * DASHBOARD CONTROLLER - GrindX (Versão Dinâmica)
 * Gerencia a navegação baseada na estrutura vinda da API.
 */

class DashboardController {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.mainNav = document.getElementById('mainNav');
        this.viewport = document.getElementById('moduleViewport');
        this.loader = document.getElementById('moduleLoader');
        this.token = localStorage.getItem('access_token');
        
        this.init();
    }

    async init() {
        this.checkAuth();
        this.checkSidebarState();
        this.setupEvents();
        await this.loadCurrentUserProfile();
        await this.loadDynamicMenu();
        this.loadInitialView();
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
            localStorage.setItem('grindx_user_profile', JSON.stringify(profile));
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
    }

    toggleSidebarCollapse() {
        this.sidebar.classList.toggle('collapsed');
        // Salvar estado no localStorage para persistência
        localStorage.setItem('sidebar_collapsed', this.sidebar.classList.contains('collapsed'));
    }

    checkSidebarState() {
        if (localStorage.getItem('sidebar_collapsed') === 'true') {
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
            <div class="nav-group" id="group-${aba.id}">
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
             const body = iframe.contentDocument.body;
             if (body) {
                 body.classList.remove('light-theme', 'dark-theme');
                 body.classList.add(`${theme}-theme`);
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
        document.getElementById('userAvatar').textContent = this.getInitials(displayName);
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
        localStorage.clear();
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
        try {
            return JSON.parse(localStorage.getItem('grindx_user_profile')) || {};
        } catch (e) {
            return {};
        }
    }

    loadInitialView() {
        // Tenta carregar o primeiro módulo disponível ou o dashboard
        setTimeout(() => {
            const firstLink = this.mainNav.querySelector('.nav-link');
            if (firstLink) firstLink.click();
        }, 500);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new DashboardController();
});
