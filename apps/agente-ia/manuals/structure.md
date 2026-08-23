# Manual do Módulo Módulos & Abas

## Visão Geral do Módulo

O módulo **Módulos & Abas** (tela "Estrutura do Portal") é o lugar onde você organiza o **menu lateral do sistema**. Ele serve para duas coisas principais:

1. **Criar, editar e excluir abas** — as "pastas" do menu lateral (por exemplo: "Gestão", "Relatórios", "Configurações").
2. **Criar, editar e excluir módulos** — os itens que ficam DENTRO de cada aba (por exemplo: "Módulos & Abas", "Usuários", "Dashboard").

**Como pensar nisso:** as abas são as pastas do menu, e os módulos são os arquivos dentro dessas pastas. Uma aba pode até ter **sub-abas** (abas dentro de abas), formando uma árvore de menu.

Tudo que você alterar aqui **atualiza o menu lateral automaticamente**, ou seja, você não precisa sair e entrar de novo para ver as mudanças.

> **Importante:** este módulo em si é um item protegido do sistema e não pode ser excluído. As abas e módulos "essenciais" (explicados mais abaixo) também têm proteção.

---

## Tela Principal — Estrutura do Portal

Quando você abre o módulo, vê a tela principal com os seguintes elementos:

### Cabeçalho da página
- **Título:** "Estrutura do Portal"
- **Selo de versão:** no topo, ao lado do título, aparece a versão do sistema (apenas informativo).
- **Subtítulo:** "Gerencie as abas do menu lateral e os módulos do sistema." — resume o que você pode fazer aqui.

### Botão "Nova Aba"
- **Onde:** no topo, do lado direito, primeiro botão (ícone de **pasta com +**).
- **O que faz:** abre a janela (modal) para você **criar uma nova aba** no menu lateral.
- **Quando usar:** quando você precisa de uma nova "pasta" no menu (ex.: criar a aba "Financeiro").
- **Dica:** em telas pequenas (celular), o texto "Nova Aba" some e fica só o ícone.

### Botão "Novo Módulo"
- **Onde:** no topo, do lado direito, segundo botão (ícone de **símbolo de +**).
- **O que faz:** abre a janela (modal) para você **criar um novo módulo** dentro de uma aba.
- **Quando usar:** quando o módulo que você quer colocar no menu **ainda não existe** (você vai preencher tudo na mão, campo por campo).
- **Dica:** se o módulo já existe no sistema, é mais rápido usar o botão de "procurar" dentro da janela de módulo (veja a seção da janela de módulo abaixo).

### A área de estrutura (lista de abas e módulos)
Logo abaixo dos botões, o sistema carrega ("Carregando estrutura...") e mostra a organização atual do menu. A estrutura aparece como uma **lista de cartões**, um para cada aba. Dentro de cada cartão ficam os módulos e as sub-abas.

**Cartão de uma aba (raiz ou sub-aba):**
- **Nome da aba** com o ícone escolhido na frente (ex.: 🗂️ Gestão).
- **Botão de editar** (ícone de **lápis**) → abre a janela para editar a aba.
- **Botão de excluir** (ícone de **lixeira**) → apaga a aba e tudo que tem dentro dela.
- **Módulos:** cada módulo aparece como uma linha com o **nome**, o **endereço (URL)** e a **ordem** (ex.: "Ordem: 1"). Do lado direito da linha do módulo ficam os botões de **editar** (caneta) e **excluir** (lixeira).
- **Sub-abas:** aparecem logo abaixo da aba pai, **recuadas para a direita** com uma linha vertical colorida na borda esquerda, para você entender que ela é filha de outra aba.

**Regras de exibição dos botões de excluir (lixeira):**
- O botão de excluir **não aparece** em abas ou módulos **protegidos** (essenciais). Nesses casos, só fica visível o lápis de edição.
- Se uma aba é protegida, os módulos dentro dela também não podem ser excluídos (o botão some).

**Mensagens possíveis na área da estrutura:**
- **"Nenhuma estrutura cadastrada."** → ainda não existe nenhuma aba no sistema.
- **Mensagem de erro** (ícone de **triângulo com exclamação**) → houve problema ao carregar a estrutura (ex.: sem conexão). Nesse caso, recarregue a página ou tente novamente.

### Ícones de ação (botões por ícone)

