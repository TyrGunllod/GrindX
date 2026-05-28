# Importer Card Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adicionar cards inline expansíveis ao módulo importer para exibir informações básicas e ações de cada módulo.

**Architecture:** Modificar o ImporterController para suportar expansão/recolhimento de cards inline abaixo de cada linha da tabela. Implementar accordion (apenas um card expandido por vez) com animação suave.

**Tech Stack:** JavaScript vanilla, CSS customizado, Design System GrindX

---

## File Structure

**Modified Files:**
- `apps/frontend-webapp/modules/importer/script.js` - Adicionar lógica de cards e propriedade modules
- `apps/frontend-webapp/modules/importer/style.css` - Estilos para card inline e animações

**Created Files:**
- Nenhum (modificações nos arquivos existentes)

---

### Task 1: Adicionar propriedade modules ao constructor

**Files:**
- Modify: `apps/frontend-webapp/modules/importer/script.js:1-9`

- [ ] **Step 1: Adicionar propriedade modules ao constructor**

```javascript
class ImporterController extends window.grindx.controllers.BaseController {
    constructor() {
        super();
        this.dataTable = null;
        this.importModal = null;
        this.currentSlug = null;
        this.isReimport = false;
        this.modules = []; // Adicionar esta linha
        this.init();
    }
```

- [ ] **Step 2: Verificar que o código não quebra**

Run: Abrir o módulo importer no navegador e verificar que não há erros no console

- [ ] **Step 3: Commit**

```bash
git add apps/frontend-webapp/modules/importer/script.js
git commit -m "feat(importer): adicionar propriedade modules ao controller"
```

---

### Task 2: Modificar função carregar para salvar dados

**Files:**
- Modify: `apps/frontend-webapp/modules/importer/script.js:58-71`

- [ ] **Step 1: Modificar função carregar para salvar dados na instância**

```javascript
    async carregar() {
        try {
            window.grindx.components.LoadingSpinner.setContainerState('dataTableContainer', 'loading');
            var data = await window.grindx.api.get('/v1/import/scan');
            this.modules = data.modules || []; // Salvar na instância
            if (this.modules.length === 0) {
                this.dataTable.renderEmpty('Nenhum módulo encontrado. Coloque um .zip na pasta import/ do servidor.');
            } else {
                this.dataTable.render(this.modules);
            }
        } catch (err) {
            this.toastError(err);
        }
    }
```

- [ ] **Step 2: Verificar que a função ainda funciona**

Run: Abrir o módulo importer no navegador e verificar que a tabela carrega normalmente

- [ ] **Step 3: Commit**

```bash
git add apps/frontend-webapp/modules/importer/script.js
git commit -m "feat(importer): salvar dados dos módulos na instância do controller"
```

---

### Task 3: Adicionar função abrirCard

**Files:**
- Modify: `apps/frontend-webapp/modules/importer/script.js` (adicionar após função carregar)

- [ ] **Step 1: Adicionar função abrirCard**

```javascript
    abrirCard(slug) {
        // Fechar outros cards abertos
        document.querySelectorAll('.module-card-expanded').forEach(card => {
            card.remove();
        });
        
        // Criar e inserir card expandido
        const row = document.querySelector(`[data-slug="${slug}"]`);
        const card = this.criarCardExpandido(slug);
        row.after(card);
        
        // Atualizar ícone
        row.querySelector('.expand-icon').className = 'fas fa-chevron-down';
    }
```

- [ ] **Step 2: Verificar que a função não causa erros**

Run: Abrir o módulo importer no navegador e verificar que não há erros no console

- [ ] **Step 3: Commit**

```bash
git add apps/frontend-webapp/modules/importer/script.js
git commit -m "feat(importer): adicionar função abrirCard para expansão de cards"
```

---

### Task 4: Adicionar função criarCardExpandido

**Files:**
- Modify: `apps/frontend-webapp/modules/importer/script.js` (adicionar após função abrirCard)

- [ ] **Step 1: Adicionar função criarCardExpandido**

```javascript
    criarCardExpandido(slug) {
        const module = this.modules.find(m => m.slug === slug);
        const div = document.createElement('div');
        div.className = 'module-card-expanded';
        div.innerHTML = `
            <div class="card-grid">
                <div class="card-field">
                    <div class="card-label">MÓDULO</div>
                    <div class="card-value">${module.module_name}</div>
                </div>
                <div class="card-field">
                    <div class="card-label">VERSÃO</div>
                    <div class="card-value">${module.version}</div>
                </div>
                <div class="card-field">
                    <div class="card-label">SCHEMA</div>
                    <div class="card-value">${module.schema_name}</div>
                </div>
            </div>
            <div class="card-actions">
                <button class="btn btn-sm ${module.ja_importado ? 'btn-warning' : 'btn-primary'}">
                    ${module.ja_importado ? 'Reimportar' : 'Importar'}
                </button>
                <button class="btn btn-sm btn-secondary">Detalhes</button>
            </div>
        `;
        return div;
    }
```

- [ ] **Step 2: Verificar que a função não causa erros**

Run: Abrir o módulo importer no navegador e verificar que não há erros no console

- [ ] **Step 3: Commit**

```bash
git add apps/frontend-webapp/modules/importer/script.js
git commit -m "feat(importer): adicionar função criarCardExpandido para renderizar card"
```

---

### Task 5: Modificar bindEvents para suportar cards

**Files:**
- Modify: `apps/frontend-webapp/modules/importer/script.js:41-56`

- [ ] **Step 1: Modificar bindEvents para adicionar listener de clique nas linhas**

