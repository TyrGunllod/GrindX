/**
 * Shared form field helpers.
 */

(function initFormField() {
    function createSelect({ id, label, options = [], value }) {
        const group = document.createElement('div');
        group.className = 'form-group';
        group.innerHTML = `
            <label for="${id}">${label}</label>
            <select id="${id}" class="form-control">
                ${options.map(option => `
                    <option value="${option.value}" ${option.value === value ? 'selected' : ''}>
                        ${option.label}
                    </option>
                `).join('')}
            </select>
        `;
        return group;
    }

    function createIconSelect({ id, label, value = 'fas fa-folder' }) {
        const iconOptions = window.grindx.constants.ICON_OPTIONS.map(icon => ({
            value: icon,
            label: icon.replace('fas fa-', '')
        }));
        const group = createSelect({ id, label, options: iconOptions, value });
        const preview = document.createElement('div');
        preview.id = `${id}Preview`;
        preview.style.marginTop = '0.5rem';
        preview.style.fontSize = '1.5rem';
        group.appendChild(preview);

        const select = group.querySelector('select');
        const updatePreview = () => {
            preview.innerHTML = `<i class="${select.value}"></i>`;
            const i = preview.querySelector('i');
            if (i) window.grindx.icons.convert(i);
            const lib = window.grindx.icons.activeLib();
            if (lib === 'lucide') {
                const w = window.parent !== window ? window.parent : window;
                if (w.lucide) w.lucide.createIcons();
                else if (window.lucide) window.lucide.createIcons();
            }
        };
        select.addEventListener('change', updatePreview);
        updatePreview();

        return group;
    }

    function appendFields(form, fields) {
        fields.forEach(field => {
            form.appendChild(window.grindx.ui.createInput(field));
        });
    }

    window.grindx = window.grindx || {};
    window.grindx.components = {
        ...(window.grindx.components || {}),
        FormField: {
            appendFields,
            createIconSelect,
            createSelect
        }
    };
})();