| Ícone | Nome | O que faz |
|-------|------|-----------|
| 🖍️ (lápis, `edit`) | Editar | Abre a janela para alterar a aba correspondente. |
| 🗑️ (lixeira, `trash`) | Excluir | Apaga a aba (e seus módulos) após confirmação. Só aparece em itens não protegidos. |
| ✏️ (caneta, `pen`) | Editar módulo | Abre a janela para alterar o módulo. |
| 🗑️ (lixeira, `trash`) | Excluir módulo | Apaga o módulo após confirmação. Só aparece em itens não protegidos. |
| ➕ (pasta +) | Nova Aba | Abre a janela para criar uma aba. |
| ➕ (+) | Novo Módulo | Abre a janela para criar um módulo manualmente. |

---

## Janela "Nova Aba" / "Editar Aba"

**Como abrir:**
- Para **criar**: clique no botão **"Nova Aba"** do topo.
- Para **editar**: clique no ícone de **lápis (editar)** no cartão da aba desejada.

**O que é:** é uma janela flutuante (modal) no centro da tela. O título da janela muda conforme a ação: **"Nova Aba"** para criar e **"Editar Aba"** para editar. Quando você edita, os campos já vêm preenchidos com os dados atuais da aba.

> **Dica:** para fechar a janela sem salvar, clique em "Cancelar" ou aperte a tecla `Esc`. Ao fechar, os formulários são limpos.

### Campos da janela (preencha um por um)

#### Nome da Aba (obrigatório)
- **O que é:** o nome que aparecerá no menu lateral.
- **Como preencher:** digite um nome curto e claro, como "Gestão", "Relatórios" ou "Financeiro".
- **Regra:** é obrigatório. Se você tentar salvar sem preencher, o campo fica destacado em vermelho e aparece a mensagem "Informe o nome da aba."

#### Ordem (número)
- **O que é:** a posição da aba no menu lateral. Número menor = aparece mais acima.
- **Como preencher:** digite um número inteiro (ex.: 0, 1, 2, 3...).
- **Padrão:** se deixar em branco, o valor usado é **0**.
- **Regra:** se digitar algo que não é número, o sistema avisa para informar um número válido.

#### Ícone da Aba
- **O que é:** o ícone que fica ao lado do nome da aba no menu.
- **Como preencher:** abaixo do rótulo aparece o ícone escolhido em tamanho grande (prévia) e, logo abaixo, uma **grade de ícones** organizada em categorias: Coding, Devices, Design, Files, Users, Alert, Business, Charts, Communication, Editing, Logistics e Maps. **Clique em um ícone** para escolhê-lo — o ícone selecionado fica com a borda colorida (azul). A grade tem rolagem própria para você ver todos os ícones.
- **Padrão:** pasta (`fas fa-folder`).

#### Sub-aba de (opcional)
- **O que é:** se você quiser que esta aba fique **dentro de outra aba** (vire uma sub-aba), escolhe aqui a aba "mãe".
- **Como preencher:** abra a lista e escolha a aba pai. As opções são só as abas "raiz" (que não são sub-aba de ninguém).
- **Deixar em branco:** a opção **"Nenhuma (aba raiz)"** fica marcada por padrão — a aba vira raiz do menu.
- **Regra:** opcional. Se não escolher nada, a aba será do primeiro nível do menu.

### Botões da janela

| Botão | O que faz |
|-------|-----------|
| **Cancelar** | Fecha a janela sem salvar nada. |
| **Salvar Aba** | Valida os campos e salva a aba. Se der certo, aparece a mensagem **"Aba salva com sucesso."** e o menu lateral é atualizado na hora. Se algum campo estiver errado, aparece o aviso "Revise os campos destacados." |

### Fluxo passo a passo — Criar uma aba
1. Clique em **"Nova Aba"**.
2. Em **Nome da Aba**, digite o nome (ex.: "Financeiro").
3. Em **Ordem**, digite a posição desejada (ex.: 2).
4. Em **Ícone da Aba**, clique no ícone que você quer (ex.: ícone de moedas).
5. Em **Sub-aba de**, escolha a aba pai (ou deixe em "Nenhuma" para ser raiz).
6. Clique em **"Salvar Aba"**.
7. Pronto! A nova aba aparece na estrutura e no menu lateral.

### Fluxo passo a passo — Editar uma aba
1. Clique no ícone de **lápis** no cartão da aba.
2. Altere os campos que quiser (nome, ordem, ícone ou aba pai).
3. Clique em **"Salvar Aba"**.
4. Confirme as mudanças na estrutura e no menu lateral.

