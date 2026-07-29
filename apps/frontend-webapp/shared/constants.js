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
            'fas fa-network-wired', 'fas fa-filter',
            'fas fa-gear', 'fas fa-keyboard',
        ],
        devices: [
            'fas fa-mobile-alt', 'fas fa-tablet-alt', 'fas fa-laptop',
            'fas fa-desktop', 'fas fa-hdd', 'fas fa-microchip',
            'fas fa-sd-card', 'fas fa-sim-card', 'fas fa-plug',
            'fas fa-battery-full', 'fas fa-wifi', 'fas fa-ethernet',
            'fas fa-memory', 'fas fa-headphones', 'fas fa-mouse',
            'fas fa-tv', 'fas fa-power-off', 'fas fa-camera',
            'fas fa-gamepad', 'fas fa-usb',
        ],
        design: [
            'fas fa-paint-brush', 'fas fa-palette', 'fas fa-pencil-alt',
            'fas fa-pen', 'fas fa-pen-fancy', 'fas fa-highlighter',
            'fas fa-marker', 'fas fa-vector-square', 'fas fa-eye-dropper',
            'fas fa-ruler-combined', 'fas fa-layer-group', 'fas fa-eraser',
            'fas fa-th-large', 'fas fa-th-list', 'fas fa-archive',
            'fas fa-swatchbook', 'fas fa-draw-polygon',
            'fas fa-crop', 'fas fa-crop-alt', 'fas fa-fill-drip',
        ],
        files: [
            'fas fa-folder', 'fas fa-folder-open', 'fas fa-folder-plus',
            'fas fa-file', 'fas fa-file-alt', 'fas fa-file-invoice',
            'fas fa-file-code', 'fas fa-file-image', 'fas fa-file-pdf',
            'fas fa-copy', 'fas fa-paste', 'fas fa-save',
            'fas fa-download', 'fas fa-upload', 'fas fa-print',
            'fas fa-file-excel', 'fas fa-file-word',
            'fas fa-file-powerpoint', 'fas fa-file-archive',
            'fas fa-file-video',
        ],
        users: [
            'fas fa-user', 'fas fa-users', 'fas fa-user-tie',
            'fas fa-user-cog', 'fas fa-user-circle', 'fas fa-user-friends',
            'fas fa-user-plus', 'fas fa-user-check', 'fas fa-user-shield',
            'fas fa-user-graduate', 'fas fa-phone', 'fas fa-envelope',
            'fas fa-comment', 'fas fa-comment-dots', 'fas fa-bell',
            'fas fa-id-card', 'fas fa-id-badge', 'fas fa-address-card',
            'fas fa-people-arrows', 'fas fa-person',
        ],
        alert: [
            'fas fa-bell', 'fas fa-bell-slash', 'fas fa-exclamation-triangle',
            'fas fa-exclamation-circle', 'fas fa-radiation-alt',
            'fas fa-skull-crossbones', 'fas fa-biohazard',
            'fas fa-fire', 'fas fa-fire-extinguisher',
            'fas fa-virus', 'fas fa-virus-slash', 'fas fa-ban',
            'fas fa-circle-info', 'fas fa-circle-question',
            'fas fa-circle-check', 'fas fa-circle-xmark',
            'fas fa-triangle-exclamation', 'fas fa-circle-exclamation',
            'fas fa-shield-haltered', 'fas fa-scale-balanced',
        ],
        business: [
            'fas fa-briefcase', 'fas fa-building', 'fas fa-landmark',
            'fas fa-coins', 'fas fa-handshake', 'fas fa-file-invoice-dollar',
            'fas fa-receipt', 'fas fa-balance-scale', 'fas fa-sack-dollar',
            'fas fa-calculator', 'fas fa-cash-register', 'fas fa-store',
            'fas fa-shop', 'fas fa-industry', 'fas fa-city',
            'fas fa-sitemap', 'fas fa-file-contract', 'fas fa-percent',
            'fas fa-piggy-bank', 'fas fa-chart-pie',
        ],
        charts: [
            'fas fa-chart-line', 'fas fa-chart-bar', 'fas fa-chart-pie',
            'fas fa-chart-area', 'fas fa-diagram-project', 'fas fa-table',
            'fas fa-chart-column', 'fas fa-chart-gantt',
            'fas fa-square-poll-vertical', 'fas fa-square-poll-horizontal',
            'fas fa-ranking-star', 'fas fa-sliders',
            'fas fa-gauge', 'fas fa-gauge-high', 'fas fa-gauge-simple-high',
            'fas fa-timeline', 'fas fa-chart-simple',
            'fas fa-calculator', 'fas fa-percent', 'fas fa-scroll',
        ],
        communication: [
            'fas fa-comments', 'fas fa-envelope', 'fas fa-envelope-open-text',
            'fas fa-phone', 'fas fa-paper-plane', 'fas fa-inbox',
            'fas fa-address-book', 'fas fa-at', 'fas fa-voicemail',
            'fas fa-phone-volume', 'fas fa-microphone',
            'fas fa-microphone-slash', 'fas fa-video', 'fas fa-video-slash',
            'fas fa-message', 'fas fa-share-nodes',
            'fas fa-bullhorn', 'fas fa-circle-nodes',
            'fas fa-fax', 'fas fa-comment-sms',
        ],
        editing: [
            'fas fa-edit', 'fas fa-pen-to-square', 'fas fa-pencil',
            'fas fa-eraser', 'fas fa-highlighter', 'fas fa-clipboard',
            'fas fa-clipboard-list', 'fas fa-signature', 'fas fa-scissors',
            'fas fa-paste', 'fas fa-trash-can', 'fas fa-trash',
            'fas fa-rotate-left', 'fas fa-rotate-right',
            'fas fa-check', 'fas fa-xmark', 'fas fa-plus',
            'fas fa-minus', 'fas fa-bold', 'fas fa-italic',
        ],
        logistics: [
            'fas fa-truck', 'fas fa-truck-fast', 'fas fa-box',
            'fas fa-boxes-stacked', 'fas fa-warehouse', 'fas fa-pallet',
            'fas fa-barcode', 'fas fa-tasks', 'fas fa-box-open',
            'fas fa-box-archive', 'fas fa-clipboard-check',
            'fas fa-dolly', 'fas fa-cart-flatbed', 'fas fa-gears',
            'fas fa-arrows-spin', 'fas fa-weight-scale', 'fas fa-ruler',
            'fas fa-industry', 'fas fa-truck-ramp-box', 'fas fa-tag',
        ],
        maps: [
            'fas fa-map', 'fas fa-location-dot', 'fas fa-map-pin',
            'fas fa-compass', 'fas fa-globe', 'fas fa-globe-americas',
            'fas fa-road', 'fas fa-route', 'fas fa-map-marked-alt',
            'fas fa-location-arrow', 'fas fa-location-crosshairs',
            'fas fa-mountain', 'fas fa-tree', 'fas fa-flag',
            'fas fa-flag-checkered', 'fas fa-signs-post',
            'fas fa-satellite', 'fas fa-satellite-dish',
            'fas fa-building-columns', 'fas fa-monument',
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
