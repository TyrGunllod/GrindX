# 📖 GrindX - Instruções Completas

## 🎯 Visão Geral do Projeto

**GrindX** é um **ERP Modular** construído com arquitetura moderna de **Monorepo**, focado em:
- ✅ Alta escalabilidade e performance
- ✅ Segurança robusta (JWT, RBAC)
- ✅ Experiência do usuário premium
- ✅ Desenvolvimento modular e isolado

---

## 🏗️ Arquitetura do Sistema

### 📦 Estrutura de Pastas

```
GrindX/
├── packages/
│   ├── api-postgres/          # API Principal (FastAPI + PostgreSQL)
│   ├── api-sqlserver/         # API Legada (SQL Server)
│   ├── frontend-webapp/       # Portal Shell + Micro-módulos
│   └── shared/                # Código compartilhado
├── Makefile                   # Automação de tasks
├── podman-compose.yml         # Orquestração de containers
└── README.md                  # Documentação principal
```

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos
- **Python 3.12+**
- **PostgreSQL 15+**
- **Node.js 18+** (opcional, para ferramentas)
- **Docker/Podman** (para containers)

### Instalação e Execução

#### 1️⃣ Instalar Dependências
```bash
make install
```

#### 2️⃣ Rodar a API PostgreSQL (Porta 8002)
```bash
make dev-postgres
```

#### 3️⃣ Rodar o Frontend (Porta 5500) - Em outro terminal
```bash
python -m http.server 5500 --directory packages/frontend-webapp
```

#### 4️⃣ Acessar o Portal
- **URL:** `http://localhost:5500`
- **Usuário:** `admin`
- **Senha:** `admin123`

---

## 🔐 Credenciais de Teste

| Usuário | Senha | Perfil | Permissões |
|---------|-------|--------|-----------|
| `admin` | `admin123` | Administrador | Acesso total |
| `operador` | `operador123` | Operador | Leitura e modificação |

---

## 📚 Frontend - Portal Modular

### 🎨 O Shell (Host)

O Portal funciona como um **Shell Orquestrador** que:
1. **Autentica o usuário** via JWT
2. **Carrega o menu dinâmico** do banco de dados (`/v1/portal/menu`)
3. **Renderiza módulos** em iframes isolados
4. **Mantém a navegação** consistente

### 🧩 Micro-módulos

Cada módulo é um projeto **standalone** que:
- Pode ser testado individualmente abrindo `index.html` no navegador
- Está isolado em uma `<iframe>` para evitar erros globais
- Usa a `UIFactory` para consistência visual
- Consome a API via `apiService.js`

#### Módulos Disponíveis

| Módulo | Local | Descrição |
|--------|-------|-----------|
| **Home** | `modules/home/` | Dashboard principal |
| **Users** | `modules/users/` | Gestão de usuários |
| **Structure** | `modules/structure/` | Administração de estrutura |

---

## 🛠️ Design System & UIFactory

### 📐 Componentes Compartilhados

Todos os módulos devem usar os recursos em `shared/`:

#### 1. **Core CSS** - Variáveis e Tokens
```html
<link rel="stylesheet" href="../../shared/core.css">
```
Contém:
- ✅ Tokens de cor (variáveis CSS)
- ✅ Tipografia (fonts, sizes)
- ✅ Utilitários de layout (Grid/Flex)
- ✅ Suporte Dark/Light Mode

#### 2. **UIFactory** - Criação Programática
```html
<script src="../../shared/app.js"></script>
```

Exemplo de uso:
```javascript
const input = window.grindx.ui.createInput({
    label: 'Nome do Produto',
    id: 'nome',
    placeholder: 'Digite aqui...'
});

const button = window.grindx.ui.createButton({
    label: 'Salvar',
    type: 'primary',
    onClick: handleSave
});

document.body.appendChild(input);
document.body.appendChild(button);
```

#### 3. **Componentes Reutilizáveis**

Importar em cada módulo:
```html
<script src="../../shared/components/FormField.js"></script>
<script src="../../shared/components/ReusableModal.js"></script>
<script src="../../shared/components/DataTable.js"></script>
<script src="../../shared/components/LoadingSpinner.js"></script>
```

---

## 🔌 Integração com API

### Base URL Centralizada

A URL base é definida em `shared/app.js`:
```javascript
window.grindx.config.API_BASE_URL = 'http://localhost:8002/v1'
```

Para mudar o ambiente, defina antes de carregar `app.js`:
```html
<script>
    window.GRINDX_CONFIG = {
        API_BASE_URL: 'https://api.producao.com/v1'
    };
</script>
<script src="../../shared/app.js"></script>
```

### Chamadas à API

Use o serviço centralizado em `apiService.js`:

```javascript
// GET
const usuarios = await window.grindx.api.get('/usuarios');

// POST
await window.grindx.api.post('/usuarios', {
    nome: 'João',
    email: 'joao@example.com'
});

// PUT
await window.grindx.api.put('/usuarios/1', dados);

// DELETE
await window.grindx.api.delete('/usuarios/1');

// Request customizado
await window.grindx.api.request('/portal/menu', {
    method: 'GET'
});
```

**Recursos:**
- ✅ Autenticação automática (Bearer Token)
- ✅ Tratamento padronizado de erros
- ✅ Serialização JSON automática
- ✅ Conversão de URLs baseada em config

---

## 🎯 Criando um Novo Módulo