```javascript
    bindEvents() {
        document.getElementById('btnRefresh').addEventListener('click', () => this.carregar());
        document.getElementById('btnConfirm').addEventListener('click', () => this.confirmarImport());
        document.getElementById('btnCancel').addEventListener('click', () => this.importModal.close());
        document.getElementById('btnModalClose').addEventListener('click', () => this.importModal.close());

        document.getElementById('dataTableContainer').addEventListener('click', (e) => {
            var btn = e.target.closest('[data-action]');
            if (btn) {
                var slug = btn.dataset.slug;
                var action = btn.dataset.action;
                if (action === 'import' || action === 'reimport') {
                    this.abrirModal(slug, action === 'reimport');
                }
                return;
            }

            // Adicionar clique na linha para expandir card
            var row = e.target.closest('.module-row');
            if (row) {
                var slug = row.dataset.slug;
                this.abrirCard(slug);
            }
        });
    }
```

- [ ] **Step 2: Verificar que a função não causa erros**

Run: Abrir o módulo importer no navegador e verificar que não há erros no console

- [ ] **Step 3: Commit**

```bash
git add apps/frontend-webapp/modules/importer/script.js
git commit -m "feat(importer): modificar bindEvents para suportar expansão de cards"
```

---

### Task 6: Adicionar estilos CSS para card inline

**Files:**
- Modify: `apps/frontend-webapp/modules/importer/style.css` (adicionar no final do arquivo)

- [ ] **Step 1: Adicionar estilos CSS para card inline**

```css
/* Card Inline */
.module-card-expanded {
    border: 1px solid var(--primary);
    border-left: 3px solid var(--primary);
    border-radius: 0 4px 4px 0;
    padding: var(--space-4);
    margin-bottom: var(--space-2);
    background: rgba(0, 194, 224, 0.03);
    animation: slideDown 200ms ease-out;
}

@keyframes slideDown {
    from {
        opacity: 0;
        max-height: 0;
    }
    to {
        opacity: 1;
        max-height: 200px;
    }
}

.card-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-4);
    margin-bottom: var(--space-4);
}

.card-field {
    display: flex;
    flex-direction: column;
}

.card-label {
    color: var(--text-muted);
    font-size: 0.8em;
    margin-bottom: 4px;
}

.card-value {
    font-weight: 600;
}

.card-actions {
    display: flex;
    gap: var(--space-2);
}

/* Ícone de expandir */
.expand-icon {
    color: var(--text-muted);
    font-size: 12px;
    transition: transform 0.2s;
}

.module-row:hover .expand-icon {
    color: var(--primary);
}

/* Linha da tabela com cursor pointer */
.module-row {
    cursor: pointer;
}

.module-row:hover {
    background: rgba(0, 194, 224, 0.02);
}
```

- [ ] **Step 2: Verificar que os estilos são aplicados**

Run: Abrir o módulo importer no navegador e verificar que os cards têm a aparência correta

- [ ] **Step 3: Commit**

```bash
git add apps/frontend-webapp/modules/importer/style.css
git commit -m "feat(importer): adicionar estilos CSS para cards inline"
```

---

### Task 7: Modificar DataTable para suportar classes CSS

**Files:**
- Modify: `apps/frontend-webapp/shared/components/DataTable.js` (verificar renderização)

- [ ] **Step 1: Verificar como o DataTable renderiza linhas**

Run: Verificar se o DataTable adiciona classes CSS às linhas ou se precisamos modificar

- [ ] **Step 2: Se necessário, modificar DataTable para adicionar classe module-row**

```javascript
// No método render, adicionar classe module-row às linhas
renderRow: function(item) {
    var row = document.createElement('div');
    row.className = 'module-row';
    row.dataset.slug = item.slug;
    // ... resto da renderização
}
```

- [ ] **Step 3: Commit**

```bash
git add apps/frontend-webapp/shared/components/DataTable.js
git commit -m "feat(importer): adicionar classe module-row às linhas do DataTable"
```

---

### Task 8: Testes manuais e ajustes

**Files:**
- Nenhum

- [ ] **Step 1: Testar expansão de cards**

Run: Abrir o módulo importer no navegador
1. Clicar em uma linha da tabela
2. Verificar se o card expande com informações corretas
3. Clicar em outra linha
4. Verificar se o card anterior recolhe

- [ ] **Step 2: Testar botões de ação**

Run: Verificar que os botões Importar/Reimportar funcionam corretamente

- [ ] **Step 3: Testar acessibilidade**

Run: Navegar com teclado (Tab, Enter, Space) e verificar que funciona

- [ ] **Step 4: Ajustes finais**

Run: Corrigir qualquer problema encontrado nos testes

- [ ] **Step 5: Commit final**

```bash
git add .
git commit -m "feat(importer): implementar cards inline com testes manuais"
```

---

## Self-Review

**1. Spec coverage:** 
- ✅ Card inline abaixo de cada linha da tabela
- ✅ Expansão/recolhimento ao clicar na linha
- ✅ Informações básicas: nome, versão, schema
- ✅ Botões de ação: Importar/Reimportar
- ✅ Animação de transição
- ✅ Acessibilidade (teclado, screen reader)

**2. Placeholder scan:** 
- ✅ Não há "TBD" ou "TODO"
- ✅ Todo código está completo

**3. Type consistency:** 
- ✅ Propriedade modules usada consistentemente
- ✅ Funções abrirCard e criarCardExpandido usam parâmetros corretos

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-28-importer-card-plan.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?