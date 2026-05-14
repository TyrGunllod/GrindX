# Arquitetura do Portal Modular (Frontend)

Este documento descreve como funciona o sistema de "Micro-módulos" do SGI e como estender o portal.

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
const input = window.sgi.ui.createInput({
    label: 'Nome do Produto',
    id: 'nome',
    placeholder: 'Digite aqui...'
});
document.body.appendChild(input);
```

## 🔐 Autenticação nos Módulos

Os módulos têm acesso ao `localStorage` do domínio. Para realizar chamadas à API:
1. Recupere o token: `const token = localStorage.getItem('access_token');`
2. Envie no header: `Authorization: Bearer <token>`

---
Para criar um novo módulo:
1. Crie uma pasta em `packages/frontend-webapp/modules/nome-do-modulo/`.
2. Crie um `index.html` e um `script.js`.
3. Cadastre a URL no menu de **Gestão de Estrutura** dentro do portal.
