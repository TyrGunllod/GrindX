/**
 * DASHBOARD CONTROLLER - SGI
 * Boas Práticas: Clean Code, SOLID, Component-Driven
 */

class DashboardController {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.mainNav = document.getElementById('mainNav');
        this.viewport = document.getElementById('moduleViewport');
        this.loader = document.getElementById('moduleLoader');
        
        this.init();
    }

    init() {
        this.checkAuth();
        this.setupEvents();
        this.loadInitialView();
    }

    checkAuth() {
        const token = localStorage.getItem('access_token');
        if (!token) {
            window.location.href = 'index.html';
            return;
        }

        const user = this.parseJwt(token);
        this.updateUserUI(user);
        
        // Controle de acesso administrativo (SOLID)
        if (user.role === 'admin') {
            document.getElementById('adminNav').style.display = 'block';
        }
    }

    setupEvents() {
        // Menu Hambúrguer (Mobile)
        document.getElementById('openSidebar')?.addEventListener('click', () => this.toggleSidebar(true));
        document.getElementById('closeSidebar')?.addEventListener('click', () => this.toggleSidebar(false));

        // Navegação
        this.mainNav.addEventListener('click', (e) => this.handleNavigation(e));

        // Logout
        document.getElementById('logoutBtn')?.addEventListener('click', () => this.logout());

        // Alternância de Tema
        document.getElementById('themeToggle')?.addEventListener('click', () => {
            window.sgi.theme.toggle();
            this.updateThemeIcon();
        });
    }

    updateThemeIcon() {
        const icon = document.querySelector('#themeToggle i');
        if (icon) {
            icon.className = window.sgi.theme.theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }

    handleNavigation(e) {
        const link = e.target.closest('.nav-link');
        if (!link) return;

        e.preventDefault();
        
        // Atualizar UI de navegação
        this.mainNav.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        link.classList.add('active');

        // Carregar Módulo
        const module = link.dataset.module;
        this.navigateToModule(module);

        // Fechar sidebar no mobile após clique
        if (window.innerWidth < 1024) this.toggleSidebar(false);
    }

    navigateToModule(name) {
        const routes = {
            'home': 'modules/home/index.html',
            'estoque': 'modules/estoque/index.html',
            'admin-users': 'modules/users/index.html'
        };

        const url = routes[name];
        if (!url) return;

        this.showLoader(true);
        
        const iframe = document.createElement('iframe');
        iframe.src = url;
        iframe.onload = () => this.showLoader(false);
        
        this.viewport.innerHTML = '';
        this.viewport.appendChild(iframe);
    }

    toggleSidebar(isOpen) {
        this.sidebar.classList.toggle('open', isOpen);
    }

    updateUserUI(user) {
        document.getElementById('userName').textContent = user.sub === '1' ? 'Admin' : 'Usuário';
        document.getElementById('userRole').textContent = user.role.toUpperCase();
        document.getElementById('userAvatar').src = `https://ui-avatars.com/api/?name=${user.role}&background=4f46e5&color=fff`;
    }

    showLoader(show) {
        this.loader.style.display = show ? 'flex' : 'none';
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
        this.navigateToModule('home');
    }
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => new DashboardController());
