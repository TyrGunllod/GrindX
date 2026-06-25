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
        this.customFonts = [];
        this.iconFont = null;
        this._currentSnapshot = null;
        this._originalSnapshot = null;
        this.apiBase = window.grindx.config.API_BASE_URL;

        this.init();
    }

    async init() {
        if (!this.requireAuth('../../index.html')) return;
        this.setupEvents();
        await this.loadSkins();
        await this.loadTemplates();
    }

    setupEvents() {
        // Header buttons
        document.getElementById('btnUseTemplate')?.addEventListener('click', () => this.openTemplatePicker());
        document.getElementById('btnImportSkin')?.addEventListener('click', () => this.importSkin());

        // Modals
        document.getElementById('btnCloseModal')?.addEventListener('click', () => this.closeModal());
        document.getElementById('btnCloseTemplateModal')?.addEventListener('click', () => this.closeTemplatePicker());
        document.getElementById('btnCancelTemplate')?.addEventListener('click', () => this.closeTemplatePicker());

        // Save/Reset/Preview
        document.getElementById('btnSaveSkin')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.saveSkin();
        });
        document.getElementById('btnResetSkin')?.addEventListener('click', () => {
            this.resetPreview();
            this._updateResetButton();
        });
        document.getElementById('btnAutoDarkMode')?.addEventListener('click', () => this.generateDarkMode());

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

        // Font import via ZIP
        const fontUploadArea = document.getElementById('fontUploadArea');
        const fontFileInput = document.getElementById('customFontFile');
        if (fontUploadArea && fontFileInput) {
            fontUploadArea.addEventListener('click', () => fontFileInput.click());
            fontFileInput.addEventListener('change', (e) => this.processFontZip(e));
        }

        // Icon font upload
        const iconUploadArea = document.getElementById('iconUploadArea');
        const iconFileInput = document.getElementById('iconFontFile');
        if (iconUploadArea && iconFileInput) {
            iconUploadArea.addEventListener('click', () => iconFileInput.click());
            iconFileInput.addEventListener('change', (e) => this.processIconFont(e));
        }
        document.getElementById('btnRemoveIconFont')?.addEventListener('click', () => this.removeIconFont());

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

        // Logo upload
        const logoFile = document.getElementById('logoFile');
        const uploadArea = document.querySelector('.upload-area');
        if (logoFile && uploadArea) {
            uploadArea.addEventListener('click', () => logoFile.click());
            logoFile.addEventListener('change', (e) => this.handleLogoUpload(e));
        }

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

    _updateSectionPreviews() {
        const g = (id) => document.getElementById(id);

        // Basic Colors preview
        const basicInner = g('previewBasic')?.querySelector('.section-preview-inner');
        if (basicInner) {
            const bgMain = g('colorBgMainText')?.value || '#f8fafc';
            const bgCard = g('colorBgCardText')?.value || '#ffffff';
            const primary = g('colorPrimaryText')?.value || '#00c2e0';
            const success = g('colorSuccessText')?.value || '#10b981';
            const danger = g('colorDangerText')?.value || '#ef4444';
            const warning = g('colorWarningText')?.value || '#f59e0b';
            basicInner.style.background = bgMain;
            basicInner.style.color = g('colorTextMainText')?.value || '#1e293b';
            if (g('pbBtn')) { g('pbBtn').style.background = primary; g('pbBtn').style.color = '#fff'; }
            if (g('pbSuccess')) { g('pbSuccess').style.background = success; g('pbSuccess').style.color = '#fff'; }
            if (g('pbDanger')) { g('pbDanger').style.background = danger; g('pbDanger').style.color = '#fff'; }
            if (g('pbWarning')) { g('pbWarning').style.background = warning; g('pbWarning').style.color = '#fff'; }
            if (g('pbCard')) {
                g('pbCard').style.background = bgCard;
                g('pbCard').style.borderColor = g('colorBorderColorText')?.value || '#e2e8f0';
                g('pbCard').style.color = g('colorTextMainText')?.value || '#1e293b';
            }
        }

        // Advanced Colors preview
        const advInner = g('previewAdvanced')?.querySelector('.section-preview-inner');
        if (advInner) {
            advInner.style.background = g('colorBgMainText')?.value || '#f8fafc';
            const primaryHover = g('colorPrimaryHoverText')?.value || '#00a8c4';
            const textMain = g('colorTextMainText')?.value || '#1e293b';
            const textMuted = g('colorTextMutedText')?.value || '#64748b';
            const borderColor = g('colorBorderColorText')?.value || '#e2e8f0';
            const focusRing = g('colorFocusRingText')?.value || 'rgba(0,194,224,0.35)';
            if (g('paBtn')) { g('paBtn').style.background = primaryHover; g('paBtn').style.color = '#fff'; }
            if (g('paTextMain')) g('paTextMain').style.color = textMain;
            if (g('paTextMuted')) g('paTextMuted').style.color = textMuted;
            if (g('paBorder')) {
                g('paBorder').style.borderColor = borderColor;
                g('paBorder').style.background = g('colorBgCardText')?.value || '#ffffff';
                g('paBorder').style.color = textMain;
            }
            if (g('paFocus')) {
                g('paFocus').style.borderColor = borderColor;
                g('paFocus').style.boxShadow = `0 0 0 2px ${focusRing}`;
                g('paFocus').style.background = g('colorBgCardText')?.value || '#ffffff';
                g('paFocus').style.color = textMain;
            }
        }

        // Dark Mode preview
        const darkInner = g('previewDark')?.querySelector('.section-preview-inner');
        if (darkInner) {
            const bgMainDark = g('colorBgMainDarkText')?.value || '#0f172a';
            const bgCardDark = g('colorBgCardDarkText')?.value || '#1e293b';
            const textMainDark = g('colorTextMainDarkText')?.value || '#f8fafc';
            const textMutedDark = g('colorTextMutedDarkText')?.value || '#94a3b8';
            const borderColorDark = g('colorBorderColorDarkText')?.value || 'rgba(255,255,255,0.05)';
            darkInner.style.background = bgMainDark;
            darkInner.style.color = textMainDark;
            if (g('pdBtn')) { g('pdBtn').style.background = textMainDark; g('pdBtn').style.color = bgMainDark; }
            if (g('pdSuccess')) { g('pdSuccess').style.background = textMainDark; g('pdSuccess').style.color = bgMainDark; }
            if (g('pdDanger')) { g('pdDanger').style.background = textMutedDark; g('pdDanger').style.color = bgMainDark; }
            if (g('pdCard')) {
                g('pdCard').style.background = bgCardDark;
                g('pdCard').style.borderColor = borderColorDark;
                g('pdCard').style.color = textMainDark;
            }
        }

        // Fonts preview
        if (g('pfHeading')) g('pfHeading').style.fontFamily = g('fontHeading')?.value || 'Barlow Condensed';
        if (g('pfBody')) g('pfBody').style.fontFamily = g('fontBody')?.value || 'DM Sans';

        // Tokens Extras preview
        if (g('previewTokens')) {
            const bgCard = g('colorBgCardText')?.value || '#ffffff';
            const borderColor = g('colorBorderColorText')?.value || '#e2e8f0';
            const textMain = g('colorTextMainText')?.value || '#1e293b';
            const radiusSm = g('radiusSm')?.value || '0.25rem';
            const radiusMd = g('radiusMd')?.value || '0.5rem';
            const radiusLg = g('radiusLg')?.value || '0.75rem';
            const radiusXl = g('radiusXl')?.value || '1.5rem';
            const shadowCard = g('shadowCard')?.value || '0 10px 25px rgba(0,0,0,0.1)';
            const shadowModal = g('shadowModal')?.value || '0 20px 25px -5px rgba(0,0,0,0.2)';
            if (g('ptRadiusSm')) {
                g('ptRadiusSm').style.borderRadius = radiusSm;
                g('ptRadiusSm').style.background = bgCard;
                g('ptRadiusSm').style.borderColor = borderColor;
                g('ptRadiusSm').style.color = textMain;
            }
            if (g('ptRadiusMd')) {
                g('ptRadiusMd').style.borderRadius = radiusMd;
                g('ptRadiusMd').style.background = bgCard;
                g('ptRadiusMd').style.borderColor = borderColor;
                g('ptRadiusMd').style.color = textMain;
            }
            if (g('ptRadiusLg')) {
                g('ptRadiusLg').style.borderRadius = radiusLg;
                g('ptRadiusLg').style.background = bgCard;
                g('ptRadiusLg').style.borderColor = borderColor;
                g('ptRadiusLg').style.color = textMain;
            }
            if (g('ptRadiusXl')) {
                g('ptRadiusXl').style.borderRadius = radiusXl;
                g('ptRadiusXl').style.background = bgCard;
                g('ptRadiusXl').style.borderColor = borderColor;
                g('ptRadiusXl').style.color = textMain;
            }
            if (g('ptShadowCard')) {
                g('ptShadowCard').style.boxShadow = shadowCard;
                g('ptShadowCard').style.background = bgCard;
                g('ptShadowCard').style.borderColor = borderColor;
                g('ptShadowCard').style.color = textMain;
            }
            if (g('ptShadowModal')) {
                g('ptShadowModal').style.boxShadow = shadowModal;
                g('ptShadowModal').style.background = bgCard;
                g('ptShadowModal').style.borderColor = borderColor;
                g('ptShadowModal').style.color = textMain;
            }
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

        if (this.skins.length === 0) {
            grid.innerHTML = '<div class="text-center text-muted" style="padding: 2rem;">Nenhuma skin encontrada. Verifique o console (F12) para erros de API.</div>';
            return;
        }

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
                        <button class="btn btn-danger" onclick="window.adminSkins.deleteSkin(${skin.id})">Excluir</button>
                    </div>
                </div>
            `;
        }).join('');

        grid.innerHTML = cards;
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

    async importSkin() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.style.display = 'none';
        document.body.appendChild(input);

        input.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) {
                document.body.removeChild(input);
                return;
            }

            try {
                const text = await file.text();
                const skinData = JSON.parse(text);

                // Validate required fields
                if (!skinData.name) {
                    alert('Arquivo JSON inválido: campo "name" é obrigatório.');
                    document.body.removeChild(input);
                    return;
                }

                // Send to API
                const resp = await fetch(`${this.apiBase}/themes`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: `Bearer ${this.token}`,
                    },
                    body: JSON.stringify(skinData),
                });

                if (!resp.ok) {
                    const err = await resp.json();
                    throw new Error(err.detail || 'Erro ao importar skin');
                }

                const importedSkin = await resp.json();
                this._originalSnapshot = { ...importedSkin, customFonts: [] };

                await this.loadSkins();
                alert(`Skin "${skinData.name}" importada com sucesso!`);
            } catch (err) {
                console.error('Erro ao importar skin:', err);
                alert(err.message || 'Erro ao processar o arquivo JSON.');
            }

            document.body.removeChild(input);
        });

        input.click();
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
        document.getElementById('layoutMode').value = skin.layout_mode || 'topbar';

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
        this.customFonts = (fonts.custom || []).map(f => ({ name: f.name, data: f.data, format: f.format }));
        this._populateFontDropdowns();

        const icons = fonts.icons || {};
        this.iconFont = icons.url ? { name: icons.name, url: icons.url, format: icons.format } : null;
        document.getElementById('iconFontName').value = icons.name || '';
        if (this.iconFont) {
            document.getElementById('btnRemoveIconFont').style.display = '';
            document.getElementById('iconUploadPreview').innerHTML = `<i class="fas fa-check-circle" style="color:var(--skin-success, #22c55e)"></i> <span>${icons.name || 'Fonte carregada'}</span>`;
        }

        const tokens = skin.tokens || {};
        document.getElementById('radiusMd').value = tokens['--skin-radius-md'] || '0.5rem';
        document.getElementById('radiusLg').value = tokens['--skin-radius-lg'] || '0.75rem';
        document.getElementById('radiusSm').value = tokens['--skin-radius-sm'] || '0.25rem';
        document.getElementById('radiusXl').value = tokens['--skin-radius-xl'] || '1.5rem';
        document.getElementById('shadowCard').value = tokens['--skin-shadow-card'] || '0 10px 25px rgba(0,0,0,0.1)';
        document.getElementById('shadowModal').value = tokens['--skin-shadow-modal'] || '0 20px 25px -5px rgba(0,0,0,0.2)';

        this._currentSnapshot = { ...skin, customFonts: [...this.customFonts] };
        await this._loadOriginalSnapshot(id);
        this.previewSkin();
        this._updateResetButton();
        this.openModal();
    }

    async _loadOriginalSnapshot(id) {
        // Try API endpoint first (most reliable)
        try {
            const resp = await fetch(`${this.apiBase}/themes/${id}/original-snapshot`, {
                headers: { Authorization: `Bearer ${this.token}` },
            });
            if (resp.ok) {
                const data = await resp.json();
                this._originalSnapshot = { ...data, customFonts: [] };
                return;
            }
        } catch (_) {}

        // Fallback: try JSON file by slug (from name)
        const tryFetch = async (url) => {
            try {
                const resp = await fetch(url);
                if (resp.ok) return resp.json();
            } catch (_) {}
            return null;
        };

        if (this._currentSnapshot) {
            const slug = this._currentSnapshot.name
                .toLowerCase()
                .replace(/[^a-z0-9]+/g, '-')
                .replace(/^-|-$/g, '');
            const data = await tryFetch(`../../skins/${slug}.json`);
            if (data) {
                this._originalSnapshot = { ...data, customFonts: [] };
                return;
            }
        }

        this._originalSnapshot = this._currentSnapshot ? { ...this._currentSnapshot } : null;
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

    _populateFontDropdowns() {
        const customNames = this.customFonts.map(f => f.name);
        ['fontHeading', 'fontBody'].forEach(id => {
            const sel = document.getElementById(id);
            if (!sel) return;
            const builtIn = sel.querySelectorAll('option:not(.custom-font-option)');
            const currentValue = sel.value;
            sel.innerHTML = '';
            builtIn.forEach(opt => sel.appendChild(opt.cloneNode(true)));
            customNames.forEach(name => {
                const opt = document.createElement('option');
                opt.value = name;
                opt.textContent = name;
                opt.className = 'custom-font-option';
                sel.appendChild(opt);
            });
            sel.value = currentValue;
        });
    }

    async processFontZip(e) {
        const file = e.target.files[0];
        if (!file) return;
        if (!file.name.toLowerCase().endsWith('.zip')) {
            alert('Selecione um arquivo ZIP.');
            return;
        }

        const statusEl = document.getElementById('fontImportStatus');
        const preview = document.getElementById('fontUploadPreview');

        statusEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando ZIP...';

        try {
            const arrayBuf = await file.arrayBuffer();
            const zip = await JSZip.loadAsync(arrayBuf);

            const fontFiles = [];
            zip.forEach((relPath, entry) => {
                if (!entry.dir) {
                    const ext = relPath.split('.').pop().toLowerCase();
                    if (['ttf', 'otf', 'woff', 'woff2'].includes(ext)) {
                        fontFiles.push({ entry, name: relPath.split('/').pop(), ext });
                    }
                }
            });

            if (fontFiles.length === 0) {
                statusEl.innerHTML = '<span style="color: var(--skin-danger);">Nenhum arquivo de fonte encontrado no ZIP.</span>';
                return;
            }

            let imported = 0;
            let skipped = 0;

            for (const ff of fontFiles) {
                const blob = await ff.entry.async('blob');
                const buf = await blob.arrayBuffer();
                let fontName = null;

                try {
                    const parsed = opentype.parse(buf);
                    fontName = parsed?.names?.fontFamily?.en || parsed?.names?.fontFamily || null;
                } catch (_) {
                    // fallback: use filename without extension
                }

                if (!fontName) {
                    fontName = ff.name.replace(/\.[^.]+$/, '');
                }

                if (this.customFonts.some(f => f.name.toLowerCase() === fontName.toLowerCase())) {
                    skipped++;
                    continue;
                }

                const formatMap = { ttf: 'truetype', otf: 'opentype', woff: 'woff', woff2: 'woff2' };
                const format = formatMap[ff.ext] || ff.ext;

                // Upload font file to server
                statusEl.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Enviando ${fontName}...`;
                const formData = new FormData();
                const fontFile = new File([blob], ff.name, { type: 'application/octet-stream' });
                formData.append('file', fontFile);

                const resp = await fetch(`${this.apiBase}/themes/fonts-icons/upload`, {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${this.token}` },
                    body: formData,
                });

                if (!resp.ok) {
                    const err = await resp.json();
                    throw new Error(err.detail || 'Erro ao enviar fonte');
                }

                const result = await resp.json();

                this.customFonts.push({ name: fontName, url: result.url, format });
                imported++;
            }

        this._populateFontDropdowns();

        if (imported > 0) {
                statusEl.innerHTML = `<span style="color: var(--skin-success);">${imported} fonte(s) importada(s)${skipped > 0 ? `, ${skipped} ignorada(s) (já existem)` : ''}.</span>`;
                this.previewSkin();
            } else if (skipped > 0) {
                statusEl.innerHTML = `<span style="color: var(--skin-warning);">Todas as ${skipped} fonte(s) já foram importadas.</span>`;
            }
        } catch (err) {
            console.error('Erro ao processar ZIP:', err);
            statusEl.innerHTML = `<span style="color: var(--skin-danger);">${err.message || 'Erro ao processar o arquivo ZIP.'}</span>`;
        }

        if (preview) {
            preview.innerHTML = `<i class="fas fa-file-archive"></i><span>${file.name}</span>`;
        }
        e.target.value = '';
    }

    async processIconFont(e) {
        const file = e.target.files[0];
        if (!file) return;

        const allowedExts = ['.woff2', '.woff', '.ttf', '.otf'];
        const ext = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowedExts.includes(ext)) {
            alert('Formato nao suportado. Use .woff2, .woff, .ttf ou .otf.');
            return;
        }

        const name = document.getElementById('iconFontName').value.trim() || file.name.replace(/\.[^.]+$/, '');
        const statusEl = document.getElementById('iconImportStatus');
        const preview = document.getElementById('iconUploadPreview');

        statusEl.textContent = 'Enviando...';
        statusEl.className = 'font-import-status';

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('type', 'icon');

            const resp = await fetch(`${this.apiBase}/themes/fonts-icons/upload`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${this.token}` },
                body: formData,
            });

            if (!resp.ok) {
                const err = await resp.json().catch(() => ({}));
                throw new Error(err.detail || 'Erro no upload');
            }

            const data = await resp.json();
            this.iconFont = { name, url: data.url, format: ext.replace('.', '') };

            statusEl.textContent = `Fonte de icones "${name}" importada com sucesso.`;
            statusEl.className = 'font-import-status success';
            preview.innerHTML = `<i class="fas fa-check-circle" style="color:var(--skin-success, #22c55e)"></i> <span>${name}</span>`;
            document.getElementById('btnRemoveIconFont').style.display = '';
            this.previewSkin();
        } catch (err) {
            statusEl.textContent = err.message;
            statusEl.className = 'font-import-status error';
        }
    }

    removeIconFont() {
        this.iconFont = null;
        document.getElementById('iconFontName').value = '';
        document.getElementById('iconFontFile').value = '';
        document.getElementById('iconImportStatus').textContent = '';
        document.getElementById('iconImportStatus').className = 'font-import-status';
        document.getElementById('iconUploadPreview').innerHTML = '<i class="fas fa-icons"></i> <span>Clique para selecionar um arquivo de fonte</span>';
        document.getElementById('btnRemoveIconFont').style.display = 'none';
        this.previewSkin();
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
                custom: this.customFonts,
                icons: this.iconFont || null,
            },
            icon_library: 'fontawesome',
            layout_mode: document.getElementById('layoutMode').value || 'topbar',
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

            this._currentSnapshot = { ...savedSkin, customFonts: [...this.customFonts] };
            this.editingSkinId = savedSkin.id;

            this.closeModal();
            await this.loadSkins();
            this.toastSuccess('Skin salva com sucesso.');
            setTimeout(() => {
                if (window.parent !== window) {
                    // Limpa cache do pai antes de recarregar
                    const companyId = window.grindx.session.getUserProfile()?.empresa_id;
                    if (companyId && window.parent.skinLoader) {
                        window.parent.skinLoader.clearCache(parseInt(companyId));
                    }
                    window.parent.location.reload();
                } else {
                    const companyId = window.grindx.session.getUserProfile()?.empresa_id;
                    if (companyId && window.skinLoader) {
                        window.skinLoader.clearCache(parseInt(companyId));
                    }
                    location.reload();
                }
            }, 1500);
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
            this.toastSuccess('Skin ativada com sucesso.');
            setTimeout(() => {
                if (window.parent !== window) {
                    const companyId = window.grindx.session.getUserProfile()?.empresa_id;
                    if (companyId && window.parent.skinLoader) {
                        window.parent.skinLoader.clearCache(parseInt(companyId));
                    }
                    window.parent.location.reload();
                } else {
                    const companyId = window.grindx.session.getUserProfile()?.empresa_id;
                    if (companyId && window.skinLoader) {
                        window.skinLoader.clearCache(parseInt(companyId));
                    }
                    const companyIdReload = window.grindx.session.getUserProfile()?.empresa_id;
                    if (companyIdReload && window.skinLoader) {
                        window.skinLoader.reload(parseInt(companyIdReload));
                    }
                }
            }, 1500);
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

        const fonts = {
            heading: document.getElementById('fontHeading').value,
            body: document.getElementById('fontBody').value,
            custom: this.customFonts,
        };

        if (window.skinLoader) {
            window.skinLoader.applyPreviewColors(colors);
            window.skinLoader._applyFonts(fonts);
        }

        if (this.iconFont) {
            window.skinLoader._applyIconFont(this.iconFont);
        } else {
            window.skinLoader._removeIconFont();
        }

        this._updateSectionPreviews();
        this._updateResetButton();
    }

    _applySnapshot(snap) {
        const c = snap.colors || {};
        const f = snap.fonts || {};
        const t = snap.tokens || {};

        document.getElementById('skinName').value = snap.name || '';
        document.getElementById('companyName').value = snap.company_name || '';
        document.getElementById('copyrightText').value = snap.copyright_text || '';
        document.getElementById('layoutMode').value = snap.layout_mode || 'topbar';

        this.currentLogoUrl = snap.logo_url || null;
        this.pendingLogoFile = null;
        const logoPreview = document.getElementById('logoPreview');
        if (logoPreview) {
            if (snap.logo_url) this._setPreviewImage(logoPreview, snap.logo_url);
            else this._resetPreviewDefault(logoPreview);
        }

        this.setColor('colorPrimary', 'colorPrimaryText', c['--skin-primary'] || '#00c2e0');
        this.setColor('colorDanger', 'colorDangerText', c['--skin-danger'] || '#ef4444');
        this.setColor('colorSuccess', 'colorSuccessText', c['--skin-success'] || '#10b981');
        this.setColor('colorWarning', 'colorWarningText', c['--skin-warning'] || '#f59e0b');
        this.setColor('colorBgMain', 'colorBgMainText', c['--skin-bg-main'] || '#f8fafc');
        this.setColor('colorBgCard', 'colorBgCardText', c['--skin-bg-card'] || '#ffffff');
        this.setColor('colorPrimaryHover', 'colorPrimaryHoverText', c['--skin-primary-hover'] || '#00a8c4');
        this.setColor('colorTextMain', 'colorTextMainText', c['--skin-text-main'] || '#1e293b');
        this.setColor('colorTextMuted', 'colorTextMutedText', c['--skin-text-muted'] || '#64748b');
        this.setColor('colorBorderColor', 'colorBorderColorText', c['--skin-border-color'] || '#e2e8f0');
        this.setColor('colorFocusRing', 'colorFocusRingText', c['--skin-focus-ring'] || 'rgba(0, 194, 224, 0.35)');
        this.setColor('colorBgMainDark', 'colorBgMainDarkText', c['--skin-bg-main-dark'] || '#0f172a');
        this.setColor('colorBgCardDark', 'colorBgCardDarkText', c['--skin-bg-card-dark'] || '#1e293b');
        this.setColor('colorTextMainDark', 'colorTextMainDarkText', c['--skin-text-main-dark'] || '#f8fafc');
        this.setColor('colorTextMutedDark', 'colorTextMutedDarkText', c['--skin-text-muted-dark'] || '#94a3b8');
        this.setColor('colorBorderColorDark', 'colorBorderColorDarkText', c['--skin-border-color-dark'] || 'rgba(255, 255, 255, 0.05)');

        document.getElementById('fontHeading').value = f.heading || 'Barlow Condensed';
        document.getElementById('fontBody').value = f.body || 'DM Sans';
        this.customFonts = snap.customFonts || (f.custom || []).map(fo => ({ name: fo.name, url: fo.url, format: fo.format }));
        this._populateFontDropdowns();

        document.getElementById('radiusMd').value = t['--skin-radius-md'] || '0.5rem';
        document.getElementById('radiusLg').value = t['--skin-radius-lg'] || '0.75rem';
        document.getElementById('radiusSm').value = t['--skin-radius-sm'] || '0.25rem';
        document.getElementById('radiusXl').value = t['--skin-radius-xl'] || '1.5rem';
        document.getElementById('shadowCard').value = t['--skin-shadow-card'] || '0 10px 25px rgba(0,0,0,0.1)';
        document.getElementById('shadowModal').value = t['--skin-shadow-modal'] || '0 20px 25px -5px rgba(0,0,0,0.2)';

        if (window.skinLoader) {
            window.skinLoader.resetToDefaults();
        }
        this.previewSkin();
    }

    _hasFormChanges() {
        const snap = this._originalSnapshot || this._currentSnapshot;
        if (!snap) return false;
        const s = snap;
        const c = s.colors || {};
        const f = s.fonts || {};
        const t = s.tokens || {};
        const val = (id, fallback = '') => document.getElementById(id)?.value ?? fallback;

        return (
            val('skinName') !== (s.name || '') ||
            val('companyName') !== (s.company_name || '') ||
            val('copyrightText') !== (s.copyright_text || '') ||
            val('layoutMode') !== (s.layout_mode || 'topbar') ||
            val('colorPrimaryText') !== (c['--skin-primary'] || '#00c2e0') ||
            val('colorDangerText') !== (c['--skin-danger'] || '#ef4444') ||
            val('colorSuccessText') !== (c['--skin-success'] || '#10b981') ||
            val('colorWarningText') !== (c['--skin-warning'] || '#f59e0b') ||
            val('colorBgMainText') !== (c['--skin-bg-main'] || '#f8fafc') ||
            val('colorBgCardText') !== (c['--skin-bg-card'] || '#ffffff') ||
            val('colorPrimaryHoverText') !== (c['--skin-primary-hover'] || '#00a8c4') ||
            val('colorTextMainText') !== (c['--skin-text-main'] || '#1e293b') ||
            val('colorTextMutedText') !== (c['--skin-text-muted'] || '#64748b') ||
            val('colorBorderColorText') !== (c['--skin-border-color'] || '#e2e8f0') ||
            val('colorFocusRingText') !== (c['--skin-focus-ring'] || 'rgba(0, 194, 224, 0.35)') ||
            val('colorBgMainDarkText') !== (c['--skin-bg-main-dark'] || '#0f172a') ||
            val('colorBgCardDarkText') !== (c['--skin-bg-card-dark'] || '#1e293b') ||
            val('colorTextMainDarkText') !== (c['--skin-text-main-dark'] || '#f8fafc') ||
            val('colorTextMutedDarkText') !== (c['--skin-text-muted-dark'] || '#94a3b8') ||
            val('colorBorderColorDarkText') !== (c['--skin-border-color-dark'] || 'rgba(255, 255, 255, 0.05)') ||
            val('fontHeading') !== (f.heading || 'Barlow Condensed') ||
            val('fontBody') !== (f.body || 'DM Sans') ||
            val('radiusMd') !== (t['--skin-radius-md'] || '0.5rem') ||
            val('radiusLg') !== (t['--skin-radius-lg'] || '0.75rem') ||
            val('radiusSm') !== (t['--skin-radius-sm'] || '0.25rem') ||
            val('radiusXl') !== (t['--skin-radius-xl'] || '1.5rem') ||
            val('shadowCard') !== (t['--skin-shadow-card'] || '0 10px 25px rgba(0,0,0,0.1)') ||
            val('shadowModal') !== (t['--skin-shadow-modal'] || '0 20px 25px -5px rgba(0,0,0,0.2)')
        );
    }

    _updateResetButton() {
        const btn = document.getElementById('btnResetSkin');
        if (!btn) return;
        const snap = this._originalSnapshot || this._currentSnapshot;
        btn.style.display = snap && this._hasFormChanges() ? '' : 'none';
    }

    resetPreview() {
        const snap = this._originalSnapshot || this._currentSnapshot;
        if (snap) {
            this._applySnapshot(snap);
        } else {
            this._applySnapshot({
                name: '',
                company_name: '',
                copyright_text: '',
                layout_mode: 'topbar',
                logo_url: null,
                colors: {},
                fonts: { heading: 'Barlow Condensed', body: 'DM Sans', custom: [] },
                tokens: {},
                customFonts: [],
            });
        }
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
        const advancedOnly = document.querySelectorAll('.advanced-only');
        const autoDarkBtn = document.getElementById('btnAutoDarkMode');

        if (this.advancedMode) {
            advancedOnly.forEach(el => el.style.display = 'block');
            if (autoDarkBtn) autoDarkBtn.style.display = 'inline-flex';
        } else {
            advancedOnly.forEach(el => el.style.display = 'none');
            if (autoDarkBtn) autoDarkBtn.style.display = 'none';
        }
    }

    resetForm() {
        this._currentSnapshot = null;
        this._originalSnapshot = null;
        this.currentLogoUrl = null;
        this.pendingLogoFile = null;
        this.customFonts = [];
        this.resetPreview();
        this._populateFontDropdowns();
        document.getElementById('customFontFile').value = '';
        const fontPreview = document.getElementById('fontUploadPreview');
        if (fontPreview) {
            fontPreview.innerHTML = '<i class="fas fa-file-archive"></i><span>Clique para selecionar um arquivo ZIP</span>';
        }
        const statusEl = document.getElementById('fontImportStatus');
        if (statusEl) statusEl.innerHTML = '';
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
