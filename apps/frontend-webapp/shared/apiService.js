/**
 * Shared API service.
 */

(function initApiService() {
    const resolveUrl = (url) => {
        return url.startsWith('/') ? window.location.origin + url : url;
    };

    const getBaseUrl = () => {
        if (window.GRINDX_CONFIG?.API_BASE_URL) {
            return resolveUrl(window.GRINDX_CONFIG.API_BASE_URL);
        }
        if (window.grindx?.config?.API_BASE_URL) {
            return resolveUrl(window.grindx.config.API_BASE_URL);
        }
        const hostname = window.location.hostname;
        const isLocal = hostname === 'localhost' || hostname === '127.0.0.1';
        return isLocal ? `http://${hostname}:8002/v1` : `/v1`;
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
                try {
                    const doc = window.top.document;
                    const toast = doc.createElement('div');
                    toast.className = 'toast toast-error';
                    toast.textContent = 'Sessão expirada. Você será redirecionado.';
                    toast.style.cssText = 'position:fixed;top:20px;right:20px;z-index:99999;padding:16px 24px;border-radius:8px;background:var(--skin-danger,#dc2626);color:#fff;font-weight:600;box-shadow:0 8px 24px rgba(0,0,0,0.2);animation:fadeIn 0.3s';
                    doc.body.appendChild(toast);
                    setTimeout(() => { window.top.location.href = 'index.html'; }, 2000);
                } catch (e) {
                    window.location.href = 'index.html';
                }
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
        patch: (endpoint, data, options = {}) => request(endpoint, { ...options, method: 'PATCH', data }),
        delete: (endpoint, options = {}) => request(endpoint, { ...options, method: 'DELETE' })
    };

    window.grindx = window.grindx || {};
    window.grindx.api = ApiService;
    window.grindx.ApiService = ApiService;
})();
