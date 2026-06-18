# Icon Font Import — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adicionar upload de fonte de ícones no módulo admin-skins, abaixo da seção de importação de fontes.

**Architecture:** Unifica upload de fontes e ícones em `POST /v1/themes/fonts-icons/upload` com campo `type`. A fonte de ícones é armazenada no JSON `fonts.icons` da skin e aplicada via `@font-face` + variável CSS `--skin-font-icons`.

**Tech Stack:** FastAPI, Python, vanilla JS, nginx

---

### Task 1: Endpoint unificado `POST /v1/themes/fonts-icons/upload`

**Files:**
- Modify: `apps/api-postgres/app/routers/theme_router.py:399-461`

- [ ] **Step 1: Substituir endpoint `/fonts/upload` por `/fonts-icons/upload`**

Trocar o decorator e adicionar o parâmetro `type`:

```python
@router.post(
    "/fonts-icons/upload",
    response_model=ThemeFontResponse,
    summary="Upload de fonte ou icone",
    description="Faz upload de arquivo de fonte ou icone. type=font para fontes, type=icon para icones.",
    responses={
        400: {"model": ErrorResponse, "description": "Arquivo invalido"},
        413: {"model": ErrorResponse, "description": "Arquivo muito grande"},
    },
)
async def upload_font_or_icon(
    file: UploadFile = File(...),
    type: str = "font",
    current_user=Depends(require_role("admin")),
) -> dict:
```

- [ ] **Step 2: Atualizar validação e diretório de destino**

Dentro da função, após validar extensão e magic bytes, determinar o diretório:

```python
    if type not in ("font", "icon"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo invalido. Use 'font' ou 'icon'.",
        )

    sub_dir = "fonts" if type == "font" else "icons"
    dest_dir = os.path.join(uploads_dir, sub_dir)
    os.makedirs(dest_dir, exist_ok=True)

    file_path = os.path.join(dest_dir, unique_filename)
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    file_url = f"/uploads/{sub_dir}/{unique_filename}"

    logger.info("Font/Icon uploaded", type=type, filename=unique_filename, size=len(content))
    return {"url": file_url, "type": type}
```

- [ ] **Step 3: Atualizar main.py para criar diretório `uploads/icons/`**

Em `apps/api-postgres/app/main.py:112-113`, adicionar:

```python
fonts_dir = os.path.join(uploads_dir, "fonts")
icons_dir = os.path.join(uploads_dir, "icons")
os.makedirs(fonts_dir, exist_ok=True)
os.makedirs(icons_dir, exist_ok=True)
```

- [ ] **Step 4: Commit**

```bash
git add apps/api-postgres/app/routers/theme_router.py apps/api-postgres/app/main.py
git commit -m "feat(skins): endpoint unificado POST /v1/themes/fonts-icons/upload"
```

---

### Task 2: UI de importação de ícones no admin-skins

**Files:**
- Modify: `apps/frontend-webapp/modules/admin-skins/index.html:377`
- Modify: `apps/frontend-webapp/modules/admin-skins/script.js:467-471`

- [ ] **Step 1: Adicionar HTML da seção de importação de ícones**

Em `apps/frontend-webapp/modules/admin-skins/index.html`, após o `</fieldset>` da seção "Importar Fontes (ZIP)" (linha 377), adicionar:

```html
                   <!-- Importar Fonte de Icones -->
                   <fieldset class="form-section">
                       <legend>Importar Fonte de Icones</legend>
                       <div class="form-row">
                           <label for="iconFontName">Nome da Fonte de Icones</label>
                           <input type="text" id="iconFontName" placeholder="Ex: Material Icons">
                       </div>
                       <div class="form-row">
                           <label for="iconFontFile">Arquivo de fonte (.woff2, .ttf, .woff, .otf)</label>
                           <div class="upload-area" id="iconUploadArea">
                               <input type="file" id="iconFontFile" accept=".woff2,.ttf,.woff,.otf">
                               <div class="upload-preview" id="iconUploadPreview">
                                   <i class="fas fa-icons"></i>
                                   <span>Clique para selecionar um arquivo de fonte</span>
                               </div>
                           </div>
                       </div>
                       <div class="font-import-status" id="iconImportStatus"></div>
                       <button class="btn btn-sm btn-danger" id="btnRemoveIconFont" type="button" style="display:none;">
                           <i class="fas fa-trash"></i> Remover fonte de icones
                       </button>
                   </fieldset>
```

- [ ] **Step 2: Adicionar loading do icon font no editSkin()**

Em `apps/frontend-webapp/modules/admin-skins/script.js`, após o bloco de custom fonts (linha 470), adicionar:

```javascript
        const icons = fonts.icons || {};
        this.iconFont = icons.url ? { name: icons.name, url: icons.url, format: icons.format } : null;
        document.getElementById('iconFontName').value = icons.name || '';
        if (this.iconFont) {
            document.getElementById('btnRemoveIconFont').style.display = '';
            document.getElementById('iconUploadPreview').innerHTML = `<i class="fas fa-check-circle" style="color:var(--skin-success, #22c55e)"></i> <span>${icons.name || 'Fonte carregada'}</span>`;
        }
```

