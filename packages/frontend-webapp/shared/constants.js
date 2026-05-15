/**
 * Shared domain constants.
 */

(function initSharedConstants() {
    const ICON_OPTIONS = [
        'fas fa-folder', 'fas fa-folder-open', 'fas fa-th-large', 'fas fa-th-list',
        'fas fa-cog', 'fas fa-wrench', 'fas fa-tools',
        'fas fa-users', 'fas fa-user', 'fas fa-user-tie',
        'fas fa-box', 'fas fa-boxes', 'fas fa-cube', 'fas fa-cubes',
        'fas fa-truck', 'fas fa-shipping-fast', 'fas fa-warehouse',
        'fas fa-chart-bar', 'fas fa-chart-line', 'fas fa-chart-pie',
        'fas fa-file', 'fas fa-file-invoice', 'fas fa-file-alt',
        'fas fa-shopping-cart', 'fas fa-credit-card', 'fas fa-cash-register',
        'fas fa-building', 'fas fa-store', 'fas fa-industry',
        'fas fa-calendar', 'fas fa-clock', 'fas fa-bell',
        'fas fa-home', 'fas fa-globe', 'fas fa-map-marker-alt',
        'fas fa-print', 'fas fa-download', 'fas fa-upload',
        'fas fa-envelope', 'fas fa-comment', 'fas fa-phone',
        'fas fa-lock', 'fas fa-shield-alt', 'fas fa-key',
        'fas fa-database', 'fas fa-server', 'fas fa-cloud'
    ];

    const USER_ROLES = [
        { value: 'leitura', label: 'Leitura' },
        { value: 'operador', label: 'Operador' },
        { value: 'admin', label: 'Administrador' }
    ];

    const PROTECTED_ABA_NAMES = ['principal', 'gestão', 'gestao'];

    const PROTECTED_MODULE_NAMES = [
        'usuários', 'usuarios', 'módulos', 'modulos', 'módulo', 'modulo',
        'dashboard', 'painel de controle', 'início', 'inicio'
    ];

    window.grindx = window.grindx || {};
    window.grindx.constants = {
        ICON_OPTIONS,
        USER_ROLES,
        PROTECTED_ABA_NAMES,
        PROTECTED_MODULE_NAMES
    };
})();
