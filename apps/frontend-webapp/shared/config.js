/**
 * Configuracao injetada no deploy.
 *
 * Substitua API_BASE_URL pelo IP/host da maquina que roda as APIs.
 *
 * Uso:
 *   1. Editar este arquivo com o IP correto
 *   2. Incluir no HTML antes do apiService.js:
 *      <script src="shared/config.js"></script>
 *      <script src="shared/apiService.js"></script>
 */

window.GRINDX_CONFIG = {
  // URL base da API — usa variavel injetada (window.__GRINDX_API_URL)
  // Em dev (localhost:8101) usa porta 8002; em producao (nginx) usa /v1 (same-origin)
  API_BASE_URL: window.__GRINDX_API_URL || (window.location.port === '8101' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? `http://${window.location.hostname}:8002/v1`
    : `/v1`),
};