- [ ] **Step 3: Adicionar evento de upload de ícone**

No método `setupEvents()`, após os eventos de font zip, adicionar:

```javascript
        document.getElementById('iconFontFile')?.addEventListener('change', (e) => this.processIconFont(e));
        document.getElementById('btnRemoveIconFont')?.addEventListener('click', () => this.removeIconFont());
```

- [ ] **Step 4: Adicionar método processIconFont()**

Antes do `saveSkin()`, adicionar:

```javascript
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
```

- [ ] **Step 5: Inicializar `this.iconFont` no constructor**

```javascript
        this.customFonts = [];
        this.iconFont = null;
```

- [ ] **Step 6: Incluir iconFont no saveSkin()**

Em `apps/frontend-webapp/modules/admin-skins/script.js`, no objeto `data`, dentro da chave `fonts`, adicionar `icons`:

```javascript
            fonts: {
                heading: document.getElementById('fontHeading').value,
                body: document.getElementById('fontBody').value,
                custom: this.customFonts,
                icons: this.iconFont || null,
            },
```

- [ ] **Step 7: Aplicar preview de ícone no previewSkin()**

Em `previewSkin()`, após aplicar fontes, adicionar:

```javascript
        if (this.iconFont) {
            window.skinLoader._applyIconFont(this.iconFont);
        } else {
            window.skinLoader._removeIconFont();
        }
```

- [ ] **Step 8: Commit**

```bash
git add apps/frontend-webapp/modules/admin-skins/index.html apps/frontend-webapp/modules/admin-skins/script.js
git commit -m "feat(skins): UI de importacao de fonte de icones no admin-skins"
```

---

### Task 3: Aplicação da fonte de ícones no skinLoader.js

**Files:**
- Modify: `apps/frontend-webapp/shared/skinLoader.js:273`

- [ ] **Step 1: Adicionar método `_applyIconFont()`**

Em `apps/frontend-webapp/shared/skinLoader.js`, após o método `_applyFonts()` (linha 273), adicionar:

```javascript
    _applyIconFont(iconFont) {
        if (!iconFont || !iconFont.url) return;

        // Remove icone font anterior se existir
        const existing = document.getElementById('skin-icon-font');
        if (existing) existing.remove();

        const style = document.createElement('style');
        style.id = 'skin-icon-font';
        const format = iconFont.format || 'woff2';
        style.textContent = `@font-face { font-family: '${iconFont.name}'; src: url('${iconFont.url}') format('${format}'); font-display: swap; }`;
        document.head.appendChild(style);

        document.documentElement.style.setProperty('--skin-font-icons', `'${iconFont.name}'`);
    }

    _removeIconFont() {
        const existing = document.getElementById('skin-icon-font');
        if (existing) existing.remove();
        document.documentElement.style.removeProperty('--skin-font-icons');
    }
```

- [ ] **Step 2: Chamar _applyIconFont no _applySkin()**

Em `_applySkin()`, após `_applyFonts`, adicionar:

```javascript
        if (skin.fonts?.icons) {
            this._applyIconFont(skin.fonts.icons);
        } else {
            this._removeIconFont();
        }
```

- [ ] **Step 3: Commit**

```bash
git add apps/frontend-webapp/shared/skinLoader.js
git commit -m "feat(skins): aplicar fonte de icones via @font-face no skinLoader"
```

---

### Task 4: Injetar fonte de ícones nos iframes (dashboard.js)

**Files:**
- Modify: `apps/frontend-webapp/dashboard.js:505-518`

- [ ] **Step 1: Adicionar injecao de @font-face de icone no iframe**

Em `apps/frontend-webapp/dashboard.js`, no método `applySkinToIframe()`, após o bloco de custom fonts (linha 518), adicionar:

```javascript
        // Inject @font-face for icon font
        if (fonts.icons && fonts.icons.url) {
            const existingIcon = doc.getElementById('skin-icon-font-iframe');
            if (existingIcon) existingIcon.remove();

            const iconStyle = doc.createElement('style');
            iconStyle.id = 'skin-icon-font-iframe';
            const fmt = fonts.icons.format || 'woff2';
            iconStyle.textContent = `@font-face{font-family:'${fonts.icons.name}';src:url('${fonts.icons.url}')format('${fmt}');font-display:swap}`;
            doc.head.appendChild(iconStyle);
        }
```

- [ ] **Step 2: Commit**

```bash
git add apps/frontend-webapp/dashboard.js
git commit -m "feat(skins): injetar fonte de icones nos iframes dos modulos"
```

---

### Task 5: Verificar lint

- [ ] **Step 1: Rodar ruff**

No diretório `apps/api-postgres`:
```powershell
$env:PYTHONPATH='..\..\packages'; .\.venv\Scripts\python -m ruff check app/routers/theme_router.py app/main.py
```

Expected: sem erros.

- [ ] **Step 2: Se houver erros, corrigir e commitar**

```bash
git add -A
git commit -m "fix: corrigir lint apos implementacao de icones"
```
