---
name: extrair-manual-modulo
description: Gera um manual de uso (Markdown) de um módulo do GrindX a partir do código frontend, descrevendo apenas como o usuário final utiliza o módulo — sem detalhes técnicos. Funciona tanto no monorepo GrindX quanto em módulos standalone. Use quando precisar documentar como um módulo funciona para alimentar o Agente de IA (assistente de manuais).
---

# Extrair Manual de Uso de Módulo

## Objetivo

Gerar um **manual de usuário** em Markdown descrevendo **como usar** um módulo do GrindX, a partir da análise do código frontend. O manual alimenta o Agente de IA (assistente de manuais), por isso deve conter **apenas o que o usuário final precisa saber**.

## Contexto de execução (detectar ANTES de começar)

A skill funciona em dois contextos. Identifique qual se aplica antes de ler ou escrever qualquer arquivo.

### 1. Monorepo GrindX

Aplicável quando a pasta `apps/frontend-webapp/modules/` (ou `apps/agente-ia/`) existe na raiz do repositório.

- **Código do módulo:** `apps/frontend-webapp/modules/<slug>/`
  - `index.html` — estrutura da tela (campos, botões, tabelas, modais, textos).
  - `script.js` — comportamento e fluxos (ações, validações, mensagens).
  - `style.css` — apenas layout; ignorar o conteúdo técnico.
- **Saída:** `apps/agente-ia/manuals/<slug>.md`

### 2. Módulo standalone (fora do GrindX)

Aplicável quando há `module.json` e a pasta `frontend/` na raiz do projeto standalone (estrutura criada pela skill `create-standalone-module`).

- **Código do módulo:** `frontend/<prefix>_<tab>/` — uma pasta por aba, cada uma com `index.html`, `script.js` e `style.css`.
- **Nome do módulo:** campo `module_name` do `module.json` (use `menu_label` como título amigável do manual, se existir).
- **Saída:** criar a pasta `manuals/` na **raiz do projeto standalone** e salvar `manuals/<module_name>.md`.

## Regras de conteúdo (obrigatórias)

- **Somente a perspectiva do usuário final**: o que ele vê e faz em cada tela.
- **NÃO incluir** detalhes técnicos: código, endpoints, classes, funções, nomes de arquivos JS, variáveis, CSS, migrations, banco de dados.
- Focar em: telas, campos, botões, ações, fluxos, pré-requisitos de uso e permissões visíveis ao usuário.

## Passos

1. Detecte o contexto (monorepo ou standalone).
2. Identifique o módulo-alvo:
   - Monorepo: receba o `slug` (ex.: `users`, `home`, `configurar-agente`).
   - Standalone: leia o `module.json` para obter `module_name`/`menu_label` e liste as pastas em `frontend/`.
3. Leia o `index.html` e o `script.js` de cada aba/tela (e `style.css` apenas para confirmar o que é visual).
4. Identifique as funcionalidades de uso: cada tela, modal ou fluxo vira uma seção.
5. Escreva o manual no local correto:
   - Monorepo: `apps/agente-ia/manuals/<slug>.md`.
   - Standalone: **crie a pasta `manuals/` na raiz do standalone** (se não existir) e salve `manuals/<module_name>.md`.

## Estrutura do manual

```markdown
# Manual do Módulo <Nome>

## <Tela ou Funcionalidade>
<descrição passo a passo do que o usuário faz>

## <Outra Funcionalidade>
...
```

## Diretrizes de escrita

- Título H1 = `# Manual do Módulo <Nome>` (nome exibido ao usuário, ex.: "Usuários", "Estoque").
- Uma seção `##` por tela/funcionalidade (não por campo individual).
- Em standalone, cada aba do `frontend/` vira uma seção `##` (ou subseções, se a aba tiver várias funcionalidades).
- Descreva ações em ordem: "Acesse o menu X", "Preencha o campo Y", "Clique em Salvar".
- Mencione permissões visíveis ("disponível somente para administradores") quando relevante ao uso.
- Linguagem simples, direta e em português. Sem jargão técnico.

## Saída

- **Monorepo:** `apps/agente-ia/manuals/<slug>.md`. Importar pelo módulo **Gestão → Configurar Agente**, selecionando o módulo correspondente (o mesmo `slug`).
- **Standalone:** `manuals/<module_name>.md` na raiz do projeto standalone. Depois, importar no GrindX pelo módulo **Gestão → Configurar Agente** (com o `slug`/`module_name` do módulo).
