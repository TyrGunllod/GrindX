/**
 * Shared API service.
 */

(function initApiService() {
    const getBaseUrl = () => {
        // Tenta usar config injetada globalmente (GRINDX_CONFIG)
        if (window.GRINDX_CONFIG?.API_BASE_URL) {
            return window.GRINDX_CONFIG.API_BASE_URL;
        }
        // Também suporta window.grindx.config (config dinâmica)
        if (window.grindx?.config?.API_BASE_URL) {
            return window.grindx.config.API_BASE_URL;
        }
        
        // Fallback: detectar automaticamente baseado no host atual
        // Quando acessado via localhost, usa localhost:8002
        // Quando acessado via outro IP, usa esse IP:8002
        const hostname = window.location.hostname;
        return `http://${hostname}:8002/v1`;
    };

    function buildApiUrl(endpoint, params = {}) {
        const baseUrl = getBaseUrl();
        const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
        const url = new URL(`${baseUrl}${normalizedEndpoint}`);
        const searchParams = new URLSearchParams();

        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null && value !== '') {
                searchParams.set(key, value);
            }
        });

        url.search = searchParams.toString();
        return url.toString();
    }

    function authHeaders() {
        const token = window.grindx?.session?.getToken();
        return token ? { Authorization: `Bearer ${token}` } : {};
    }

    async function parseResponse(response) {
        // Handle 204 No Content - no body expected
        if (response.status === 204) {
            if (!response.ok) {
                throw new Error('Erro na requisição');
            }
            return null;
        }

        if (response.status === 401) {
            const url = response.url || '';
            if (!url.endsWith('/auth/token') && !url.includes('/auth/refresh')) {
                window.grindx.session.clear();
                try { window.top.location.href = 'index.html'; } catch (e) { window.location.href = 'index.html'; }
                throw new Error('Sessão expirada. Faça login novamente.');
            }
        }

        const contentType = response.headers.get('content-type') || '';
        const hasJson = contentType.includes('application/json');
        const payload = hasJson ? await response.json() : await response.text();

        if (!response.ok) {
            const message = payload?.message || payload?.detail || payload || 'Erro na requisição';
            throw new Error(message);
        }

        return payload || null;
    }

    async function request(endpoint, options = {}) {
        const {
            method = 'GET',
            params = {},
            data,
            auth = true,
            headers = {}
        } = options;
        const requestHeaders = {
            ...(auth ? authHeaders() : {}),
            ...headers
        };
        const fetchOptions = { method, headers: requestHeaders };

        if (data !== undefined) {
            requestHeaders['Content-Type'] = requestHeaders['Content-Type'] || 'application/json';
            fetchOptions.body = JSON.stringify(data);
        }

        const response = await fetch(buildApiUrl(endpoint, params), fetchOptions);
        return parseResponse(response);
    }

    const ApiService = {
        buildApiUrl,
        request,
        get: (endpoint, params = {}, options = {}) => request(endpoint, { ...options, method: 'GET', params }),
        post: (endpoint, data, options = {}) => request(endpoint, { ...options, method: 'POST', data }),
        put: (endpoint, data, options = {}) => request(endpoint, { ...options, method: 'PUT', data }),
        delete: (endpoint, options = {}) => request(endpoint, { ...options, method: 'DELETE' })
    };

    window.grindx = window.grindx || {};
    window.grindx.api = ApiService;
    window.grindx.ApiService = ApiService;
})();
