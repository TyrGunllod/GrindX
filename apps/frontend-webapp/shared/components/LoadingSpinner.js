/**
 * Shared loading, empty state and toast helpers.
 */

(function initFeedbackComponents() {
    const DEFAULT_MESSAGES = {
        network: 'Verifique sua conexão e tente novamente.',
        auth: 'Sua sessão expirou. Faça login novamente.',
        forbidden: 'Você não tem permissão para realizar esta ação.',
        notFound: 'Não encontramos as informações solicitadas.',
        validation: 'Revise os campos destacados e tente novamente.',
        generic: 'Não foi possível concluir a ação. Tente novamente.'
    };

    function createLoading(message = 'Carregando...') {
        const wrapper = document.createElement('div');
        wrapper.className = 'state-panel loading-panel';
        wrapper.setAttribute('role', 'status');
        wrapper.setAttribute('aria-live', 'polite');
        wrapper.innerHTML = `
            <div class="spinner" aria-hidden="true"></div>
            <strong>${message}</strong>
        `;
        return wrapper;
    }

    function createEmpty({ icon = 'fas fa-inbox', title, action } = {}) {
        const wrapper = document.createElement('div');
        wrapper.className = 'state-panel empty-panel';
        wrapper.innerHTML = `
            <i class="${icon}" aria-hidden="true"></i>
            <strong>${title}</strong>
        `;
        if (action) wrapper.appendChild(action);
        return wrapper;
    }

    function toUserMessage(error) {
        const message = String(error?.message || error || '').toLowerCase();

        if (message.includes('failed to fetch') || message.includes('network')) return DEFAULT_MESSAGES.network;
        if (message.includes('401') || message.includes('unauthorized') || message.includes('token')) return DEFAULT_MESSAGES.auth;
        if (message.includes('403') || message.includes('forbidden')) return DEFAULT_MESSAGES.forbidden;
        if (message.includes('404') || message.includes('not found')) return DEFAULT_MESSAGES.notFound;
        if (message.includes('validation') || message.includes('invalid')) return DEFAULT_MESSAGES.validation;

        return error?.message || DEFAULT_MESSAGES.generic;
    }

    function toast(message, type = 'info') {
        const existing = document.querySelector('.toast-region');
        const region = existing || document.createElement('div');
        region.className = 'toast-region';
        region.setAttribute('aria-live', 'polite');
        region.setAttribute('aria-atomic', 'true');
        if (!existing) document.body.appendChild(region);

        const item = document.createElement('div');
        item.className = `toast toast-${type}`;
        item.textContent = message;
        region.appendChild(item);

        setTimeout(() => item.remove(), 4000);
    }

    function setContainerState(container, stateElement) {
        container.innerHTML = '';
        container.appendChild(stateElement);
    }

    window.grindx = window.grindx || {};
    window.grindx.components = {
        ...(window.grindx.components || {}),
        LoadingSpinner: {
            create: createLoading,
            createEmpty,
            setContainerState,
            toUserMessage,
            toast
        }
    };
})();
