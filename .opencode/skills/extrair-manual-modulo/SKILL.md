---
name: extrair-manual-modulo
description: Gera um manual de uso (Markdown) de um módulo do GrindX a partir do código frontend, descrevendo apenas como o usuário final utiliza o módulo — sem detalhes técnicos. Use quando precisar documentar como um módulo funciona para alimentar o Agente de IA (assistente de manuais).
---

# Extrair Manual de Uso de Módulo

## Objetivo

Gerar um **manual de usuário** em Markdown descrevendo **como usar** um módulo do GrindX, a partir da análise do código frontend. O manual alimenta o Agente de IA (assistente de manuais), por isso deve conter **apenas o que o usuário final precisa saber**.

## Regras de conteúdo (obrigatórias)

- **Somente a perspectiva do usuário final**: o que ele vê e faz em cada tela.
- **NÃO incluir** detalhes técnicos: código, endpoints, classes, funções, nomes de arquivos JS, variáveis, CSS, migrations, banco de dados.
- Focar em: telas, campos, botões, ações, fluxos, pré-requisitos de uso e permissões visíveis ao usuário.

## Onde está o código do módulo

`apps/frontend-webapp/modules/<slug>/`

- `index.html` — estrutura da tela (campos, botões, tabelas, modais, textos).
- `script.js` — comportamento e fluxos (ações, validações, mensagens).
- `style.css` — apenas layout; ignorar o conteúdo técnico (não vai para o manual).

## Passos

1. Receba o `slug` do módulo (ex.: `users`, `home`, `configurar-agente`).
2. Leia `index.html` e `script.js` (e `style.css` apenas para confirmar o que é visual).
3. Identifique as funcionalidades de uso: cada tela, modal ou fluxo vira uma seção.
4. Escreva o manual em `apps/agente-ia/manuals/<slug>.md`.

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
- Descreva ações em ordem: "Acesse o menu X", "Preencha o campo Y", "Clique em Salvar".
- Mencione permissões visíveis ("disponível somente para administradores") quando relevante ao uso.
- Linguagem simples, direta e em português. Sem jargão técnico.

## Saída

Salvar o manual em `apps/agente-ia/manuals/<slug>.md`.

Depois, importar pelo módulo **Gestão → Configurar Agente**, selecionando o módulo correspondente (o mesmo `slug`).
