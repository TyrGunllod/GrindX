# Manual do Módulo Módulos & Abas

Este manual descreve como usar a tela **Estrutura do Portal** (também chamada de "Módulos & Abas"), onde você organiza as abas do menu lateral e os módulos do sistema. Aqui você cria, edita, exclui e organiza abas e módulos que aparecem no menu do GrindX.

> **Resumo das telas:**
> 1. Tela principal "Estrutura do Portal" — lista de abas e módulos.
> 2. Janela "Nova Aba / Editar Aba".
> 3. Janela "Novo Módulo / Editar Módulo".
> 4. Janela "Selecionar Módulo" (busca de arquivo de módulo).

---

## Tela Principal — Estrutura do Portal

É a primeira tela que você vê ao abrir o módulo. No topo há um cabeçalho com o título "Estrutura do Portal" e a descrição "Gerencie as abas do menu lateral e os módulos do sistema.".

Logo abaixo do título ficam dois botões de criação:

- **Nova Aba** — abre a janela para criar uma nova aba (grupo) no menu lateral.
- **Novo Módulo** — abre a janela para criar um novo módulo (item de menu) dentro de uma aba.

Na área central, o sistema mostra a estrutura em formato de **cartões organizados em árvore**:

- Cada **aba** aparece como um cartão com o seu ícone e nome.
- Abas dentro de outras abas (sub-abas) aparecem recuadas e com uma linha de destaque à esquerda.
- Cada **módulo** aparece listado dentro da sua aba, mostrando o nome, o caminho (URL) e a ordem.
- Os itens são exibidos ordenados pelo campo "Ordem".

Se não houver nada cadastrado, aparece a mensagem "Nenhuma estrutura cadastrada.".

### Ações em uma Aba (cartão)

Dentro de cada cartão de aba, há botões de ação:

- **Editar (ícone de lápis)** — abre a janela "Editar Aba" com os dados daquela aba preenchidos.
- **Excluir (ícone de lixeira)** — exclui a aba **e todos os seus módulos**. Antes de excluir, o sistema pede confirmação. *Obs.: este botão não aparece para abas protegidas do sistema.*

### Ações em um Módulo (item da lista)

Ao lado de cada módulo, há botões de ação:

- **Editar (ícone de caneta)** — abre a janela "Editar Módulo" com os dados daquele módulo preenchidos.
- **Excluir (ícone de lixeira)** — exclui o módulo. Antes de excluir, o sistema pede confirmação. *Obs.: este botão não aparece para módulos protegidos do sistema.*

### Permissões visíveis

- Abas e módulos considerados **protegidos** (essenciais para o sistema, como "Menu", "Gestão", "Usuários", "Módulos & Abas", "Dashboard", "Início") não mostram o botão de excluir. Se tentar excluir pela interface, o sistema avisa que o item é essencial e não pode ser removido.

---

## Janela — Nova Aba / Editar Aba

Esta janela serve para criar uma nova aba ou editar uma aba existente.

**Como abrir:**
- Para **criar**: clique em **Nova Aba** no topo da tela principal.
- Para **editar**: clique no ícone de **Editar (lápis)** do cartão da aba.

O título da janela muda conforme o caso: "Nova Aba" ou "Editar Aba".

### Campos

- **Nome da Aba** — texto que identifica a aba no menu. **Obrigatório.**
- **Ícone da Aba** — ícone exibido ao lado do nome no menu. Clique em um dos ícones da grade para selecionar; o ícone escolhido fica destacado e aparece uma prévia acima da grade.
- **Ordem** — número que define a posição da aba em relação às outras (menor número = aparece primeiro). Se deixar vazio, usa o padrão 0.
- **Sub-aba de (opcional)** — permite colocar esta aba dentro de outra aba (virar sub-aba). Selecione a aba "mãe" na lista, ou deixe em "Nenhuma (aba raiz)" para que seja uma aba principal.

### Botões

