# Arquitetura do Portal Modular (Frontend)

Este documento descreve como funciona o sistema de "Micro-módulos" do GrindX e como estender o portal.

## 📐 Conceito Central

O Portal funciona como um **Shell (Host)**. Ele não contém a lógica de negócio das páginas, mas sim o "esqueleto" (Menu Lateral, Topbar, Autenticação).

As páginas de negócio são carregadas dentro de um `<iframe>` no Viewport central. Isso garante:
1.  **Isolamento de Erros:** Um erro em um módulo não derruba o portal inteiro.
2.  **Tecnologia Agnóstica:** Você pode ter módulos em HTML Puro, React, Vue ou qualquer outra tecnologia, desde que rodem no navegador.
3.  **Desenvolvimento Standalone:** Cada módulo pode ser testado abrindo o seu próprio arquivo `index.html` diretamente.

## 🛠️ O Sistema Dinâmico

A árvore de navegação é definida no banco de dados através de duas entidades:
- **Aba:** Uma categoria no menu lateral (ex: "Logística").
- **Módulo:** Um item dentro da aba (ex: "Entrada de Estoque") que aponta para uma URL.

O `dashboard.js` consome o endpoint `/v1/portal/menu` e renderiza os links em tempo real.

## 🎨 Design System & UIFactory

Para manter a consistência, todos os módulos devem utilizar o pacote `shared` do frontend:

### 1. Core CSS (`shared/core.css`)
Contém todas as variáveis de cores (Tokens), tipografia e utilitários de layout (Grid/Flex).
```html
<link rel="stylesheet" href="../../shared/core.css">
```

### 2. UI Factory (`shared/app.js`)
Sempre que precisar criar um elemento de interface (Input, Botão, Card), utilize a `UIFactory` via JavaScript. Isso garante que se mudarmos o design do sistema, todos os módulos se atualizem automaticamente.

Exemplo de uso:
```javascript
const input = window.grindx.ui.createInput({
    label: 'Nome do Produto',
    id: 'nome',
    placeholder: 'Digite aqui...'
});
document.body.appendChild(input);
```

### 3. Constantes e Componentes Compartilhados

Use `shared/constants.js` para listas de domínio reutilizáveis, como ícones, perfis de usuário e itens protegidos do portal.

```html
<script src="../../shared/constants.js"></script>
```

Componentes compartilhados ficam em `shared/components/`:
- `FormField.js`: helpers para campos, selects e seletor de ícones.
- `ReusableModal.js`: abertura/fechamento de modal com foco inicial, restauração de foco, `Escape` e contenção de `Tab`.
- `DataTable.js`: renderização simples de tabelas baseadas em colunas.
- `LoadingSpinner.js`: estados de carregamento, vazio e toast.

```html
<script src="../../shared/components/FormField.js"></script>
<script src="../../shared/components/ReusableModal.js"></script>
<script src="../../shared/components/LoadingSpinner.js"></script>
<script src="../../shared/components/DataTable.js"></script>
```

Para validação client-side, use `shared/validation.js` e destaque erros inline antes de chamar a API.

## 🔐 API e Autenticação nos Módulos

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

Para realizar chamadas à API, use o serviço centralizado em `shared/apiService.js`. Ele monta URLs, aplica o token `Authorization: Bearer <token>` quando disponível, serializa JSON e padroniza erros.

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
Para criar um novo módulo:
1. Crie uma pasta em `packages/frontend-webapp/modules/nome-do-modulo/`.
2. Crie um `index.html` e um `script.js`.
3. Cadastre a URL no menu de **Gestão de Estrutura** dentro do portal.
