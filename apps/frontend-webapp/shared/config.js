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
  // Em localhost/127.0.0.1 usa direto porta 8002; em IP externo usa /v1 (same-origin via nginx proxy)
  API_BASE_URL: window.__GRINDX_API_URL || (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? `http://${window.location.hostname}:8002/v1`
    : `/v1`),
};