### Fluxo passo a passo — Excluir uma aba
1. Clique no ícone de **lixeira** no cartão da aba.
2. O sistema pergunta: **"Excluir esta aba e todos os seus módulos?"** — clique em **OK** para confirmar ou **Cancelar** para desistir.
3. Depois de confirmar, a aba **e todos os módulos dentro dela** são apagados. Aparece a mensagem **"Aba excluída com sucesso."** e o menu é atualizado.
4. **Atenção:** essa ação não tem desfazer — só exclua se tiver certeza.
5. Se a aba for **protegida**, o botão de lixeira nem aparece, e o sistema avisa: *"A aba 'X' é essencial para o sistema e não pode ser excluída."*

---

## Janela "Novo Módulo" / "Editar Módulo"

**Como abrir:**
- Para **criar**: clique no botão **"Novo Módulo"** do topo.
- Para **editar**: clique no ícone de **caneta** na linha do módulo desejado.

**O que é:** janela flutuante (modal) para criar ou alterar um módulo. O título muda: **"Novo Módulo"** ou **"Editar Módulo"**. Ao editar, os campos já vêm preenchidos.

> **Importante (somente na edição):** os campos **URL do Arquivo**, **Identificador (Slug)** e **Ícone do Módulo** ficam **desabilitados (acinzentados)** quando você edita um módulo existente — eles não podem ser alterados depois que o módulo é criado. Somente Nome, Ordem, Aba Destino e Perfil Mínimo podem ser editados.

### Campos da janela (preencha um por um)

#### URL do Arquivo (obrigatório — somente na criação)
- **O que é:** o endereço do arquivo que o sistema carrega quando você clica nesse módulo no menu.
- **Como preencher:** existem **duas formas**:
  1. **Digitando:** escreva o caminho do arquivo (ex.: `modules/home/index.html`).
  2. **Procurando:** clique no botão de **pasta aberta** (`📂`, do lado direito do campo) para abrir a janela **"Selecionar Módulo"** e escolher de uma lista. Ao escolher, o sistema preenche sozinho o endereço, o nome e o identificador.
- **Regra:** obrigatório e precisa ser um endereço válido (URL completa ou caminho de arquivo). Se estiver errado, aparece "Use uma URL ou caminho válido." e "Informe a URL do arquivo."

#### Botão de procurar módulo (pasta aberta)
- **Onde:** dentro da janela de módulo, ao lado direito do campo "URL do Arquivo".
- **O que faz:** abre a janela **"Selecionar Módulo"** para você encontrar o arquivo de uma lista pronta, sem digitar o endereço na mão.
- **Dica:** é o jeito mais fácil de criar um módulo que já existe no projeto. Não fica disponível na edição (fica acinzentado).

#### Aba Destino (obrigatório)
- **O que é:** em qual aba este módulo vai aparecer no menu.
- **Como preencher:** abra a lista e escolha a aba. Se houver sub-abas, elas aparecem com hífens `--` antes do nome para indicar o nível (ex.: `-- Sub-aba`).
- **Regra:** obrigatório. Sem escolher, aparece "Selecione a aba de destino."

#### Nome do Módulo (obrigatório)
- **O que é:** o nome que aparece no menu lateral e na linha do módulo.
- **Como preencher:** digite um nome claro (ex.: "Módulos & Abas", "Usuários").
- **Regra:** obrigatório. Se tentar salvar sem nome, aparece "Informe o nome do módulo."

#### Ordem (número)
- **O que é:** a posição do módulo dentro da aba. Número menor = aparece mais acima.
- **Como preencher:** digite um número inteiro (ex.: 0, 1, 2...).
- **Padrão:** se vazio, o valor é **0**.
- **Regra:** deve ser número; caso contrário, o sistema avisa.

#### Identificador (Slug) (obrigatório — somente na criação)
- **O que é:** um apelido curto e sem espaços que identifica o módulo internamente (ex.: `modulos-abas`, `usuarios`, `home`).
- **Como preencher:** digite letras minúsculas, números e hífens, sem espaços (ex.: `financeiro`).
- **Regra:** obrigatório, com pelo menos **2 caracteres**. Se não cumprir, aparece "Informe o identificador."
- **Dica:** se você usou o botão de procurar módulo, este campo é preenchido automaticamente.