- **Cancelar** — fecha a janela sem salvar e descarta o que foi digitado.
- **Salvar Aba** — valida os campos e grava a aba (cria nova ou atualiza a existente). Em seguida atualiza a lista e o menu lateral.

Se algum campo obrigatório estiver vazio, ao clicar em **Salvar Aba** o campo é destacado e aparece a mensagem "Revise os campos destacados.".

---

## Janela — Novo Módulo / Editar Módulo

Esta janela serve para criar um novo módulo (item de menu) ou editar um já existente.

**Como abrir:**
- Para **criar**: clique em **Novo Módulo** no topo da tela principal.
- Para **editar**: clique no ícone de **Editar (caneta)** do módulo desejado.

O título da janela muda conforme o caso: "Novo Módulo" ou "Editar Módulo".

### Campos

- **URL do Arquivo** — caminho do arquivo do módulo (ex.: `modules/home/index.html`). **Obrigatório.** Ao lado do campo há o botão **Procurar módulo (pasta)** que abre a janela "Selecionar Módulo" para escolher um módulo já disponível.
- **Aba Destino** — a aba onde o módulo vai aparecer no menu. **Obrigatório.**
- **Nome do Módulo** — nome que aparece no menu. **Obrigatório.**
- **Ordem** — número que define a posição do módulo dentro da aba (menor número = aparece primeiro). Se deixar vazio, usa 0.
- **Identificador (Slug)** — código curto e único que identifica o módulo internamente. **Obrigatório**, com pelo menos 2 caracteres.
- **Perfil Mínimo** — perfil de acesso necessário para o usuário enxergar este módulo. Opções: **Leitura**, **Operador** (padrão) e **Administrador**.
- **Ícone do Módulo** — ícone exibido ao lado do nome no menu. Clique em um ícone da grade para selecionar. Padrão: cubo.

### Botões

- **Procurar módulo (pasta)** — abre a janela "Selecionar Módulo" para localizar e preencher automaticamente o arquivo, o nome e o identificador.
- **Cancelar** — fecha a janela sem salvar e descarta o que foi digitado.
- **Salvar Módulo** — valida os campos e grava o módulo (cria novo ou atualiza o existente). Em seguida atualiza a lista e o menu lateral.

Se um campo obrigatório estiver vazio ou inválido, ao clicar em **Salvar Módulo** o campo é destacado e aparece a mensagem "Revise os campos destacados.".

### Detalhes ao editar

Ao **editar** um módulo, os campos **URL do Arquivo**, **Identificador (Slug)** e **Ícone do Módulo** ficam bloqueados (somente leitura), pois identificam o módulo. Você pode alterar apenas **Nome**, **Aba Destino**, **Perfil Mínimo** e **Ordem**.

---

## Janela — Selecionar Módulo

Esta janela ajuda a localizar um módulo já disponível no sistema para vincular, sem precisar digitar o caminho do arquivo manualmente.

**Como abrir:**
- Na janela "Novo Módulo", clique no botão **Procurar módulo (pasta)**, ao lado do campo "URL do Arquivo".

### Como usar

1. A janela abre com a lista de módulos disponíveis. Cada item mostra o nome, o caminho (URL) e uma indicação de vínculo.
2. Use o campo **Buscar módulo...** no topo para filtrar a lista por nome ou caminho (a busca filtra enquanto você digita).
3. Cada item da lista pode ter duas situações:
   - **Não vinculado** — módulo ainda não está em nenhuma aba; pode ser escolhido (ícone de "mais").
   - **Vinculado em: (nome da aba)** — módulo que já está em uso em uma aba (ícone de "link").
4. Clique no item desejado. Ao escolher, o sistema preenche automaticamente no formulário "Novo Módulo" os campos **URL do Arquivo**, **Nome do Módulo** e **Identificador (Slug)**.

### Botões

- **Cancelar** — fecha a janela sem selecionar nada.
