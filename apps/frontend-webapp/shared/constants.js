/**
 * Shared domain constants.
 */

(function initSharedConstants() {
    const ICON_CATEGORIES = {
        coding: [
            'fas fa-code', 'fas fa-terminal', 'fas fa-bug', 'fas fa-cog',
            'fas fa-wrench', 'fas fa-tools', 'fas fa-laptop-code',
            'fas fa-code-branch', 'fas fa-tag', 'fas fa-tags',
            'fas fa-key', 'fas fa-lock', 'fas fa-shield-alt',
            'fas fa-database', 'fas fa-cloud', 'fas fa-server',
        ],
        devices: [
            'fas fa-mobile-alt', 'fas fa-tablet-alt', 'fas fa-laptop',
            'fas fa-desktop', 'fas fa-hdd', 'fas fa-microchip',
            'fas fa-sd-card', 'fas fa-sim-card', 'fas fa-plug',
            'fas fa-battery-full', 'fas fa-wifi',
        ],
        design: [
            'fas fa-paint-brush', 'fas fa-palette', 'fas fa-pencil-alt',
            'fas fa-pen', 'fas fa-pen-fancy', 'fas fa-highlighter',
            'fas fa-marker', 'fas fa-vector-square', 'fas fa-eye-dropper',
            'fas fa-ruler-combined', 'fas fa-layer-group', 'fas fa-eraser',
            'fas fa-th-large', 'fas fa-th-list', 'fas fa-archive',
        ],
        files: [
            'fas fa-folder', 'fas fa-folder-open', 'fas fa-folder-plus',
            'fas fa-file', 'fas fa-file-alt', 'fas fa-file-invoice',
            'fas fa-file-code', 'fas fa-file-image', 'fas fa-file-pdf',
            'fas fa-copy', 'fas fa-paste', 'fas fa-save',
            'fas fa-download', 'fas fa-upload', 'fas fa-print',
        ],
        users: [
            'fas fa-user', 'fas fa-users', 'fas fa-user-tie',
            'fas fa-user-cog', 'fas fa-user-circle', 'fas fa-user-friends',
            'fas fa-user-plus', 'fas fa-user-check', 'fas fa-user-shield',
            'fas fa-user-graduate', 'fas fa-phone', 'fas fa-envelope',
            'fas fa-comment', 'fas fa-comment-dots', 'fas fa-bell',
        ],
    };

    const ICON_OPTIONS = Object.values(ICON_CATEGORIES).flat();

    const USER_ROLES = [
        { value: 'leitura', label: 'Leitura' },
        { value: 'operador', label: 'Operador' },
        { value: 'admin', label: 'Administrador' }
    ];

    const PROTECTED_ABA_NAMES = ['principal', 'gestão', 'gestao', 'menu'];

    const PROTECTED_MODULE_NAMES = [
        'usuários', 'usuarios',
        'módulos & abas', 'modulos & abas',
        'módulos e abas', 'modulos e abas',
        'módulos', 'modulos',
        'estrutura do portal',
        'dashboard', 'painel de controle',
        'início', 'inicio'
    ];

    window.grindx = window.grindx || {};
    window.grindx.constants = {
        ICON_OPTIONS,
        ICON_CATEGORIES,
        USER_ROLES,
        PROTECTED_ABA_NAMES,
        PROTECTED_MODULE_NAMES
    };
})();
