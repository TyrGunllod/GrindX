/**
 * GrindX Config — Standalone Fallback
 *
 * No monorepo, apps/frontend-webapp/shared/config.js define window.GRINDX_CONFIG.
 * Este stub define o padrão para uso standalone.
 */

window.GRINDX_CONFIG = window.GRINDX_CONFIG || {
    API_BASE_URL: window.__GRINDX_API_URL || (window.location.protocol + '//' + window.location.hostname + ':8002/v1'),
};
