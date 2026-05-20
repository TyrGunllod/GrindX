/**
 * ADMIN SKINS MODULE - GrindX
 * Gestão de skins/temas via módulo admin.
 */

class AdminSkinsController {
    constructor() {
        this.skins = [];
        this.editingSkinId = null;
        this.apiBase = window.grindx.config.API_BASE_URL;
        this.token = window.grindx.session.getToken();

        this.init();
    }

    async init() {
        this.setupEvents();
        await this.loadSkins();
    }

    setupEvents() {
        document.getElementById('btnNewSkin')?.addEventListener('click', () => this.openNewSkinModal());
        document.getElementById('btnCloseModal')?.addEventListener('click', () => this.closeModal());
        document.getElementById('btnSaveSkin')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.saveSkin();
        });
        document.getElementById('btnPreviewSkin')?.addEventListener('click', () => this.previewSkin());
        document.getElementById('btnResetSkin')?.addEventListener('click', () => this.resetPreview());

        // Color pickers live update
        ['colorPrimary', 'colorDanger', 'colorSuccess', 'colorWarning', 'colorBgMain', 'colorBgCard'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('input', (e) => {
                    document.getElementById(id + 'Value').textContent = e.target.value;
                    this.previewSkin();
                });
            }
        });

        // Font select live update
        ['fontHeading', 'fontBody'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('change', () => this.previewSkin());
            }
        });
    }

    async loadSkins() {
        try {
            const resp = await fetch(`${this.apiBase}/themes`, {
                headers: { Authorization: `Bearer ${this.token}` },
            });
            if (!resp.ok) throw new Error('Failed to load skins');
            this.skins = await resp.json();
            this.renderSkins();
        } catch (e) {
            console.error('Erro ao carregar skins:', e);
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
        `;
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
        document.getElementById('modalTitle').textContent = `Editar: ${skin.name}`;

        document.getElementById('skinName').value = skin.name || '';
        document.getElementById('companyName').value = skin.company_name || '';
        document.getElementById('copyrightText').value = skin.copyright_text || '';
        document.getElementById('logoUrl').value = skin.logo_url || '';
        document.getElementById('logoShortUrl').value = skin.logo_short_url || '';

        const colors = skin.colors || {};
        document.getElementById('colorPrimary').value = colors['--skin-primary'] || '#00c2e0';
        document.getElementById('colorPrimaryValue').textContent = colors['--skin-primary'] || '#00c2e0';
        document.getElementById('colorDanger').value = colors['--skin-danger'] || '#ef4444';
        document.getElementById('colorDangerValue').textContent = colors['--skin-danger'] || '#ef4444';
        document.getElementById('colorSuccess').value = colors['--skin-success'] || '#10b981';
        document.getElementById('colorSuccessValue').textContent = colors['--skin-success'] || '#10b981';
        document.getElementById('colorWarning').value = colors['--skin-warning'] || '#f59e0b';
        document.getElementById('colorWarningValue').textContent = colors['--skin-warning'] || '#f59e0b';
        document.getElementById('colorBgMain').value = colors['--skin-bg-main'] || '#f8fafc';
        document.getElementById('colorBgMainValue').textContent = colors['--skin-bg-main'] || '#f8fafc';
        document.getElementById('colorBgCard').value = colors['--skin-bg-card'] || '#ffffff';
        document.getElementById('colorBgCardValue').textContent = colors['--skin-bg-card'] || '#ffffff';

        const fonts = skin.fonts || {};
        document.getElementById('fontHeading').value = fonts.heading || 'Barlow Condensed';
        document.getElementById('fontBody').value = fonts.body || 'DM Sans';

        const iconRadio = document.querySelector(`input[name="iconLibrary"][value="${skin.icon_library || 'fontawesome'}"]`);
        if (iconRadio) iconRadio.checked = true;

        const tokens = skin.tokens || {};
        document.getElementById('radiusMd').value = tokens['--skin-radius-md'] || '0.5rem';
        document.getElementById('radiusLg').value = tokens['--skin-radius-lg'] || '0.75rem';

        this.openModal();
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
            logo_url: document.getElementById('logoUrl').value || null,
            logo_short_url: document.getElementById('logoShortUrl').value || null,
            colors: {
                '--skin-primary': document.getElementById('colorPrimary').value,
                '--skin-danger': document.getElementById('colorDanger').value,
                '--skin-success': document.getElementById('colorSuccess').value,
                '--skin-warning': document.getElementById('colorWarning').value,
                '--skin-bg-main': document.getElementById('colorBgMain').value,
                '--skin-bg-card': document.getElementById('colorBgCard').value,
            },
            fonts: {
                heading: document.getElementById('fontHeading').value,
                body: document.getElementById('fontBody').value,
            },
            icon_library: document.querySelector('input[name="iconLibrary"]:checked')?.value || 'fontawesome',
            tokens: {
                '--skin-radius-md': document.getElementById('radiusMd').value,
                '--skin-radius-lg': document.getElementById('radiusLg').value,
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

            this.closeModal();
            await this.loadSkins();
        } catch (e) {
            console.error('Erro ao salvar skin:', e);
            alert(e.message);
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
        } catch (e) {
            console.error('Erro ao ativar skin:', e);
            alert(e.message);
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
        } catch (e) {
            console.error('Erro ao excluir skin:', e);
            alert(e.message);
        }
    }

    previewSkin() {
        const colors = {
            '--skin-primary': document.getElementById('colorPrimary').value,
            '--skin-danger': document.getElementById('colorDanger').value,
            '--skin-success': document.getElementById('colorSuccess').value,
            '--skin-warning': document.getElementById('colorWarning').value,
            '--skin-bg-main': document.getElementById('colorBgMain').value,
            '--skin-bg-card': document.getElementById('colorBgCard').value,
        };

        if (window.skinLoader) {
            window.skinLoader.applyPreviewColors(colors);
        }

        const previewCard = document.getElementById('previewCard');
        if (previewCard) {
            previewCard.style.background = colors['--skin-bg-card'];
            previewCard.style.borderColor = colors['--skin-border-color'] || '#e2e8f0';
            const header = previewCard.querySelector('.preview-header');
            if (header) header.style.background = colors['--skin-primary'];
        }
    }

    resetPreview() {
        if (window.skinLoader) {
            window.skinLoader.resetToDefaults();
        }
        document.getElementById('colorPrimary').value = '#00c2e0';
        document.getElementById('colorPrimaryValue').textContent = '#00c2e0';
        document.getElementById('colorDanger').value = '#ef4444';
        document.getElementById('colorDangerValue').textContent = '#ef4444';
        document.getElementById('colorSuccess').value = '#10b981';
        document.getElementById('colorSuccessValue').textContent = '#10b981';
        document.getElementById('colorWarning').value = '#f59e0b';
        document.getElementById('colorWarningValue').textContent = '#f59e0b';
        document.getElementById('colorBgMain').value = '#f8fafc';
        document.getElementById('colorBgMainValue').textContent = '#f8fafc';
        document.getElementById('colorBgCard').value = '#ffffff';
        document.getElementById('colorBgCardValue').textContent = '#ffffff';
    }

    resetForm() {
        document.getElementById('skinName').value = '';
        document.getElementById('companyName').value = '';
        document.getElementById('copyrightText').value = '';
        document.getElementById('logoUrl').value = '';
        document.getElementById('logoShortUrl').value = '';
        this.resetPreview();
        document.getElementById('fontHeading').value = 'Barlow Condensed';
        document.getElementById('fontBody').value = 'DM Sans';
        document.querySelector('input[name="iconLibrary"][value="fontawesome"]').checked = true;
        document.getElementById('radiusMd').value = '0.5rem';
        document.getElementById('radiusLg').value = '0.75rem';
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
