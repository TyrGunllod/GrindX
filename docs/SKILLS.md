# 🛠️ GrindX - Skills Necessárias

## 📊 Resumo de Skills por Funcionalidade

```
┌─────────────────────────────────────────────────────────────┐
│            SKILLS NECESSÁRIAS PARA GRINDX                   │
├─────────────────────────────────────────────────────────────┤
│ ✅ frontend-design    → Criar componentes web e interfaces   │
│ ✅ docx              → Gerar documentos Word                 │
│ ✅ pdf               → Manipular arquivos PDF                │
│ ✅ xlsx              → Gerenciar planilhas Excel             │
│ ✅ file-reading      → Ler/processar arquivos                │
│ ✅ pdf-reading       → Extrair dados de PDFs                 │
│ ⚠️  web-artifacts    → Criar artifacts avançados             │
│ ⚠️  skill-creator    → Criar/otimizar skills próprias        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Skills por Etapa do Projeto

### 1️⃣ **Desenvolvimento Frontend** 
**Skill: `frontend-design`**

#### 📍 Quando Usar
- Criar novos módulos visuais
- Projetar componentes React/Web
- Melhorar design system
- Implementar novo layout
- Criar dashboards e interfaces

#### 📚 Exemplos de Uso
```javascript
// Criar novo módulo com frontend-design
// 1. Ler SKILL.md de frontend-design
// 2. Criar componente React para o módulo structure
// 3. Usar Tailwind CSS baseado na paleta existente
// 4. Implementar responsividade e acessibilidade
```

#### 🎨 Recursos do frontend-design
- ✅ Design tokens e variáveis CSS
- ✅ Grid/Flexbox utilities
- ✅ Componentes reutilizáveis
- ✅ Temas dark/light mode
- ✅ Glassmorphism (já presente em core.css)
- ✅ Acessibilidade (WCAG)
- ✅ Tipografia e escala de cores

---

### 2️⃣ **Documentação e Relatórios**
**Skills: `docx`, `pdf`**

#### 📍 Quando Usar `docx`
- Criar guias de usuário em Word
- Gerar relatórios formatados
- Produzir templates de documentos
- Criar manuais de administração

#### 📍 Quando Usar `pdf`
- Extrair dados de PDFs para análise
- Criar relatórios em PDF
- Manipular formulários PDF
- Combinar múltiplos PDFs
- Adicionar watermarks

#### 📚 Exemplos de Uso
```python
# Gerar manual de usuário em DOCX
# 1. Ler SKILL.md de docx
# 2. Extrair estrutura do projeto
# 3. Criar documento Word com:
#    - Índice automático
#    - Imagens
#    - Tabelas de conteúdo
#    - Formatação profissional

# Exportar dados de relatório em PDF
# 1. Ler SKILL.md de pdf
# 2. Coletar dados da API
# 3. Gerar PDF com gráficos
# 4. Adicionar headers/footers
```

---

### 3️⃣ **Processamento de Dados**
**Skills: `xlsx`, `file-reading`, `pdf-reading`**

#### 📍 Quando Usar `xlsx`
- Importar dados via Excel
- Exportar relatórios em planilhas
- Criar templates de importação
- Gerar dashboard de dados

#### 📍 Quando Usar `file-reading`
- Processar arquivos do usuário
- Determinar tipo de arquivo
- Extrair conteúdo estruturado
- Validar formatos

#### 📍 Quando Usar `pdf-reading`
- Extrair tabelas de PDFs
- OCR em documentos escaneados
- Coletar dados de invoices
- Processar formulários

#### 📚 Exemplos de Uso
```python
# Importar usuários via Excel
# 1. User faz upload de .xlsx
# 2. file-reading identifica tipo
# 3. xlsx processa linhas e colunas
# 4. Validar com validation.js
# 5. Inserir no banco via API