### Passo 1: Criar a Estrutura
```bash
mkdir packages/frontend-webapp/modules/novo-modulo
cd packages/frontend-webapp/modules/novo-modulo
touch index.html script.js style.css
```

### Passo 2: Template Básico (`index.html`)

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Novo Módulo</title>
    
    <!-- Design System -->
    <link rel="stylesheet" href="../../shared/core.css">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div id="app"></div>
    
    <!-- API e Componentes -->
    <script src="../../shared/app.js"></script>
    <script src="../../shared/apiService.js"></script>
    <script src="../../shared/constants.js"></script>
    <script src="../../shared/validation.js"></script>
    <script src="../../shared/components/FormField.js"></script>
    <script src="../../shared/components/DataTable.js"></script>
    <script src="../../shared/components/LoadingSpinner.js"></script>
    
    <!-- Lógica do módulo -->
    <script src="script.js"></script>
</body>
</html>
```

### Passo 3: Lógica do Módulo (`script.js`)

```javascript
(async () => {
    const app = document.getElementById('app');
    const api = window.grindx.api;
    const ui = window.grindx.ui;

    // Carregar dados
    try {
        const dados = await api.get('/seu-endpoint');
        renderTabela(dados);
    } catch (erro) {
        app.innerHTML = `<p class="error">${erro.message}</p>`;
    }

    function renderTabela(dados) {
        const tabela = ui.createDataTable({
            columns: ['nome', 'email', 'status'],
            data: dados
        });
        app.appendChild(tabela);
    }
})();
```

### Passo 4: Estilo do Módulo (`style.css`)

```css
#app {
    padding: var(--spacing-lg);
    max-width: 1200px;
    margin: 0 auto;
}

.error {
    color: var(--color-error);
    padding: var(--spacing-md);
    border-radius: var(--border-radius);
    background: var(--color-error-bg);
}
```

### Passo 5: Registrar no Portal

1. Acesse **Gestão de Estrutura** no portal
2. Crie uma nova **Aba** (ex: "Relatórios")
3. Crie um **Módulo** com:
   - **Nome:** "Novo Módulo"
   - **URL:** `/modules/novo-modulo/index.html`
   - **Ícone:** (escolha um do sistema)

---

## 🎨 Paleta de Cores e Design

### Tokens CSS Disponíveis

```css
/* Cores Primárias */
--color-primary: #5D63F5
--color-primary-light: #8B91FF
--color-primary-dark: #4650D9

/* Estados */
--color-success: #10B981
--color-warning: #F59E0B
--color-error: #EF4444
--color-info: #3B82F6

/* Background */
--color-bg-primary: #FFFFFF
--color-bg-secondary: #F9FAFB
--color-text-primary: #111827
--color-text-secondary: #6B7280

/* Efeitos */
--color-glassmorphism: rgba(255, 255, 255, 0.25)
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05)
--shadow-lg: 0 20px 25px rgba(0, 0, 0, 0.1)
```

### Modo Dark/Light

Muda automaticamente com `prefers-color-scheme`:
```css
@media (prefers-color-scheme: dark) {
    :root {
        --color-bg-primary: #1F2937;
        --color-text-primary: #F9FAFB;
    }
}
```

---

## 🔄 Fluxo de Desenvolvimento

### 1. **Desenvolvimento Local**
- Abra `modules/seu-modulo/index.html` diretamente no navegador
- Teste sem rodar o portal inteiro
- Use o DevTools do navegador

### 2. **Teste no Portal**
- Registre a URL do módulo na **Gestão de Estrutura**
- Verifique se carrega dentro da iframe
- Teste a autenticação e permissões

### 3. **Build & Deploy**
- Use o Makefile para automatizar
- Sempre versionar com Git
- Fazer commit e push após testes

---

## 🐛 Troubleshooting

### Módulo não carrega na iframe
- ✅ Verifique a URL registrada no menu
- ✅ Abra o DevTools e veja se há CORS errors
- ✅ Certifique-se que o arquivo `index.html` existe

### Erro de autenticação
- ✅ Faça login novamente no portal
- ✅ Verifique se o token está em `localStorage`
- ✅ Confirme que a API retorna um token válido

### Componentes não aparecem
- ✅ Certifique-se que `shared/app.js` foi carregado
- ✅ Verifique se `UIFactory` está inicializado
- ✅ Abra o console e procure por erros

### API retorna erro 404
- ✅ Confirme que a API está rodando
- ✅ Verifique a porta (padrão: 8002)
- ✅ Teste manualmente com `curl` ou Postman

---

## 📚 Recursos Adicionais

| Recurso | Local |
|---------|-------|
| **Arquitetura** | `/packages/frontend-webapp/ARCHITECTURE_PORTAL.md` |
| **README Principal** | `/README.md` |
| **Makefile** | `/Makefile` |
| **Componentes** | `/packages/frontend-webapp/shared/components/` |
| **Constantes** | `/packages/frontend-webapp/shared/constants.js` |

---

## 💡 Boas Práticas

✅ Sempre use a `UIFactory` para componentes  
✅ Valide dados client-side antes de enviar à API  
✅ Use `LoadingSpinner` durante requisições assíncronas  
✅ Implemente tratamento de erros adequado  
✅ Faça commits frequentes com mensagens claras  
✅ Teste modules isoladamente antes de adicionar ao portal  
✅ Mantenha o código limpo e bem documentado  

---

**Desenvolvido com ❤️ seguindo SOLID, Clean Code e Performance**
