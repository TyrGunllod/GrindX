/**
 * ADMIN SKINS MODULE - GrindX v2
 * Gestão de skins/temas com modo avançado, templates, e preview expandido.
 */

class AdminSkinsController extends window.grindx.controllers.BaseController {
    constructor() {
        super();
        this.skins = [];
        this.templates = [];
        this.editingSkinId = null;
        this.currentLogoUrl = null;
        this.pendingLogoFile = null;
        this.advancedMode = false;
        this._darkPreview = false;
        this.apiBase = window.grindx.config.API_BASE_URL;

        this.init();
    }

    async init() {
        this.setupEvents();
        await this.loadSkins();
        await this.loadTemplates();
    }

    setupEvents() {
        // Modals
        document.getElementById('btnCloseModal')?.addEventListener('click', () => this.closeModal());
        document.getElementById('btnCloseTemplateModal')?.addEventListener('click', () => this.closeTemplatePicker());
        document.getElementById('btnCancelTemplate')?.addEventListener('click', () => this.closeTemplatePicker());

        // Save/Reset/Preview
        document.getElementById('btnSaveSkin')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.saveSkin();
        });
        document.getElementById('btnPreviewSkin')?.addEventListener('click', () => this.previewSkin());
        document.getElementById('btnResetSkin')?.addEventListener('click', () => this.resetPreview());
        document.getElementById('btnAutoDarkMode')?.addEventListener('click', () => this.generateDarkMode());

        // Preview dark/light toggle
        document.getElementById('previewThemeToggle')?.addEventListener('click', () => this.togglePreviewTheme());

        // Advanced mode toggle
        document.getElementById('advancedModeToggle')?.addEventListener('change', (e) => {
            this.advancedMode = e.target.checked;
            this.toggleAdvancedMode();
        });

        // Color pickers + text inputs sync
        this.setupColorSync('colorPrimary', 'colorPrimaryText');
        this.setupColorSync('colorDanger', 'colorDangerText');
        this.setupColorSync('colorSuccess', 'colorSuccessText');
        this.setupColorSync('colorWarning', 'colorWarningText');
        this.setupColorSync('colorBgMain', 'colorBgMainText');
        this.setupColorSync('colorBgCard', 'colorBgCardText');
        this.setupColorSync('colorPrimaryHover', 'colorPrimaryHoverText');
        this.setupColorSync('colorTextMain', 'colorTextMainText');
        this.setupColorSync('colorTextMuted', 'colorTextMutedText');
        this.setupColorSync('colorBorderColor', 'colorBorderColorText');
        this.setupColorSync('colorFocusRing', 'colorFocusRingText');
        this.setupColorSync('colorBgMainDark', 'colorBgMainDarkText');
        this.setupColorSync('colorBgCardDark', 'colorBgCardDarkText');
        this.setupColorSync('colorTextMainDark', 'colorTextMainDarkText');
        this.setupColorSync('colorTextMutedDark', 'colorTextMutedDarkText');
        this.setupColorSync('colorBorderColorDark', 'colorBorderColorDarkText');

        // Font select live update
        ['fontHeading', 'fontBody'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('change', () => this.previewSkin());
            }
        });

        // Auto-generate copyright from company name
        const companyNameInput = document.getElementById('companyName');
        const copyrightInput = document.getElementById('copyrightText');
        if (companyNameInput && copyrightInput) {
            companyNameInput.addEventListener('input', (e) => {
                const name = e.target.value.trim();
                if (name) {
                    const year = new Date().getFullYear();
                    copyrightInput.value = `© ${year} ${name}. Todos os direitos reservados.`;
                } else {
                    copyrightInput.value = '';
                }
            });
        }

        // Icon library radio change triggers preview
        document.querySelectorAll('input[name="iconLibrary"]').forEach(radio => {
            radio.addEventListener('change', () => this.previewSkin());
        });

        // Logo upload
        const logoFile = document.getElementById('logoFile');
        const uploadArea = document.querySelector('.upload-area');
        if (logoFile && uploadArea) {
            uploadArea.addEventListener('click', () => logoFile.click());
            logoFile.addEventListener('change', (e) => this.handleLogoUpload(e));
        }

        // Close modals on overlay click
        document.getElementById('skinModal')?.addEventListener('click', (e) => {
            if (e.target === e.currentTarget) this.closeModal();
        });
        document.getElementById('templateModal')?.addEventListener('click', (e) => {
            if (e.target === e.currentTarget) this.closeTemplatePicker();
        });
    }

    setupColorSync(colorId, textId) {
        const colorPicker = document.getElementById(colorId);
        const textInput = document.getElementById(textId);

        if (colorPicker && textInput) {
            colorPicker.addEventListener('input', (e) => {
                textInput.value = e.target.value;
                this.previewSkin();
            });

            textInput.addEventListener('input', (e) => {
                const value = e.target.value;
                if (this.isValidHex(value)) {
                    colorPicker.value = value;
                    colorPicker.disabled = false;
                } else {
                    colorPicker.disabled = true;
                }
                this.previewSkin();
            });
        }
    }

    isValidHex(hex) {
        return /^#([0-9A-F]{3}){1,2}$/i.test(hex);
    }

    async loadSkins() {
        try {
            const resp = await fetch(`${this.apiBase}/themes`, {
                headers: { Authorization: `Bearer ${this.token}` },
            });
            if (!resp.ok) throw new Error('Failed to load skins');
            this.skins = await resp.json();
        } catch (e) {
            console.error('Erro ao carregar skins:', e);
        }
        this.renderSkins();
    }

    async loadTemplates() {
        try {
            const resp = await fetch(`${this.apiBase}/themes/templates`, {
                headers: { Authorization: `Bearer ${this.token}` },
            });
            if (!resp.ok) throw new Error('Failed to load templates');
            this.templates = await resp.json();
            this.renderTemplates();
        } catch (e) {
            console.error('Erro ao carregar templates:', e);
        }
    }

    renderSkins() {
        const grid = document.getElementById('skinsGrid');
        if (!grid) return;

        const cards = this.skins.map(skin => {
            const colors = skin.colors || {};
            const primary = colors['--skin-primary'] || '#00c2e0';
            const danger = colors['--skin-danger'] || '#ef4444';
            const success = colors['--skin-success'] || '#10b981';
            const bgMain = colors['--skin-bg-main'] || '#f8fafc';

            return `
                <div class="skin-card" data-id="${skin.id}">
                    <div class="skin-card-header">
                        <span class="skin-card-name">${skin.name}</span>
                        ${skin.is_active ? '<span class="skin-card-badge">Ativa</span>' : ''}
                    </div>
                    <div class="skin-card-preview">
                        <span style="background: ${primary}"></span>
                        <span style="background: ${danger}"></span>
                        <span style="background: ${success}"></span>
                        <span style="background: ${bgMain}; border: 1px solid #e2e8f0"></span>
                    </div>
                    <div class="skin-card-actions">
                        ${skin.is_active
                            ? '<button class="btn" disabled>Ativa</button>'
                            : `<button class="btn btn-primary" onclick="window.adminSkins.activateSkin(${skin.id})">Ativar</button>`
                        }
                        <button class="btn" onclick="window.adminSkins.editSkin(${skin.id})">Editar</button>
                        <button class="btn btn-test" onclick="window.adminSkins.testSkin(${skin.id})" title="Testar">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn" style="background: var(--skin-danger); color: white;" onclick="window.adminSkins.deleteSkin(${skin.id})">Excluir</button>
                    </div>
                </div>
            `;
        }).join('');

        grid.innerHTML = cards + `
            <div class="skin-card" style="display: flex; align-items: center; justify-content: center; cursor: pointer; border-style: dashed;" onclick="window.adminSkins.openNewSkinModal()">
                <div style="text-align: center; color: var(--skin-text-muted);">
                    <i class="fas fa-plus" style="font-size: 2rem; margin-bottom: 0.5rem;"></i>
                    <div>Criar Nova Skin</div>
                </div>
            </div>
            <div class="skin-card" style="display: flex; align-items: center; justify-content: center; cursor: pointer; border-style: dashed;" onclick="window.adminSkins.openTemplatePicker()">
                <div style="text-align: center; color: var(--skin-text-muted);">
                    <i class="fas fa-th-large" style="font-size: 2rem; margin-bottom: 0.5rem;"></i>
                    <div>Usar Template</div>
                </div>
            </div>
        `;
    }

    renderTemplates() {
        const grid = document.getElementById('templateGrid');
        if (!grid) return;

        const cards = this.templates.map(template => {
            const preview = template.preview || {};
            const primary = preview['--skin-primary'] || '#00c2e0';
            const bg = preview['--skin-bg-main'] || '#f8fafc';
            const text = preview['--skin-text-main'] || '#1e293b';
            const danger = preview['--skin-danger'] || '#ef4444';

            return `
                <div class="template-card" data-slug="${template.slug}" onclick="window.adminSkins.selectTemplate('${template.slug}')">
                    <div class="template-card-name">${template.name}</div>
                    <div class="template-card-preview">
                        <span style="background: ${primary}"></span>
                        <span style="background: ${bg}"></span>
                        <span style="background: ${text}"></span>
                        <span style="background: ${danger}"></span>
                    </div>
                </div>
            `;
        }).join('');

        grid.innerHTML = cards;
    }

    openNewSkinModal() {
        this.editingSkinId = null;
        document.getElementById('modalTitle').textContent = 'Nova Skin';
        this.resetForm();
        this.openModal();
    }

    async editSkin(id) {
        const skin = this.skins.find(s => s.id === id);
        if (!skin) return;

        this.editingSkinId = id;
        this.currentLogoUrl = skin.logo_url || null;
        this.pendingLogoFile = null;
        document.getElementById('modalTitle').textContent = `Editar: ${skin.name}`;

        document.getElementById('skinName').value = skin.name || '';
        document.getElementById('companyName').value = skin.company_name || '';
        document.getElementById('copyrightText').value = skin.copyright_text || '';

        const logoPreview = document.getElementById('logoPreview');
        if (logoPreview) {
            if (skin.logo_url) {
                this._setPreviewImage(logoPreview, skin.logo_url);
            } else {
                this._resetPreviewDefault(logoPreview);
            }
        }

        const colors = skin.colors || {};
        this.setColor('colorPrimary', 'colorPrimaryText', colors['--skin-primary'] || '#00c2e0');
        this.setColor('colorDanger', 'colorDangerText', colors['--skin-danger'] || '#ef4444');
        this.setColor('colorSuccess', 'colorSuccessText', colors['--skin-success'] || '#10b981');
        this.setColor('colorWarning', 'colorWarningText', colors['--skin-warning'] || '#f59e0b');
        this.setColor('colorBgMain', 'colorBgMainText', colors['--skin-bg-main'] || '#f8fafc');
        this.setColor('colorBgCard', 'colorBgCardText', colors['--skin-bg-card'] || '#ffffff');
        this.setColor('colorPrimaryHover', 'colorPrimaryHoverText', colors['--skin-primary-hover'] || '#00a8c4');
        this.setColor('colorTextMain', 'colorTextMainText', colors['--skin-text-main'] || '#1e293b');
        this.setColor('colorTextMuted', 'colorTextMutedText', colors['--skin-text-muted'] || '#64748b');
        this.setColor('colorBorderColor', 'colorBorderColorText', colors['--skin-border-color'] || '#e2e8f0');
        this.setColor('colorFocusRing', 'colorFocusRingText', colors['--skin-focus-ring'] || 'rgba(0, 194, 224, 0.35)');
        this.setColor('colorBgMainDark', 'colorBgMainDarkText', colors['--skin-bg-main-dark'] || '#0f172a');
        this.setColor('colorBgCardDark', 'colorBgCardDarkText', colors['--skin-bg-card-dark'] || '#1e293b');
        this.setColor('colorTextMainDark', 'colorTextMainDarkText', colors['--skin-text-main-dark'] || '#f8fafc');
        this.setColor('colorTextMutedDark', 'colorTextMutedDarkText', colors['--skin-text-muted-dark'] || '#94a3b8');
        this.setColor('colorBorderColorDark', 'colorBorderColorDarkText', colors['--skin-border-color-dark'] || 'rgba(255, 255, 255, 0.05)');

        const fonts = skin.fonts || {};
        document.getElementById('fontHeading').value = fonts.heading || 'Barlow Condensed';
        document.getElementById('fontBody').value = fonts.body || 'DM Sans';

        const iconRadio = document.querySelector(`input[name="iconLibrary"][value="${skin.icon_library || 'fontawesome'}"]`);
        if (iconRadio) iconRadio.checked = true;

        const tokens = skin.tokens || {};
        document.getElementById('radiusMd').value = tokens['--skin-radius-md'] || '0.5rem';
        document.getElementById('radiusLg').value = tokens['--skin-radius-lg'] || '0.75rem';
        document.getElementById('radiusSm').value = tokens['--skin-radius-sm'] || '0.25rem';
        document.getElementById('radiusXl').value = tokens['--skin-radius-xl'] || '1.5rem';
        document.getElementById('shadowCard').value = tokens['--skin-shadow-card'] || '0 10px 25px rgba(0,0,0,0.1)';
        document.getElementById('shadowModal').value = tokens['--skin-shadow-modal'] || '0 20px 25px -5px rgba(0,0,0,0.2)';

        this.openModal();
    }

    setColor(colorId, textId, value) {
        const colorPicker = document.getElementById(colorId);
        const textInput = document.getElementById(textId);
        if (colorPicker && textInput) {
            textInput.value = value;
            if (this.isValidHex(value)) {
                colorPicker.value = value;
                colorPicker.disabled = false;
            } else {
                colorPicker.disabled = true;
            }
        }
    }

    async saveSkin() {
        const name = document.getElementById('skinName').value.trim();
        if (!name) {
            alert('Nome da skin é obrigatório');
            return;
        }

        const data = {
            name,
            company_name: document.getElementById('companyName').value || null,
            copyright_text: document.getElementById('copyrightText').value || null,
            logo_url: this.currentLogoUrl,
            colors: {
                '--skin-primary': document.getElementById('colorPrimaryText').value,
                '--skin-danger': document.getElementById('colorDangerText').value,
                '--skin-success': document.getElementById('colorSuccessText').value,
                '--skin-warning': document.getElementById('colorWarningText').value,
                '--skin-bg-main': document.getElementById('colorBgMainText').value,
                '--skin-bg-card': document.getElementById('colorBgCardText').value,
                '--skin-primary-hover': document.getElementById('colorPrimaryHoverText').value,
                '--skin-text-main': document.getElementById('colorTextMainText').value,
                '--skin-text-muted': document.getElementById('colorTextMutedText').value,
                '--skin-border-color': document.getElementById('colorBorderColorText').value,
                '--skin-focus-ring': document.getElementById('colorFocusRingText').value,
                '--skin-bg-main-dark': document.getElementById('colorBgMainDarkText').value,
                '--skin-bg-card-dark': document.getElementById('colorBgCardDarkText').value,
                '--skin-text-main-dark': document.getElementById('colorTextMainDarkText').value,
                '--skin-text-muted-dark': document.getElementById('colorTextMutedDarkText').value,
                '--skin-border-color-dark': document.getElementById('colorBorderColorDarkText').value,
            },
            fonts: {
                heading: document.getElementById('fontHeading').value,
                body: document.getElementById('fontBody').value,
            },
            icon_library: document.querySelector('input[name="iconLibrary"]:checked')?.value || 'fontawesome',
            tokens: {
                '--skin-radius-sm': document.getElementById('radiusSm').value,
                '--skin-radius-md': document.getElementById('radiusMd').value,
                '--skin-radius-lg': document.getElementById('radiusLg').value,
                '--skin-radius-xl': document.getElementById('radiusXl').value,
                '--skin-shadow-card': document.getElementById('shadowCard').value,
                '--skin-shadow-modal': document.getElementById('shadowModal').value,
            },
        };

        try {
            const url = this.editingSkinId
                ? `${this.apiBase}/themes/${this.editingSkinId}`
                : `${this.apiBase}/themes`;
            const method = this.editingSkinId ? 'PUT' : 'POST';

            const resp = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${this.token}`,
                },
                body: JSON.stringify(data),
            });

            if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.detail || 'Erro ao salvar skin');
            }

            const savedSkin = await resp.json();

            if (this.pendingLogoFile) {
                await this.uploadLogo(this.pendingLogoFile, savedSkin.id);
            }

            this.closeModal();
            await this.loadSkins();
            this.toastSuccess('Skin salva com sucesso.');
        } catch (e) {
            console.error('Erro ao salvar skin:', e);
            this.toastError(e);
        }
    }

    async activateSkin(id) {
        try {
            const resp = await fetch(`${this.apiBase}/themes/${id}/activate`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${this.token}` },
            });
            if (!resp.ok) throw new Error('Erro ao ativar skin');
            await this.loadSkins();
            const companyId = window.grindx.session.getUserProfile()?.empresa_id || window.dashboard?.user?.company_id;
            if (companyId && window.skinLoader) {
                window.skinLoader.reload(parseInt(companyId));
            }
            this.toastSuccess('Skin ativada com sucesso.');
        } catch (e) {
            console.error('Erro ao ativar skin:', e);
            this.toastError(e);
        }
    }

    async deleteSkin(id) {
        if (!confirm('Tem certeza que deseja excluir esta skin?')) return;

        try {
            const resp = await fetch(`${this.apiBase}/themes/${id}`, {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${this.token}` },
            });
            if (!resp.ok) {
                const err = await resp.json();
                if (resp.status === 409) {
                    throw new Error('Não é possível excluir uma skin ativa. Desative-a primeiro.');
                }
                throw new Error(err.detail || 'Erro ao excluir skin');
            }
            await this.loadSkins();
            this.toastSuccess('Skin excluída com sucesso.');
        } catch (e) {
            console.error('Erro ao excluir skin:', e);
            this.toastError(e);
        }
    }

    testSkin(id) {
        // Open dashboard in preview mode
        const url = `dashboard.html?skin_preview=${id}`;
        window.open(url, '_blank');
    }

    previewSkin() {
        const colors = {
            '--skin-primary': document.getElementById('colorPrimaryText').value,
            '--skin-danger': document.getElementById('colorDangerText').value,
            '--skin-success': document.getElementById('colorSuccessText').value,
            '--skin-warning': document.getElementById('colorWarningText').value,
            '--skin-bg-main': document.getElementById('colorBgMainText').value,
            '--skin-bg-card': document.getElementById('colorBgCardText').value,
            '--skin-primary-hover': document.getElementById('colorPrimaryHoverText').value,
            '--skin-text-main': document.getElementById('colorTextMainText').value,
            '--skin-text-muted': document.getElementById('colorTextMutedText').value,
            '--skin-border-color': document.getElementById('colorBorderColorText').value,
            '--skin-focus-ring': document.getElementById('colorFocusRingText').value,
            '--skin-bg-main-dark': document.getElementById('colorBgMainDarkText').value,
            '--skin-bg-card-dark': document.getElementById('colorBgCardDarkText').value,
            '--skin-text-main-dark': document.getElementById('colorTextMainDarkText').value,
            '--skin-text-muted-dark': document.getElementById('colorTextMutedDarkText').value,
            '--skin-border-color-dark': document.getElementById('colorBorderColorDarkText').value,
        };

        if (window.skinLoader) {
            window.skinLoader.applyPreviewColors(colors);
        }

        // Apply icon library on preview
        const iconLibrary = document.querySelector('input[name="iconLibrary"]:checked')?.value || 'fontawesome';
        if (window.skinLoader) {
            window.skinLoader._loadIconLibrary(iconLibrary);
        }

        // Reset toggle state whenever preview is applied
        this._darkPreview = false;
        const icon = document.getElementById('previewThemeToggle');
        if (icon) icon.className = 'fas fa-moon';
    }

    togglePreviewTheme() {
        this._darkPreview = !this._darkPreview;
        const icon = document.getElementById('previewThemeToggle');
        const preview = document.querySelector('.preview-dashboard');

        if (!preview) return;

        if (this._darkPreview) {
            // Apply dark mode colors to preview
            const darkVars = {
                '--skin-bg-main': document.getElementById('colorBgMainDarkText').value,
                '--skin-bg-card': document.getElementById('colorBgCardDarkText').value,
                '--skin-text-main': document.getElementById('colorTextMainDarkText').value,
                '--skin-text-muted': document.getElementById('colorTextMutedDarkText').value,
                '--skin-border-color': document.getElementById('colorBorderColorDarkText').value,
            };
            for (const [key, value] of Object.entries(darkVars)) {
                preview.style.setProperty(key, value);
            }
            if (icon) icon.className = 'fas fa-sun';
        } else {
            // Restore light mode colors
            const lightVars = {
                '--skin-bg-main': document.getElementById('colorBgMainText').value,
                '--skin-bg-card': document.getElementById('colorBgCardText').value,
                '--skin-text-main': document.getElementById('colorTextMainText').value,
                '--skin-text-muted': document.getElementById('colorTextMutedText').value,
                '--skin-border-color': document.getElementById('colorBorderColorText').value,
            };
            for (const [key, value] of Object.entries(lightVars)) {
                preview.style.setProperty(key, value);
            }
            if (icon) icon.className = 'fas fa-moon';
        }
    }

    resetPreview() {
        if (window.skinLoader) {
            window.skinLoader.resetToDefaults();
        }
        this.setColor('colorPrimary', 'colorPrimaryText', '#00c2e0');
        this.setColor('colorDanger', 'colorDangerText', '#ef4444');
        this.setColor('colorSuccess', 'colorSuccessText', '#10b981');
        this.setColor('colorWarning', 'colorWarningText', '#f59e0b');
        this.setColor('colorBgMain', 'colorBgMainText', '#f8fafc');
        this.setColor('colorBgCard', 'colorBgCardText', '#ffffff');
        this.setColor('colorPrimaryHover', 'colorPrimaryHoverText', '#00a8c4');
        this.setColor('colorTextMain', 'colorTextMainText', '#1e293b');
        this.setColor('colorTextMuted', 'colorTextMutedText', '#64748b');
        this.setColor('colorBorderColor', 'colorBorderColorText', '#e2e8f0');
        this.setColor('colorFocusRing', 'colorFocusRingText', '#00c2e0');
        document.getElementById('colorFocusRingText').value = 'rgba(0, 194, 224, 0.35)';
        this.setColor('colorBgMainDark', 'colorBgMainDarkText', '#0f172a');
        this.setColor('colorBgCardDark', 'colorBgCardDarkText', '#1e293b');
        this.setColor('colorTextMainDark', 'colorTextMainDarkText', '#f8fafc');
        this.setColor('colorTextMutedDark', 'colorTextMutedDarkText', '#94a3b8');
        this.setColor('colorBorderColorDark', 'colorBorderColorDarkText', '#ffffff');
        document.getElementById('colorBorderColorDarkText').value = 'rgba(255, 255, 255, 0.05)';
    }

    generateDarkMode() {
        // Simple dark mode generation algorithm
        const lightColors = {
            '--skin-bg-main': document.getElementById('colorBgMainText').value,
            '--skin-bg-card': document.getElementById('colorBgCardText').value,
            '--skin-text-main': document.getElementById('colorTextMainText').value,
            '--skin-text-muted': document.getElementById('colorTextMutedText').value,
            '--skin-border-color': document.getElementById('colorBorderColorText').value,
        };

        const darkColors = {};
        for (const [key, value] of Object.entries(lightColors)) {
            if (this.isValidHex(value)) {
                const luminance = this.getLuminance(value);
                if (luminance > 0.5) {
                    // Light color -> make dark
                    darkColors[key + '-dark'] = this.invertColor(value, 0.15);
                } else {
                    // Dark color -> make light
                    darkColors[key + '-dark'] = this.invertColor(value, 0.85);
                }
            }
        }

        // Apply to form
        if (darkColors['--skin-bg-main-dark']) {
            this.setColor('colorBgMainDark', 'colorBgMainDarkText', darkColors['--skin-bg-main-dark']);
        }
        if (darkColors['--skin-bg-card-dark']) {
            this.setColor('colorBgCardDark', 'colorBgCardDarkText', darkColors['--skin-bg-card-dark']);
        }
        if (darkColors['--skin-text-main-dark']) {
            this.setColor('colorTextMainDark', 'colorTextMainDarkText', darkColors['--skin-text-main-dark']);
        }
        if (darkColors['--skin-text-muted-dark']) {
            this.setColor('colorTextMutedDark', 'colorTextMutedDarkText', darkColors['--skin-text-muted-dark']);
        }
        if (darkColors['--skin-border-color-dark']) {
            this.setColor('colorBorderColorDark', 'colorBorderColorDarkText', darkColors['--skin-border-color-dark']);
        }

        this.previewSkin();
    }

    getLuminance(hex) {
        const rgb = this.hexToRgb(hex);
        if (!rgb) return 0.5;
        const [r, g, b] = [rgb.r, rgb.g, rgb.b].map(c => {
            c /= 255;
            return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
        });
        return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    }

    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }

    invertColor(hex, targetLuminance) {
        const rgb = this.hexToRgb(hex);
        if (!rgb) return hex;
        const r = Math.round(255 * targetLuminance);
        const g = Math.round(255 * targetLuminance);
        const b = Math.round(255 * targetLuminance);
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }

    handleLogoUpload(e) {
        const file = e.target.files[0];
        if (!file) return;

        const preview = document.getElementById('logoPreview');
        if (preview) {
            const reader = new FileReader();
            reader.onload = (event) => {
                preview.innerHTML = `<img src="${event.target.result}" alt="Logo preview">`;
            };
            reader.readAsDataURL(file);
        }

        this.pendingLogoFile = file;

        // Upload to API if editing
        if (this.editingSkinId) {
            this.uploadLogo(file, this.editingSkinId);
        }
    }

    async uploadLogo(file, skinId) {
        const id = skinId || this.editingSkinId;
        if (!id) return;

        try {
            const formData = new FormData();
            formData.append('file', file);

            const resp = await fetch(`${this.apiBase}/themes/${id}/logo`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${this.token}` },
                body: formData,
            });

            if (!resp.ok) throw new Error('Erro ao fazer upload do logo');

            const result = await resp.json();
            this.currentLogoUrl = result.logo_url || '';
            this.pendingLogoFile = null;

            const preview = document.getElementById('logoPreview');
            if (preview && this.currentLogoUrl) {
                this._setPreviewImage(preview, this.currentLogoUrl);
            }
        } catch (e) {
            console.error('Erro ao fazer upload do logo:', e);
            this.toastError(e);
        }
    }

    _setPreviewImage(previewEl, logoUrl) {
        previewEl.innerHTML = '';
        const img = document.createElement('img');
        const fullUrl = window.skinLoader?._resolveUrl(logoUrl) || logoUrl;
        img.src = fullUrl;
        img.alt = 'Logo preview';
        img.onerror = () => {
            this._resetPreviewDefault(previewEl);
        };
        previewEl.appendChild(img);
    }

    _resetPreviewDefault(previewEl) {
        previewEl.innerHTML = '<i class="fas fa-cloud-upload-alt"></i><span>Arraste um arquivo ou clique para selecionar</span>';
    }

    openTemplatePicker() {
        document.getElementById('templateModal').style.display = 'flex';
    }

    closeTemplatePicker() {
        document.getElementById('templateModal').style.display = 'none';
    }

    selectTemplate(slug) {
        const template = this.templates.find(t => t.slug === slug);
        if (!template) return;

        // Create theme from template via API
        this.createThemeFromTemplate(slug, template.name);
        this.closeTemplatePicker();
    }

    async createThemeFromTemplate(slug, templateName) {
        try {
            const resp = await fetch(`${this.apiBase}/themes/from-template`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${this.token}`,
                },
                body: JSON.stringify({
                    template_slug: slug,
                    name: templateName,
                }),
            });

            if (!resp.ok) throw new Error('Erro ao criar tema a partir do template');

            await this.loadSkins();
            alert(`Skin "${templateName}" criada com sucesso!`);
        } catch (e) {
            console.error('Erro ao criar tema do template:', e);
            alert(e.message);
        }
    }

    toggleAdvancedMode() {
        const advancedColors = document.querySelector('.advanced-colors');
        const darkModeTokens = document.querySelector('.dark-mode-tokens');
        const advancedOnly = document.querySelectorAll('.advanced-only');
        const autoDarkBtn = document.getElementById('btnAutoDarkMode');

        if (this.advancedMode) {
            if (advancedColors) advancedColors.style.display = 'block';
            if (darkModeTokens) darkModeTokens.style.display = 'block';
            advancedOnly.forEach(el => el.style.display = 'flex');
            if (autoDarkBtn) autoDarkBtn.style.display = 'inline-flex';
        } else {
            if (advancedColors) advancedColors.style.display = 'none';
            if (darkModeTokens) darkModeTokens.style.display = 'none';
            advancedOnly.forEach(el => el.style.display = 'none');
            if (autoDarkBtn) autoDarkBtn.style.display = 'none';
        }
    }

    resetForm() {
        this.currentLogoUrl = null;
        this.pendingLogoFile = null;
        document.getElementById('skinName').value = '';
        document.getElementById('companyName').value = '';
        document.getElementById('copyrightText').value = '';
        this.resetPreview();
        document.getElementById('fontHeading').value = 'Barlow Condensed';
        document.getElementById('fontBody').value = 'DM Sans';
        document.querySelector('input[name="iconLibrary"][value="fontawesome"]').checked = true;
        document.getElementById('radiusSm').value = '0.25rem';
        document.getElementById('radiusMd').value = '0.5rem';
        document.getElementById('radiusLg').value = '0.75rem';
        document.getElementById('radiusXl').value = '1.5rem';
        document.getElementById('shadowCard').value = '0 10px 25px rgba(0,0,0,0.1)';
        document.getElementById('shadowModal').value = '0 20px 25px -5px rgba(0,0,0,0.2)';

        // Reset logo preview
        const logoPreview = document.getElementById('logoPreview');
        if (logoPreview) {
            this._resetPreviewDefault(logoPreview);
        }
    }

    openModal() {
        document.getElementById('skinModal').style.display = 'flex';
    }

    closeModal() {
        document.getElementById('skinModal').style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.adminSkins = new AdminSkinsController();
});