# Extrair dados de nota fiscal (PDF)
# 1. Receber PDF
# 2. pdf-reading extrai tabelas
# 3. Normalizar dados
# 4. Importar no sistema
```

---

## 📋 Matriz de Skills × Funcionalidades

| Funcionalidade | Skill Principal | Skills Suporte |
|----------------|-----------------|-----------------|
| **Criar módulo novo** | frontend-design | - |
| **Design System** | frontend-design | - |
| **Componentes UI** | frontend-design | - |
| **Dashboard Visual** | frontend-design | - |
| **Guia de Usuário** | docx | file-reading |
| **Relatório Executivo** | docx | xlsx |
| **Exportar para PDF** | pdf | xlsx |
| **Importar Excel** | xlsx | file-reading |
| **Processar PDF** | pdf-reading | file-reading |
| **Validar Dados** | file-reading | - |
| **Criar Artifacts** | web-artifacts | frontend-design |
| **Otimizar Skills** | skill-creator | - |

---

## 🎨 **Skill: `frontend-design`**

### ✅ Aplicável Para
- Criar novo módulo `modules/structure/`
- Aprimorar componentes em `shared/components/`
- Redesenhar dashboard principal
- Implementar novos padrões de UI
- Criar landing page do projeto

### 🔧 Recursos Disponíveis

#### Design Tokens
```css
/* Disponível em shared/core.css */
--color-primary: #5D63F5
--color-success: #10B981
--color-warning: #F59E0B
--color-error: #EF4444
--spacing-sm: 8px
--spacing-md: 16px
--spacing-lg: 24px
--border-radius: 8px
--font-family: 'Inter', sans-serif
```

#### Componentes Básicos
- Buttons (primary, secondary, danger)
- Inputs (text, email, password)
- Cards com glassmorphism
- Modals acessíveis
- Data Tables
- Loading spinners
- Toast notifications

#### Funcionalidades
- ✅ Dark/Light mode automático
- ✅ Responsivo (mobile, tablet, desktop)
- ✅ WCAG AAA compliant
- ✅ Performance otimizada
- ✅ Glassmorphism effects

### 📖 Como Usar
```html
<!-- 1. Incluir design system -->
<link rel="stylesheet" href="../../shared/core.css">

<!-- 2. Usar componentes via UIFactory -->
<script src="../../shared/app.js"></script>

<!-- 3. Criar elementos programaticamente -->
<script>
const botao = window.grindx.ui.createButton({
    label: 'Salvar',
    type: 'primary',
    onClick: () => console.log('Clicado!')
});
document.body.appendChild(botao);
</script>
```

---

## 📄 **Skill: `docx`**

### ✅ Aplicável Para
- Gerar Manual do Usuário (doc profissional)
- Criar Guia de Administração
- Produzir Relatório de Requisitos
- Gerar Contratos de API
- Criar templates de propostas

### 📖 Como Usar

```python
# Criar guia de usuário do GrindX
# 1. Ler /mnt/skills/public/docx/SKILL.md
# 2. Extrair conteúdo de README e arquitetura
# 3. Estruturar com:
#    - Capa
#    - Índice automático
#    - Capítulos (Instalação, Uso, API)
#    - Apêndices
#    - Screenshots

# Exemplo de estrutura
document = Document()
document.add_heading('GrindX - Manual do Usuário', 0)
document.add_paragraph('...')
document.save('GRINDX-MANUAL.docx')
```

### Recursos
- ✅ Formatação avançada (headers, footers)
- ✅ Tabelas com estilos
- ✅ Imagens e figuras
- ✅ Índice automático (TOC)
- ✅ Números de página
- ✅ Estilos predefinidos
- ✅ Proteção de documento

---

## 📊 **Skill: `xlsx`**

### ✅ Aplicável Para
- Gerar template de importação de usuários
- Exportar relatório de transações
- Criar planilha de configuração
- Fazer backup de dados em Excel
- Gerar dashboard de KPIs

### 📖 Como Usar

```python
# Criar template de importação
# 1. Ler /mnt/skills/public/xlsx/SKILL.md
# 2. Definir colunas esperadas
# 3. Adicionar validação
# 4. Incluir exemplos

