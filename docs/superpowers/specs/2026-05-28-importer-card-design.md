# Design: Cards de Ação por Módulo no Importer

## Visão Geral

Adicionar cards inline expansíveis ao módulo `importer` para exibir informações básicas e ações de cada módulo, mantendo a tabela como estrutura principal.

## Objetivo

- Melhorar a experiência do usuário ao interagir com módulos
- Fornecer acesso rápido a informações e ações
- Manter a funcionalidade existente da tabela

## Escopo

### Incluído
- Card inline abaixo de cada linha da tabela
- Expansão/recolhimento ao clicar na linha
- Informações básicas: nome, versão, schema
- Botões de ação: Importar/Reimportar
- Animação de transição
- Acessibilidade (teclado, screen reader)

### Não incluído
- Log de importação (futuro)
- Configurações avançadas
- Múltiplos cards expandidos simultaneamente

## Design

### Estrutura do Card

```
┌─────────────────────────────────────────────────────────────┐
│ Linha da Tabela (colapsada)                                 │
│ [▼] modulo-exemplo v1.0.0           Importado    schema: public │
├─────────────────────────────────────────────────────────────┤
│ Card Expandido                                              │
│ ┌─────────────┬─────────────┬─────────────┐                │
│ │ MÓDULO      │ VERSÃO      │ SCHEMA      │                │
│ │ nome-mod    │ 1.0.0       │ public      │                │
│ └─────────────┴─────────────┴─────────────┘                │
│ [Reimportar] [Detalhes]                                     │
└─────────────────────────────────────────────────────────────┘
```

### Comportamento

1. **Expansão**: Clique em qualquer lugar da linha expande o card
2. **Ícone de seta**: Indica estado (▼ expandido, ► recolhido)
3. **Accordion**: Apenas um card expandido por vez
4. **Animação**: Transição suave de 200ms

### Conteúdo

- **Informações básicas**: Grid 3 colunas (módulo, versão, schema)
- **Botão primário**: Importar (azul) ou Reimportar (amarelo)
- **Botão secundário**: Detalhes (para futuras expansões)

### Acessibilidade

- **Teclado**: Tab para navegar, Enter/Space para expandir
- **Screen reader**: `aria-expanded`, `aria-controls`
- **Touch**: Área de clique mínima 44px

## Implementação

### Arquivos a modificar

1. **`apps/frontend-webapp/modules/importer/script.js`**
   - Adicionar lógica de expansão/recolhimento
   - Implementar accordion (apenas um expandido)
   - Adicionar renderização do card

2. **`apps/frontend-webapp/modules/importer/style.css`**
   - Estilos para card inline
   - Animações de transição
   - Estados hover/focus

3. **`apps/frontend-webapp/modules/importer/index.html`**
   - Nenhuma alteração necessária (card é renderizado via JS)

### Detalhes Técnicos

#### JavaScript

```javascript
// Adicionar ao ImporterController
// Propriedade para armazenar dados dos módulos
constructor() {
    super();
    this.dataTable = null;
    this.importModal = null;
    this.currentSlug = null;
    this.isReimport = false;
    this.modules = []; // Adicionar esta linha
    this.init();
}

// Modificar função carregar para salvar dados
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

// Novas funções para cards
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

#### CSS

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
```

## Testes

### Casos de Teste

1. **Expansão**: Clique na linha expande o card
2. **Recolhimento**: Clique novamente recolhe
3. **Accordion**: Expandir um fecha os outros
4. **Ações**: Botões Importar/Reimportar funcionam
5. **Teclado**: Tab e Enter/Space funcionam
6. **Screen reader**: aria-expanded atualizado

### Comando de Teste

```bash
# Testes existentes
make test-postgres

# Testes manuais
# 1. Abrir módulo importer
# 2. Clicar em uma linha da tabela
# 3. Verificar se card expande
# 4. Clicar em outra linha
# 5. Verificar se card anterior recolhe
```

## Referências

- Design System: `apps/frontend-webapp/shared/core.css`
- Componentes: `apps/frontend-webapp/shared/components/`
- Módulo: `apps/frontend-webapp/modules/importer/`