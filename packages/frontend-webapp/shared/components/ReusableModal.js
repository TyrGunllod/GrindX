/**
 * Shared modal helper.
 */

(function initReusableModal() {
    class ReusableModal {
        constructor(modalElement, options = {}) {
            this.element = modalElement;
            this.options = options;
            this.previousFocus = null;
            this.handleKeydown = this.handleKeydown.bind(this);
        }

        open() {
            this.previousFocus = document.activeElement;
            this.element.style.display = 'flex';
            this.element.setAttribute('aria-modal', 'true');
            document.addEventListener('keydown', this.handleKeydown);
            this.focusFirstElement();
        }

        close() {
            if (this.element.style.display === 'none') return;
            this.element.style.display = 'none';
            document.removeEventListener('keydown', this.handleKeydown);
            if (this.previousFocus && typeof this.previousFocus.focus === 'function') {
                this.previousFocus.focus();
            }
            if (this.options.onClose) this.options.onClose();
        }

        getFocusableElements() {
            return Array.from(this.element.querySelectorAll(
                'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
            )).filter(element => element.offsetParent !== null);
        }

        focusFirstElement() {
            const initialFocus = this.options.initialFocusSelector
                ? this.element.querySelector(this.options.initialFocusSelector)
                : null;
            const focusTarget = initialFocus || this.getFocusableElements()[0];
            if (focusTarget) focusTarget.focus();
        }

        handleKeydown(event) {
            if (event.key === 'Escape') {
                this.close();
                return;
            }

            if (event.key !== 'Tab') return;

            const focusableElements = this.getFocusableElements();
            if (!focusableElements.length) return;

            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];

            if (event.shiftKey && document.activeElement === firstElement) {
                event.preventDefault();
                lastElement.focus();
            } else if (!event.shiftKey && document.activeElement === lastElement) {
                event.preventDefault();
                firstElement.focus();
            }
        }
    }

    window.grindx = window.grindx || {};
    window.grindx.components = {
        ...(window.grindx.components || {}),
        ReusableModal
    };
})();