# Estrutura esperada:
usuarios.xlsx
├── Coluna A: nome (obrigatório)
├── Coluna B: email (obrigatório)
├── Coluna C: perfil (Admin/Operador)
├── Coluna D: status (Ativo/Inativo)
└── Exemplos de dados pré-preenchidos
```

### Recursos
- ✅ Múltiplas sheets
- ✅ Fórmulas e cálculos
- ✅ Validação de dados
- ✅ Formatação condicional
- ✅ Gráficos
- ✅ Congelamento de painéis

---

## 🔖 **Skill: `pdf`**

### ✅ Aplicável Para
- Gerar relatórios em PDF
- Extrair dados de PDFs
- Combinar múltiplos PDFs
- Criar certificados
- Gerar invoices

### 📖 Como Usar

```python
# Gerar relatório mensal em PDF
# 1. Ler /mnt/skills/public/pdf/SKILL.md
# 2. Coletar dados da API
# 3. Criar PDF com:
#    - Cabeçalho e rodapé
#    - Gráficos
#    - Tabelas
#    - Logo da empresa

# Exemplo:
from pypdf import PdfWriter
writer = PdfWriter()
writer.add_page(...)
writer.write('relatorio.pdf')
```

### Recursos
- ✅ Criação de novo PDF
- ✅ Extração de texto
- ✅ Manipulação de páginas
- ✅ Watermarks
- ✅ Fusão de arquivos
- ✅ Criptografia
- ✅ Preenchimento de formulários

---

## 📂 **Skill: `file-reading`**

### ✅ Aplicável Para
- Processar uploads do usuário
- Validar tipos de arquivo
- Extrair conteúdo de múltiplos formatos
- Preparar dados para importação
- Análise de arquivos

### 📖 Como Usar

```python
# Processar arquivo enviado
# 1. Ler /mnt/skills/public/file-reading/SKILL.md
# 2. Identificar tipo (csv, json, xlsx, pdf, txt)
# 3. Usar skill apropriada
# 4. Extrair dados estruturados
# 5. Validar conteúdo

# Fluxo:
arquivo → file-reading → tipo identificado
                      → skill específica (xlsx/pdf/etc)
                      → dados extraídos
                      → validação
                      → importação
```

### Recursos
- ✅ Detecção automática de tipo
- ✅ Extração de conteúdo
- ✅ Tratamento de erros
- ✅ Conversão de formatos
- ✅ Validação de estrutura

---

## 📰 **Skill: `pdf-reading`**

### ✅ Aplicável Para
- Extrair tabelas de PDFs
- OCR em documentos escaneados
- Processar notas fiscais
- Coletar dados de relatórios
- Análise de documentos

### 📖 Como Usar

```python
# Extrair dados de nota fiscal (PDF)
# 1. Ler /mnt/skills/public/pdf-reading/SKILL.md
# 2. Carregar PDF
# 3. Extrair:
#    - Tabelas (produtos, valores)
#    - Texto (CNPJ, data)
#    - Imagens (se necessário)
# 4. Estruturar dados
# 5. Validar informações

# Exemplo:
tabelas = extrair_tabelas_pdf('nota_fiscal.pdf')
para cada linha em tabelas:
    → produto, quantidade, valor
    → inserir no banco
```

### Recursos
- ✅ Extração de texto
- ✅ Extração de tabelas
- ✅ Extração de imagens
- ✅ OCR (texto de imagens)
- ✅ Análise estrutural

---

## 🌐 **Skill: `web-artifacts-builder`** (Opcional)

### ✅ Aplicável Para
- Criar artifacts Web interativos
- Dashboard com estado
- Ferramentas administrativas
- Visualizações complexas
- SPAs (Single Page Applications)

### 📖 Como Usar
```javascript
// Criar artifact avançado com múltiplos componentes
// 1. Ler /mnt/skills/examples/web-artifacts-builder/SKILL.md
// 2. Estruturar com:
//    - React components
//    - State management
//    - Routing
//    - shadcn/ui
// 3. Deploy como artifact interativo
```

---

## 🔧 **Skill: `skill-creator`** (Meta-skill)

### ✅ Aplicável Para
- Criar skills customizadas para GrindX
- Otimizar skills existentes
- Executar avaliações de skills
- Benchmark de performance
- Melhorar triggers

### 📖 Como Usar
```
Se precisar criar uma skill específica:
1. Ler /mnt/skills/examples/skill-creator/SKILL.md
2. Definir:
   - Nome e descrição
   - Triggers (quando usar)
   - Exemplos de uso
   - Recursos necessários
