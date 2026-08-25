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
- **Descrever explicitamente cada botão e o que ele faz** (ex.: "Botão Salvar — grava o cadastro e fecha a janela."; "Botão Cancelar — descarta as alterações."). Nenhum botão visível pode ficar sem explicação.
- **Para cada modal/janela, descrever como preencher**, campo a campo, na ordem em que aparecem.

## Questionamentos antes de gerar

Antes de escrever o manual, **faça perguntas ao solicitante** para alinhar o escopo e melhorar a qualidade das respostas do agente. Faça **uma pergunta de cada vez** e aguarde a resposta.

Perguntas sugeridas (adapte ao contexto):

1. **Quais perguntas o manual deve responder?** Ex.: "o que faz o botão X?", "como preencher o cadastro?", "como faço para aprovar?", "onde vejo o saldo?". Isso define o que priorizar.
2. **Escopo:** o manual deve cobrir todas as telas/fluxos do módulo ou apenas alguns?
3. **Nível de detalhe:** objetivo e direto, ou passo a passo detalhado (campo a campo)?
4. **Público-alvo:** colaboradores iniciantes ou experientes? (ajusta tom e detalhamento)
5. **Prioridades:** há alguma tela, modal ou fluxo para destacar? Algum a omitir?
6. **Conteúdo existente:** já existe algum manual/texto do módulo para aproveitar ou ajustar?
7. **Tom:** formal, informal ou mais técnico de negócio?

Use as respostas para orientar a leitura do código e a escrita do manual.

## Passos

1. Detecte o contexto (monorepo ou standalone).
2. Identifique o módulo-alvo:
   - Monorepo: receba o `slug` (ex.: `users`, `home`, `configurar-agente`).
   - Standalone: leia o `module.json` para obter `module_name`/`menu_label` e liste as pastas em `frontend/`.
3. **Faça os questionamentos** (seção "Questionamentos antes de gerar") para alinhar escopo, perguntas a responder e nível de detalhe.
4. Leia o `index.html` e o `script.js` de cada aba/tela (e `style.css` apenas para confirmar o que é visual).
5. Identifique as funcionalidades de uso: cada tela, modal ou fluxo vira uma seção.
6. Escreva o manual no local correto:
   - Monorepo: `apps/agente-ia/manuals/<slug>.md`.
   - Standalone: **crie a pasta `manuals/` na raiz do standalone** (se não existir) e salve `manuals/<module_name>.md`.
7. **Revise com o solicitante** (seção "Ajustes e revisão do manual") e ajuste até a aprovação.

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
- Use subseções `###` para agrupar os campos de um formulário/modal (ex.: `### Dados Pessoais`).
- **Cada botão vira uma sub-seção `### Botão <Nome>`** com uma descrição focada e objetiva do que ele faz. Ex.:
  ```markdown
  ### Botão Salvar
  - **Salvar** — grava o novo usuário, fecha a janela e atualiza a tabela. Se um campo obrigatório estiver errado, exibe aviso e não fecha.
  ```
  Isso é essencial para o agente responder "o que faz o botão X?" — o título descritivo (`### Botão Salvar`) melhora a recuperação.
- **Explique o preenchimento** de cada modal: como abrir, e cada campo com o que deve ser informado.
- Mencione permissões visíveis ("disponível somente para administradores") quando relevante ao uso.
- Linguagem simples, direta e em português. Sem jargão técnico.

## Ajustes e revisão do manual

Após gerar o manual, **apresente um resumo ao solicitante e pergunte se deseja ajustes**. Objetivo: garantir que o manual responda bem às perguntas esperadas e tenha o texto adequado.

Pergunte (uma de cada vez):

- O manual cobre as perguntas que você esperava? Falta alguma tela, fluxo ou botão?
- Algum texto precisa ser ajustado (tom, clareza, nível de detalhe) para melhorar a resposta?
- Há algo a remover (ex.: conteúdo fora do escopo ou permissões irrelevantes)?

Ao receber o feedback:

1. Ajuste o manual no mesmo arquivo de saída (Monorepo: `apps/agente-ia/manuals/<slug>.md`; Standalone: `manuals/<module_name>.md`).
2. Releia o trecho ajustado para garantir que continua apenas na perspectiva do usuário final, sem detalhes técnicos.
3. Confirme com o solicitante se o ajuste atendeu, repetindo o ciclo até a aprovação.

**Lembre-se:** o manual alimenta o assistente de IA — o objetivo é que ele responda com precisão às perguntas que o solicitante indicar nos questionamentos.

## Saída

- **Monorepo:** `apps/agente-ia/manuals/<slug>.md`. Importar pelo módulo **Gestão → Configurar Agente**, selecionando o módulo correspondente (o mesmo `slug`).
- **Standalone:** `manuals/<module_name>.md` na raiz do projeto standalone. Depois, importar no GrindX pelo módulo **Gestão → Configurar Agente** (com o `slug`/`module_name` do módulo).