#### Perfil Mínimo
- **O que é:** o nível de acesso mínimo que um usuário precisa ter para **ver e abrir** este módulo no menu.
- **Como preencher:** escolha uma das três opções:
  - **Leitura** — qualquer usuário logado vê o módulo.
  - **Operador** *(padrão)* — precisa ser pelo menos operador para ver.
  - **Administrador** — somente administradores veem o módulo.
- **Dica:** abaixo da lista há a explicação: *"Perfil mínimo necessário para acessar este módulo."* Se você quer restringir uma área sensível, escolha "Administrador".

#### Ícone do Módulo
- **O que é:** o ícone ao lado do nome do módulo no menu.
- **Como preencher:** igual ao ícone da aba — há a **prévia** do ícone atual e a **grade de ícones** por categorias (Coding, Devices, Design, Files, Users, Alert, Business, Charts, Communication, Editing, Logistics, Maps). Clique para escolher; o selecionado fica com borda colorida.
- **Padrão:** cubo (`fas fa-cube`).
- **Regra:** só pode ser escolhido na **criação**. Na edição, fica bloqueado.

### Botões da janela

| Botão | O que faz |
|-------|-----------|
| **Cancelar** | Fecha a janela sem salvar. |
| **Salvar Módulo** | Valida e salva. Ao criar: **"Módulo criado com sucesso."** Ao editar: **"Módulo salvo com sucesso."** Em ambos os casos o menu lateral é atualizado. Se houver erro de preenchimento: "Revise os campos destacados." |

### Fluxo passo a passo — Criar um módulo
1. Clique em **"Novo Módulo"** (ou abra "Novo Módulo" e depois clique na **pasta aberta** para procurar).
2. **Caminho rápido:** na janela "Selecionar Módulo", busque o módulo e clique nele — o sistema preenche URL, nome e slug sozinho. Depois siga do passo 4.
3. **Caminho manual:** preencha **URL do Arquivo**, **Aba Destino**, **Nome do Módulo**, **Ordem**, **Identificador (Slug)**, **Perfil Mínimo** e **Ícone do Módulo**.
4. Clique em **"Salvar Módulo"**.
5. O módulo aparece na aba escolhida e no menu lateral.

### Fluxo passo a passo — Editar um módulo
1. Clique no ícone de **caneta** na linha do módulo.
2. A janela abre com os dados atuais. **Atenção:** URL, Slug e Ícone ficam acinzentados (não podem ser alterados).
3. Você pode mudar: **Nome do Módulo**, **Ordem**, **Aba Destino** e **Perfil Mínimo**.
4. Clique em **"Salvar Módulo"**.
5. Confira as mudanças no menu.

### Fluxo passo a passo — Excluir um módulo
1. Clique no ícone de **lixeira** na linha do módulo.
2. O sistema pergunta: **"Excluir este módulo?"** — clique em **OK** para confirmar.
3. Aparece a mensagem **"Módulo excluído com sucesso."** e o menu é atualizado.
4. **Atenção:** não tem desfazer.
5. Se o módulo (ou a aba dele) for **protegido**, o botão de lixeira nem aparece, e o sistema avisa: *"O módulo 'X' é protegido e não pode ser excluído."*

---

## Janela "Selecionar Módulo" (busca de módulos)

**Como abrir:** dentro da janela **"Novo Módulo"**, clicando no botão de **pasta aberta** ao lado do campo "URL do Arquivo".

**O que é:** uma janela que lista os **módulos já disponíveis no sistema** para você escolher um, em vez de preencher tudo na mão. Ao escolher um módulo, o sistema preenche automaticamente a URL, o nome e o identificador na janela de módulo.

### Elementos da janela

#### Campo de busca "Buscar módulo..."
- **O que faz:** filtra a lista conforme você digita, pelo **nome** ou pelo **endereço** do módulo.
- **Como usar:** digite parte do nome (ex.: "usu") e a lista vai mostrando só os itens que combinam. Apague o texto para voltar a mostrar tudo.

#### Lista de módulos
- Cada linha mostra o **nome do módulo**, o **endereço (URL)** e um **selo (badge)** de status:
  - **"Vinculado em: [nome da aba]"** — o módulo já está colocado em alguma aba (linha fica com aparência apagada/desabilitada).
  - **"Não vinculado"** — o módulo ainda não foi colocado em nenhuma aba (indicado em vermelho).