3. Criar arquivo SKILL.md
4. Registrar no projeto
```

---

## 📊 Mapa de Fluxo: Skills × Tarefas

```
┌─────────────────────────────────────────────────────┐
│ TAREFA: Criar Novo Módulo "Relatórios"            │
└─────────────────────────────────────────────────────┘
         ↓
    frontend-design ✅
    (criar UI com tokens)
         ↓
    modules/relatorios/index.html
    modules/relatorios/script.js
    modules/relatorios/style.css
         ↓
┌─────────────────────────────────────────────────────┐
│ TAREFA: Exportar Relatório em Excel               │
└─────────────────────────────────────────────────────┘
         ↓
    xlsx ✅
    (estrutura de planilha)
         ↓
    Arquivo Excel gerado
    Com formatação e validação
         ↓
┌─────────────────────────────────────────────────────┐
│ TAREFA: Gerar Manual em Word                      │
└─────────────────────────────────────────────────────┘
         ↓
    docx ✅
    (estrutura de documento)
         ↓
    frontend-design ✅
    (extrair screenshots)
         ↓
    GRINDX-MANUAL.docx
    Profissional e formatado
```

---

## ✅ Checklist de Skills para Iniciar

### Frontend Development
- [x] **frontend-design** ← Usar para criação de módulos
- [x] **web-artifacts-builder** ← Para dashboards interativos (opcional)

### Data Export
- [x] **docx** ← Para gerar guias e manuais
- [x] **pdf** ← Para relatórios em PDF
- [x] **xlsx** ← Para planilhas e exportações

### Data Import/Processing
- [x] **file-reading** ← Para validar uploads
- [x] **pdf-reading** ← Para processar documentos

### Meta (Opcional)
- [x] **skill-creator** ← Se precisar criar skills customizadas

---

## 🎯 Ordem de Prioridade

### 🔴 **Crítico** (Use AGORA)
1. ✅ **frontend-design** - Essencial para criar módulos
2. ✅ **file-reading** - Essencial para imports
3. ✅ **docx** - Documentação

### 🟡 **Importante** (Use em breve)
4. ✅ **xlsx** - Exportação de dados
5. ✅ **pdf** - Relatórios
6. ✅ **pdf-reading** - Processamento de docs

### 🟢 **Opcional** (Use conforme necessário)
7. ⚠️ **web-artifacts-builder** - Artifacts avançados
8. ⚠️ **skill-creator** - Skills customizadas

---

## 📚 Resumo: Como Usar as Skills

| Skill | Ler SKILL.md | Exemplo | Resultado |
|-------|-------------|---------|-----------|
| frontend-design | ✅ Sempre | Criar módulo | `modules/novo/` |
| docx | ✅ Sempre | Gerar manual | `MANUAL.docx` |
| xlsx | ✅ Sempre | Exportar dados | `relatorio.xlsx` |
| pdf | ✅ Sempre | Gerar PDF | `relatorio.pdf` |
| file-reading | ✅ Sempre | Validar upload | Dados extraídos |
| pdf-reading | ✅ Sempre | Extrair PDF | Dados estruturados |

---

## 🚀 Próximas Ações

1. **Para Criar Módulos**: Use `frontend-design`
2. **Para Gerar Documentação**: Use `docx` + `frontend-design`
3. **Para Exportar Dados**: Use `xlsx` ou `pdf`
4. **Para Processar Uploads**: Use `file-reading`
5. **Para Extrair de PDFs**: Use `pdf-reading`

---

**Recomendação:** Sempre ler o `SKILL.md` específico antes de usar cada skill!
