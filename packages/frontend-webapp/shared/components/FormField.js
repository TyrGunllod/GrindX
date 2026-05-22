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

        function iconLib() {
            try {
                const w = window.parent !== window ? window.parent : window;
                return w.skinLoader?.currentSkin?.icon_library;
            } catch { return 'fontawesome'; }
        }

        const select = group.querySelector('select');
        const updatePreview = () => {
            const lib = iconLib() || 'fontawesome';
            const faName = select.value;
            if (lib === 'fontawesome') {
                preview.innerHTML = `<i class="${faName}"></i>`;
            } else if (lib === 'lucide') {
                const name = faName.replace('fas fa-', '');
                preview.innerHTML = `<i data-lucide="${name}"></i>`;
                if (window.lucide) window.lucide.createIcons();
                else {
                    const w = window.parent !== window ? window.parent : window;
                    if (w.lucide) w.lucide.createIcons();
                }
            } else if (lib === 'material') {
                const name = faName.replace('fas fa-', '').replace(/-/g, '_');
                preview.innerHTML = `<span class="material-icons">${name}</span>`;
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
