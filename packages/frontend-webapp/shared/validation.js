/**
 * Shared client-side validation helpers.
 */

(function initValidationHelpers() {
    function getField(id) {
        return document.getElementById(id);
    }

    function clearFieldError(field) {
        if (!field) return;
        field.classList.remove('is-invalid');
        field.removeAttribute('aria-invalid');
        const error = document.getElementById(`${field.id}Error`);
        if (error) error.remove();
    }

    function setFieldError(field, message) {
        if (!field) return;
        clearFieldError(field);
        field.classList.add('is-invalid');
        field.setAttribute('aria-invalid', 'true');

        const error = document.createElement('div');
        error.id = `${field.id}Error`;
        error.className = 'field-error';
        error.textContent = message;
        field.setAttribute('aria-describedby', error.id);
        field.insertAdjacentElement('afterend', error);
    }

    function validateRules(rules) {
        const errors = [];

        rules.forEach(rule => {
            const field = getField(rule.id);
            const value = field?.value?.trim() || '';
            clearFieldError(field);

            if (rule.required && !value) {
                errors.push({ field, message: rule.message || 'Campo obrigatório.' });
                return;
            }

            if (value && rule.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                errors.push({ field, message: 'Informe um e-mail válido.' });
                return;
            }

            if (value && rule.minLength && value.length < rule.minLength) {
                errors.push({ field, message: `Use pelo menos ${rule.minLength} caracteres.` });
                return;
            }

            if (value && rule.number && Number.isNaN(Number(value))) {
                errors.push({ field, message: 'Informe um número válido.' });
                return;
            }

            if (value && rule.urlPath && !/^[\w\-./?#=&%]+$/.test(value)) {
                errors.push({ field, message: 'Use uma URL ou caminho válido.' });
            }
        });

        errors.forEach(error => setFieldError(error.field, error.message));
        if (errors[0]?.field) errors[0].field.focus();

        return {
            valid: errors.length === 0,
            errors
        };
    }

    function clearForm(form) {
        form.querySelectorAll('.is-invalid').forEach(clearFieldError);
        form.querySelectorAll('.field-error').forEach(error => error.remove());
    }

    window.grindx = window.grindx || {};
    window.grindx.validation = {
        clearForm,
        validateRules
    };
})();
