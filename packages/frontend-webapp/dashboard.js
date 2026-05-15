/**
 * DASHBOARD CONTROLLER - SGI (Versão Dinâmica)
 * Gerencia a navegação baseada na estrutura vinda da API.
 */

const API_BASE_URL = window.sgi.config.API_BASE_URL;

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
        await this.loadDynamicMenu();
        this.loadInitialView();
    }

    checkAuth() {
        if (!this.token) {
            window.location.href = 'index.html';
            return;
        }

        const user = this.parseJwt(this.token);
        this.user = user;
        this.updateUserUI(user);
    }

    setupEvents() {
        document.getElementById('openSidebar')?.addEventListener('click', () => this.toggleSidebar(true));
        document.getElementById('closeSidebar')?.addEventListener('click', () => this.toggleSidebar(false));
        this.mainNav.addEventListener('click', (e) => this.handleNavigation(e));
        document.getElementById('logoutBtn')?.addEventListener('click', () => this.logout());
        
        document.getElementById('themeToggle')?.addEventListener('click', () => {
            window.sgi.theme.toggle();
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
            const response = await fetch(`${API_BASE_URL}/portal/menu`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });

            if (!response.ok) throw new Error('Erro ao carregar menu');

            const menuData = await response.json();
            this.renderSidebar(menuData);
        } catch (err) {
            console.error('Falha ao carregar menu dinâmico:', err);
        }
    }

    renderSidebar(abas) {
        this.mainNav.innerHTML = abas.map(aba => `
            <div class="nav-group" id="group-${aba.id}">
                <div class="nav-title" onclick="window.dashboard.toggleGroup('${aba.id}')">
                    <span>${aba.nome}</span>
                    <i class="fas fa-chevron-down chevron"></i>
                </div>
                <div class="nav-links-container">
                    ${aba.modulos.map(mod => {
                        if (mod.role_minima === 'admin' && this.user.role !== 'admin') return '';
                        return `
                            <a href="#" class="nav-link" data-module="${mod.slug}" data-url="${mod.url}" role="button">
                                <i class="${mod.icone || 'fas fa-cube'}"></i> <span>${mod.nome}</span>
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
            const theme = window.sgi.theme.theme;
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
        document.getElementById('userName').textContent = user.sub === '1' ? 'Administrador' : 'Usuário';
        document.getElementById('userRole').textContent = user.role.toUpperCase();
        document.getElementById('userAvatar').src = `https://ui-avatars.com/api/?name=${user.role}&background=4f46e5&color=fff`;
    }

    updateThemeIcon() {
        const icon = document.querySelector('#themeToggle i');
        if (icon) icon.className = window.sgi.theme.theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
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
            return JSON.parse(atob(token.split('.')[1]));
        } catch (e) {
            return null;
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
