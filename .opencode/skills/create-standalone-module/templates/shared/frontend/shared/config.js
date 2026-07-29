/**
 * GrindX Config — Standalone Fallback
 *
 * No monorepo, apps/frontend-webapp/shared/config.js define window.GRINDX_CONFIG
 * com API_BASE_URL. Este stub só define o fallback para standalone.
 */
window.GRINDX_CONFIG = window.GRINDX_CONFIG || {};
if (!window.GRINDX_CONFIG.API_BASE_URL) {
  if (window.__GRINDX_API_URL) {
    window.GRINDX_CONFIG.API_BASE_URL = window.__GRINDX_API_URL;
  } else {
    var p = window.location.port;
    if (p === '7080') {
      window.GRINDX_CONFIG.API_BASE_URL = 'http://localhost:7000/v1';
    } else {
      window.GRINDX_CONFIG.API_BASE_URL = window.location.protocol + '//' + window.location.hostname + ':8002/v1';
    }
  }
}