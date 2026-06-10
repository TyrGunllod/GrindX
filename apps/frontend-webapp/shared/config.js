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
  // ou detecta automaticamente o host atual (funciona com IP da rede)
  API_BASE_URL: window.__GRINDX_API_URL || `http://${window.location.hostname}:8002/v1`,
};
