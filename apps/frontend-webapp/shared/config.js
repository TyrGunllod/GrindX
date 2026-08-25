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

// Em produção (onrender.com), usa a API pública — funciona em qualquer
// contexto (dashboard e módulos em iframe, que não herdam __GRINDX_API_URL).
const PROD_API_URL = (location.hostname.indexOf('onrender.com') !== -1)
    ? 'https://api-postgres-jc35.onrender.com/v1'
    : null;

window.GRINDX_CONFIG = {
  // URL base da API — usa variavel injetada (window.__GRINDX_API_URL)
  // Em localhost/127.0.0.1/IP local usa direto a porta 8002
  API_BASE_URL: window.__GRINDX_API_URL || PROD_API_URL || `${window.location.protocol}//${window.location.hostname}:8002/v1`,
};
