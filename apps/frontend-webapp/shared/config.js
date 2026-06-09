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
  // URL base da API — incluir /v1/ para todas as chamadas
  API_BASE_URL: "http://localhost:8002/v1",
};