- Ao lado, um ícone indica o estado: **corrente (link)** para já vinculado e **mais (+)** para não vinculado.
- **Como usar:** clique na linha do módulo que você quer — a janela fecha e os dados (URL, Nome, Slug) são preenchidos na janela de módulo.
- **Dica:** prefira escolher módulos **"Não vinculado"**, pois os já vinculados pertencem a outra aba.

#### Botão Cancelar
- Fecha a janela de seleção sem escolher nada e volta para a janela de módulo.

### Fluxo passo a passo — usar o seletor de módulos
1. Na janela **"Novo Módulo"**, clique na **pasta aberta** ao lado de "URL do Arquivo".
2. Digite na busca (opcional) para achar o módulo.
3. Clique no módulo desejado na lista.
4. A janela fecha e **URL do Arquivo**, **Nome do Módulo** e **Identificador** são preenchidos automaticamente.
5. Escolha a **Aba Destino**, o **Perfil Mínimo**, ajuste a **Ordem** e o **Ícone** se quiser.
6. Clique em **"Salvar Módulo"**.

---

## Itens Protegidos (não podem ser excluídos)

Algumas abas e módulos são **essenciais para o funcionamento do sistema** e não podem ser excluídos — o sistema também não deixa você criar módulos com esses nomes de forma conflitante. Nesses itens, o botão de **lixeira não aparece** e, se houver tentativa por outros caminhos, o sistema mostra o aviso de que o item é essencial/protegido.

**Abas protegidas:**
- "Principal"
- "Gestão"
- "Menu"

**Módulos protegidos (exemplos):**
- "Usuários"
- "Módulos & Abas" (e variações de nome)
- "Módulos"
- "Estrutura do Portal"
- "Dashboard"
- "Painel de Controle"
- "Início"

> **Dica:** você ainda pode **editar** (renomear, mudar ordem, mudar ícone) esses itens protegidos — só não pode apagá-los.

---

## Permissões e Perfis

O módulo **Módulos & Abas** só mostra o que cada usuário tem permissão de ver, conforme o **Perfil Mínimo** definido em cada módulo:

| Perfil | O que significa na prática |
|--------|----------------------------|
| **Leitura** | Qualquer usuário logado acessa o módulo. |
| **Operador** | Usuários com perfil Operador ou superior acessam. É o padrão para novos módulos. |
| **Administrador** | Somente administradores acessam o módulo. |

- Ao criar um módulo, o padrão já é **Operador**.
- Se você trocar o perfil de um módulo, ele **some ou aparece** do menu lateral de acordo com o perfil de quem está logado (na próxima atualização do menu).

---

## Mensagens e Avisos Comuns

| Situação | Mensagem que aparece |
|----------|----------------------|
| Aba salva | "Aba salva com sucesso." |
| Aba excluída | "Aba excluída com sucesso." |
| Tentativa de excluir aba essencial | "A aba 'X' é essencial para o sistema e não pode ser excluída." |
| Módulo criado | "Módulo criado com sucesso." |
| Módulo salvo (edição) | "Módulo salvo com sucesso." |
| Módulo excluído | "Módulo excluído com sucesso." |
| Tentativa de excluir módulo protegido | "O módulo 'X' é protegido e não pode ser excluído." |
| Campo obrigatório faltando / erro de validação | "Revise os campos destacados." (campos marcados em vermelho) |
| Nome de módulo vazio na edição | "Informe o nome do módulo." |
| Sem estrutura cadastrada | "Nenhuma estrutura cadastrada." |
| Falha ao carregar | Mensagem de erro com ícone de triângulo de exclamação. |

**Como as confirmações funcionam:** ao excluir uma aba ou módulo, o sistema mostra uma **caixa de confirmação** do navegador perguntando se você tem certeza. Clique em **OK** para confirmar ou **Cancelar** para desistir.

---

## Resumo Rápido (para consulta)

- **Nova Aba** (pasta +) → cria pasta do menu. Campos: Nome, Ordem, Ícone, Sub-aba de.
- **Novo Módulo** (sinal +) → cria item de menu. Campos: URL do Arquivo, Aba Destino, Nome, Ordem, Slug, Perfil Mínimo, Ícone.
- **Lápis / Caneta** → edita aba / módulo.
- **Lixeira** → exclui aba (com tudo dentro) / módulo, após confirmação. Não aparece em itens protegidos.
- **Pasta aberta** → procura módulo pronto na lista "Selecionar Módulo".
- **Ao editar módulo:** URL, Slug e Ícone ficam bloqueados.
- **Menu lateral** sempre atualiza sozinho após salvar ou excluir.
