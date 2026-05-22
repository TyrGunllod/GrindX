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
        const group = document.createElement('div');
        group.className = 'form-group';
        group.innerHTML = `<label>${label}</label>`;

        const hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.id = id;
        hidden.value = value;
        group.appendChild(hidden);

        const preview = document.createElement('div');
        preview.style.marginTop = '0.5rem';
        preview.style.fontSize = '1.5rem';
        preview.innerHTML = `<i class="${value}"></i>`;
        group.appendChild(preview);

        const grid = document.createElement('div');
        grid.className = 'icon-picker-grid';
        grid.style.cssText = 'display: grid; grid-template-columns: repeat(auto-fill, minmax(48px, 1fr)); gap: 6px; margin-top: 0.5rem; max-height: 260px; overflow-y: auto; padding: 4px;';

        window.grindx.constants.ICON_OPTIONS.forEach(iconClass => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.title = iconClass.replace('fas fa-', '');
            btn.dataset.value = iconClass;
            btn.style.cssText = 'display: flex; align-items: center; justify-content: center; width: 48px; height: 48px; border: 2px solid transparent; border-radius: 8px; cursor: pointer; background: var(--bg-card, #fff); font-size: 1.2rem; transition: border-color .2s, background .2s;';
            btn.innerHTML = `<i class="${iconClass}"></i>`;

            if (iconClass === value) {
                btn.style.borderColor = 'var(--primary, #00c2e0)';
                btn.style.background = 'var(--primary, #00c2e0)20';
                btn.classList.add('selected');
            }

            btn.addEventListener('mouseenter', () => {
                if (!btn.classList.contains('selected')) {
                    btn.style.borderColor = 'var(--border-color, #e2e8f0)';
                    btn.style.background = 'var(--bg-card-hover, #f1f5f9)';
                }
            });
            btn.addEventListener('mouseleave', () => {
                if (!btn.classList.contains('selected')) {
                    btn.style.borderColor = 'transparent';
                    btn.style.background = 'var(--bg-card, #fff)';
                }
            });
            btn.addEventListener('click', () => {
                grid.querySelectorAll('.icon-picker-item').forEach(b => {
                    b.classList.remove('selected');
                    b.style.borderColor = 'transparent';
                    b.style.background = 'var(--bg-card, #fff)';
                });
                btn.classList.add('selected');
                btn.style.borderColor = 'var(--primary, #00c2e0)';
                btn.style.background = 'var(--primary, #00c2e0)20';
                hidden.value = iconClass;
                hidden.dispatchEvent(new Event('change', { bubbles: true }));
            });

            grid.appendChild(btn);
        });

        group.appendChild(grid);

        hidden.addEventListener('change', () => {
            grid.querySelectorAll('.icon-picker-item').forEach(b => {
                const match = b.dataset.value === hidden.value;
                b.classList.toggle('selected', match);
                b.style.borderColor = match ? 'var(--primary, #00c2e0)' : 'transparent';
                b.style.background = match ? 'var(--primary, #00c2e0)20' : 'var(--bg-card, #fff)';
            });
            preview.innerHTML = `<i class="${hidden.value}"></i>`;
            const el = preview.querySelector('i');
            if (el) window.grindx.icons.convert(el);
            const lib = window.grindx.icons.activeLib();
            if (lib === 'lucide' && window.lucide) window.lucide.createIcons();
        });

        // Initial preview conversion
        (function initPreview() {
            const el = preview.querySelector('i');
            if (el) window.grindx.icons.convert(el);
            const lib = window.grindx.icons.activeLib();
            if (lib === 'lucide') {
                if (window.lucide) window.lucide.createIcons();
                else {
                    const s = document.createElement('script');
                    s.src = 'https://unpkg.com/lucide@latest/dist/umd/lucide.min.js';
                    s.onload = () => { if (window.lucide) window.lucide.createIcons(); };
                    document.head.appendChild(s);
                }
            }
        })();

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
