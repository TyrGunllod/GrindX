<!-- title: Arquitetura do Portal Modular — GrindX | updated: 2026-05-20 -->

# Arquitetura do Portal Modular (Frontend)

Este documento descreve o sistema de micro-módulos do GrindX e como estender o portal.

---

## Conceito Central

O Portal funciona como um **Shell (Host)**. Ele não contém a lógica de negócio das páginas, mas sim o "esqueleto" (Menu Lateral, Topbar, Autenticação).

O dashboard suporta dois modos de layout, configuráveis por empresa via tema:
- **sidebar** (padrão): menu lateral fixo à esquerda, viewport ao lado
- **topbar**: menu horizontal no topo, viewport ocupando largura total

A escolha do layout é persistida no banco (`company_themes.layout_mode`) e aplicada automaticamente pelo `skinLoader` ao carregar o tema ativo.

As páginas de negócio são carregadas dentro de um `<iframe>` no Viewport central. Isso garante:

1. **Isolamento de Erros:** Um erro em um módulo não derruba o portal inteiro
2. **Tecnologia Agnóstica:** Módulos podem ser HTML puro, React, Vue ou qualquer tecnologia que rode no navegador
3. **Desenvolvimento Standalone:** Cada módulo pode ser testado abrindo seu próprio `index.html` diretamente

---

## O Sistema Dinâmico

A árvore de navegação é definida no banco de dados através de duas entidades:

- **Aba:** Uma categoria no menu lateral (ex: "Logística")
- **Módulo:** Um item dentro da aba (ex: "Entrada de Estoque") que aponta para uma URL

O `dashboard.js` consome o endpoint `/v1/portal/menu` e renderiza os links em tempo real.

---

## Design System e UIFactory

Todos os módulos devem utilizar o pacote `shared` do frontend para manter consistência.

### 1. Core CSS (`shared/core.css`)

Contém variáveis de cores (Tokens), tipografia e utilitários de layout (Grid/Flex).

```html
<link rel="stylesheet" href="../../shared/core.css">
```

### 2. UI Factory (`shared/app.js`)

Sempre que precisar criar um elemento de interface (Input, Botão, Card), utilize a `UIFactory` via JavaScript. Isso garante que mudanças no design system se propaguem automaticamente.

```javascript
const input = window.grindx.ui.createInput({
    label: 'Nome do Produto',
    id: 'nome',
    placeholder: 'Digite aqui...'
});
document.body.appendChild(input);
```

### 3. Constantes (`shared/constants.js`)

Listas de domínio reutilizáveis: ícones, perfis de usuário e itens protegidos do portal.

```html
<script src="../../shared/constants.js"></script>
```

### 4. Componentes Compartilhados (`shared/components/`)

| Componente | Uso |
|------------|-----|
| `FormField.js` | Helpers para campos, selects e seletor de ícones |
| `ReusableModal.js` | Modal com foco, `Escape`, contenção de `Tab` |
| `DataTable.js` | Renderização de tabelas baseadas em colunas |
| `LoadingSpinner.js` | Estados de carregamento, vazio e toast |

```html
<script src="../../shared/components/FormField.js"></script>
<script src="../../shared/components/ReusableModal.js"></script>
<script src="../../shared/components/LoadingSpinner.js"></script>
<script src="../../shared/components/DataTable.js"></script>
```

Para validação client-side, use `shared/validation.js` e destaque erros inline antes de chamar a API.

---

## API e Autenticação nos Módulos

A URL base da API fica centralizada em `window.grindx.config.API_BASE_URL`, definida em `shared/app.js`.

Para mudar o ambiente, defina `window.GRINDX_CONFIG` antes de carregar `shared/app.js`:

```html
<script>
    window.GRINDX_CONFIG = {
        API_BASE_URL: 'https://api.exemplo.com/v1'
    };
</script>
<script src="../../shared/app.js"></script>
```

Para chamadas à API, use o serviço centralizado em `shared/apiService.js`. Ele monta URLs, aplica o token `Authorization: Bearer <token>` quando disponível, serializa JSON e padroniza erros.

```html
<script src="../../shared/app.js"></script>
<script src="../../shared/apiService.js"></script>
```

```javascript
const usuarios = await window.grindx.api.get('/usuarios');
await window.grindx.api.post('/usuarios', formData);
await window.grindx.api.request('/portal/abas', {
    method: 'POST',
    params: { nome, icone, ordem }
});
```

---

## Como Criar um Novo Módulo

1. Criar pasta em `packages/frontend-webapp/modules/nome-do-modulo/`
2. Criar `index.html` e `script.js`
3. Cadastrar a URL no menu de **Gestão de Estrutura** dentro do portal
