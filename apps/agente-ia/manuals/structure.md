# Manual do Módulo Módulos & Abas

Este manual explica, para usuários iniciantes, tudo que o módulo **Módulos & Abas** faz. Ele também é a fonte de consulta para o assistente responder a perguntas do tipo **"o que faz o botão X?"**.

Pense assim: **as abas são as pastas do menu lateral e os módulos são os itens dentro dessas pastas.** Este módulo é onde você cria, edita e organiza esse menu.

Tudo que você mudar aqui **atualiza o menu lateral automaticamente** — não precisa sair e entrar de novo.

---

## Tela Principal — Estrutura do Portal

Essa é a primeira tela do módulo. Ela mostra todo o menu lateral atual organizado em **cartões de aba**. Dentro de cada cartão ficam os **módulos** (linhas com nome, endereço e ordem) e as **sub-abas** (abas dentro de abas, recuadas à direita com uma linha colorida na borda).

- **Título:** "Estrutura do Portal"
- **Selo de versão:** no topo, ao lado do título (só informativo).
- **Subtítulo:** "Gerencie as abas do menu lateral e os módulos do sistema."
- **Carregamento:** ao abrir, aparece "Carregando estrutura..." até a lista aparecer.
- **Mensagens possíveis:**
  - **"Nenhuma estrutura cadastrada."** → ainda não existe nenhuma aba no sistema.
  - **Erro com triângulo de exclamação** → não foi possível carregar (ex.: sem conexão). Recarregue a página e tente de novo.

### Cartão de uma aba
- **Nome da aba** com o ícone na frente (ex.: 🗂️ Gestão).
- Botões de **editar** e **excluir** no canto do cartão.
- **Módulos:** cada linha mostra o **nome**, o **endereço (URL)** e a **ordem** (ex.: "Ordem: 1").
- **Sub-abas:** aparecem dentro da aba pai, recuadas à direita, com uma linha vertical colorida na borda esquerda.

### Botão Nova Aba
- **Onde:** no topo, do lado direito (ícone de **pasta com +**).
- **O que faz:** abre a janela para **criar uma nova aba** no menu lateral.
- **Quando usar:** quando você precisa de uma nova "pasta" no menu (ex.: criar a aba "Financeiro").
- **Dica:** em telas pequenas (celular), o texto some e fica só o ícone.

### Botão Novo Módulo
- **Onde:** no topo, do lado direito (ícone de **sinal de +**).
- **O que faz:** abre a janela para **criar um novo módulo** dentro de uma aba.
- **Quando usar:** quando o módulo que você quer colocar no menu **ainda não existe** (vai preencher tudo na mão).
- **Dica:** se o módulo já existe no sistema, use o botão de **pasta aberta** dentro da janela de módulo para procurar (mais rápido).

### Botão Editar Aba (lápis)
- **Onde:** no cartão da aba, ícone de **lápis** (✏️), com a dica "Editar".
- **O que faz:** abre a janela da aba **já preenchida com os dados atuais**, para você alterar nome, ordem, ícone ou aba pai.

### Botão Excluir Aba (lixeira)
- **Onde:** no cartão da aba, ícone de **lixeira** (🗑️), com a dica "Excluir".
- **O que faz:** apaga a aba **e todos os módulos dentro dela**, após você confirmar.
- **Atenção:** não tem desfazer. O botão **não aparece** em abas protegidas (essenciais).

### Botão Editar Módulo (caneta)
- **Onde:** na linha do módulo, ícone de **caneta** (🖊️).
- **O que faz:** abre a janela do módulo já preenchida. Na edição, os campos **URL, Identificador (Slug) e Ícone ficam acinzentados** — só Nome, Ordem, Aba Destino e Perfil Mínimo podem ser alterados.

### Botão Excluir Módulo (lixeira)
- **Onde:** na linha do módulo, ícone de **lixeira** (🗑️).
- **O que faz:** apaga o módulo após você confirmar.
- **Atenção:** não tem desfazer. O botão **não aparece** em módulos protegidos (nem em módulos dentro de aba protegida).

---

## Janela "Nova Aba" / "Editar Aba"

**Como abrir:**
- Para **criar**: clique no botão **Nova Aba** do topo.
- Para **editar**: clique no **lápis** no cartão da aba.

**O que é:** uma janela flutuante (modal) no centro da tela. O título muda conforme a ação: **"Nova Aba"** ou **"Editar Aba"**. Ao editar, os campos já vêm preenchidos.

> **Dica:** para fechar sem salvar, clique em **Cancelar** ou aperte **Esc**. Ao fechar, o formulário é limpo.

### Campo Nome da Aba (obrigatório)
- **O que é:** o nome que aparece no menu lateral.
- **Como preencher:** digite um nome curto e claro, como "Gestão", "Relatórios" ou "Financeiro".
- **Regra:** obrigatório. Se faltar, o campo fica destacado em vermelho e aparece "Informe o nome da aba."

### Campo Ordem (número)
- **O que é:** a posição da aba no menu. Número menor = mais acima.
- **Como preencher:** digite um número inteiro (ex.: 0, 1, 2...).
- **Padrão:** se vazio, usa **0**.

### Campo Ícone da Aba
- **O que é:** o ícone ao lado do nome da aba no menu.
- **Como preencher:** veja a **prévia** do ícone atual e a **grade de ícones** logo abaixo, organizada por categorias (Coding, Devices, Design, Files, Users, Alert, Business, Charts, Communication, Editing, Logistics, Maps). **Clique em um ícone** para escolher — o selecionado fica com borda colorida (azul). A grade tem rolagem própria.
- **Padrão:** pasta.

### Campo Sub-aba de (opcional)
- **O que é:** se você quiser que esta aba fique **dentro de outra aba** (vire sub-aba), escolhe aqui a aba "mãe".
- **Como preencher:** abra a lista e escolha a aba pai. Só aparecem as abas **raiz** (que não são sub-aba de ninguém).
- **Deixar em branco:** fica **"Nenhuma (aba raiz)"** — a aba vira raiz do menu.

### Botão Cancelar
- **O que faz:** fecha a janela **sem salvar** nada. O formulário é limpo.

### Botão Salvar Aba
- **O que faz:** valida os campos e salva a aba.
- **Se der certo:** aparece **"Aba salva com sucesso."** e o menu lateral atualiza na hora.
- **Se algo estiver errado:** aparece "Revise os campos destacados." e o formulário não fecha.

### Fluxo passo a passo — Criar uma aba
1. Clique em **Nova Aba**.
2. Em **Nome da Aba**, digite o nome (ex.: "Financeiro").
3. Em **Ordem**, digite a posição (ex.: 2).
4. Em **Ícone da Aba**, clique no ícone desejado.
5. Em **Sub-aba de**, escolha a aba pai (ou deixe "Nenhuma" para ser raiz).
6. Clique em **Salvar Aba**.
7. A nova aba aparece na estrutura e no menu lateral.

### Fluxo passo a passo — Editar uma aba
1. Clique no **lápis** no cartão da aba.
2. Altere os campos que quiser.
3. Clique em **Salvar Aba**.
4. Confira as mudanças no menu.

### Fluxo passo a passo — Excluir uma aba
1. Clique na **lixeira** no cartão da aba.
2. O sistema pergunta **"Excluir esta aba e todos os seus módulos?"** — clique em **OK** para confirmar ou **Cancelar** para desistir.
3. A aba **e todos os módulos dentro dela** são apagados. Aparece **"Aba excluída com sucesso."** e o menu atualiza.
4. **Atenção:** sem desfazer. Abas protegidas não mostram o botão de lixeira.

---

## Janela "Novo Módulo" / "Editar Módulo"

**Como abrir:**
- Para **criar**: clique no botão **Novo Módulo** do topo.
- Para **editar**: clique na **caneta** na linha do módulo.

**O que é:** janela flutuante para criar ou alterar um módulo. Título: **"Novo Módulo"** ou **"Editar Módulo"**. Ao editar, os campos já vêm preenchidos.

> **Importante (na edição):** os campos **URL do Arquivo**, **Identificador (Slug)** e **Ícone do Módulo** ficam **desabilitados (acinzentados)** — não podem ser alterados depois que o módulo é criado.

### Campo URL do Arquivo (obrigatório — somente na criação)
- **O que é:** o endereço do arquivo que o sistema carrega quando você clica nesse módulo no menu.
- **Como preencher — duas formas:**
  1. **Digitando:** escreva o caminho (ex.: `modules/home/index.html`).
  2. **Procurando:** clique no botão de **pasta aberta** ao lado do campo para abrir a janela **"Selecionar Módulo"**. Ao escolher, o sistema preenche sozinho o endereço, o nome e o identificador.
- **Regra:** obrigatório e precisa ser endereço válido.

### Botão Procurar Módulo (pasta aberta)
- **Onde:** na janela de módulo, ao lado direito do campo "URL do Arquivo".
- **O que faz:** abre a janela **"Selecionar Módulo"** para você escolher de uma lista pronta, sem digitar o endereço na mão.
- **Dica:** é o jeito mais fácil de criar um módulo que já existe no projeto. Fica acinzentado na edição.

### Campo Aba Destino (obrigatório)
- **O que é:** em qual aba este módulo vai aparecer no menu.
- **Como preencher:** abra a lista e escolha a aba. Sub-abas aparecem com hífens `--` antes do nome para indicar o nível.
- **Regra:** obrigatório. Se faltar, aparece "Selecione a aba de destino."

### Campo Nome do Módulo (obrigatório)
- **O que é:** o nome que aparece no menu lateral.
- **Como preencher:** digite um nome claro (ex.: "Módulos & Abas", "Usuários").
- **Regra:** obrigatório. Se faltar, aparece "Informe o nome do módulo."

### Campo Ordem (número)
- **O que é:** a posição do módulo dentro da aba. Número menor = mais acima.
- **Como preencher:** digite um número inteiro.
- **Padrão:** se vazio, usa **0**.

### Campo Identificador (Slug) (obrigatório — somente na criação)
- **O que é:** um apelido curto, sem espaços, que identifica o módulo internamente (ex.: `modulos-abas`, `usuarios`).
- **Como preencher:** letras minúsculas, números e hífens, sem espaços.
- **Regra:** obrigatório, com pelo menos **2 caracteres**. Se faltar, aparece "Informe o identificador."
- **Dica:** se você usou o **procurar módulo**, este campo é preenchido automaticamente.

### Campo Perfil Mínimo
- **O que é:** o nível de acesso mínimo para **ver e abrir** este módulo no menu.
- **Como preencher:** escolha uma das opções:
  - **Leitura** — qualquer usuário logado vê.
  - **Operador** *(padrão)* — precisa ser pelo menos operador.
  - **Administrador** — somente administradores veem.
- **Dica:** abaixo da lista aparece a explicação: *"Perfil mínimo necessário para acessar este módulo."*

### Campo Ícone do Módulo
- **O que é:** o ícone ao lado do nome do módulo no menu.
- **Como preencher:** igual ao ícone da aba — **prévia** + **grade de ícones** por categorias. Clique para escolher; o selecionado fica com borda colorida.
- **Padrão:** cubo.
- **Regra:** só pode ser escolhido na **criação**. Na edição fica bloqueado.

### Botão Cancelar
- **O que faz:** fecha a janela **sem salvar** nada.

### Botão Salvar Módulo
- **O que faz:** valida e salva o módulo.
- **Ao criar:** aparece **"Módulo criado com sucesso."**
- **Ao editar:** aparece **"Módulo salvo com sucesso."**
- **Erro de preenchimento:** "Revise os campos destacados." O menu lateral atualiza sempre que salva.

### Fluxo passo a passo — Criar um módulo
1. Clique em **Novo Módulo**.
2. **Caminho rápido:** clique na **pasta aberta**, busque o módulo na lista e clique nele — URL, nome e slug são preenchidos sozinhos. Siga do passo 4.
3. **Caminho manual:** preencha **URL do Arquivo**, **Aba Destino**, **Nome do Módulo**, **Ordem**, **Identificador (Slug)**, **Perfil Mínimo** e **Ícone do Módulo**.
4. Clique em **Salvar Módulo**.
5. O módulo aparece na aba escolhida e no menu lateral.

### Fluxo passo a passo — Editar um módulo
1. Clique na **caneta** na linha do módulo.
2. A janela abre com os dados atuais. **Atenção:** URL, Slug e Ícone ficam acinzentados.
3. Você pode mudar: **Nome do Módulo**, **Ordem**, **Aba Destino** e **Perfil Mínimo**.
4. Clique em **Salvar Módulo**.
5. Confira as mudanças no menu.

### Fluxo passo a passo — Excluir um módulo
1. Clique na **lixeira** na linha do módulo.
2. O sistema pergunta **"Excluir este módulo?"** — clique em **OK** para confirmar.
3. Aparece **"Módulo excluído com sucesso."** e o menu atualiza.
4. **Atenção:** sem desfazer. Módulos protegidos não mostram o botão de lixeira.

---

## Janela "Selecionar Módulo" (busca de módulos)

**Como abrir:** dentro da janela **"Novo Módulo"**, clicando na **pasta aberta** ao lado do campo "URL do Arquivo".

**O que é:** uma janela que lista os **módulos já disponíveis no sistema**. Ao escolher um, o sistema preenche automaticamente a URL, o nome e o identificador na janela de módulo.

### Campo de busca "Buscar módulo..."
- **O que faz:** filtra a lista conforme você digita, pelo **nome** ou pelo **endereço** do módulo.
- **Como usar:** digite parte do nome (ex.: "usu") e a lista mostra só o que combina. Apague o texto para voltar a mostrar tudo.

### Lista de módulos
- Cada linha mostra o **nome**, o **endereço (URL)** e um **selo de status**:
  - **"Vinculado em: [nome da aba]"** — já está colocado em alguma aba (linha com aparência apagada).
  - **"Não vinculado"** — ainda não foi colocado em nenhuma aba (indicado em vermelho).
- O ícone ao lado indica o estado: **corrente (link)** para já vinculado e **mais (+)** para não vinculado.
- **Como usar:** clique na linha desejada — a janela fecha e URL, Nome e Slug são preenchidos na janela de módulo.
- **Dica:** prefira módulos **"Não vinculado"**, pois os já vinculados pertencem a outra aba.

### Botão Cancelar
- **O que faz:** fecha a janela de seleção sem escolher nada e volta para a janela de módulo.

### Fluxo passo a passo — usar o seletor de módulos
1. Na janela **"Novo Módulo"**, clique na **pasta aberta** ao lado de "URL do Arquivo".
2. Digite na busca (opcional) para achar o módulo.
3. Clique no módulo desejado na lista.
4. A janela fecha e **URL do Arquivo**, **Nome do Módulo** e **Identificador** são preenchidos automaticamente.
5. Escolha a **Aba Destino**, o **Perfil Mínimo**, e ajuste **Ordem** e **Ícone** se quiser.
6. Clique em **Salvar Módulo**.

---

## Itens Protegidos (não podem ser excluídos)

Algumas abas e módulos são **essenciais para o sistema** e não podem ser excluídos. Nesses itens, o botão de **lixeira não aparece**. Se houver tentativa por outros caminhos, o sistema avisa que o item é essencial/protegido.

**Abas protegidas:**
- "Principal"
- "Gestão"
- "Menu"

**Módulos protegidos (exemplos):**
- "Usuários"
- "Módulos & Abas" (e variações)
- "Módulos"
- "Estrutura do Portal"
- "Dashboard"
- "Painel de Controle"
- "Início"

> **Dica:** você ainda pode **editar** (renomear, mudar ordem, mudar ícone) itens protegidos — só não pode apagá-los.

---

## Permissões e Perfis

O módulo **Módulos & Abas** só mostra o que cada usuário pode ver, conforme o **Perfil Mínimo** de cada módulo:

| Perfil | O que significa na prática |
|--------|----------------------------|
| **Leitura** | Qualquer usuário logado acessa o módulo. |
| **Operador** | Usuários Operador ou superior acessam. Padrão para novos módulos. |
| **Administrador** | Somente administradores acessam o módulo. |

- Ao criar um módulo, o padrão já é **Operador**.
- Ao trocar o perfil de um módulo, ele **some ou aparece** no menu conforme o perfil de quem está logado (na próxima atualização do menu).

---

## Resumo Rápido (para consulta)

| Quero fazer... | Onde clico |
|---|---|
| Criar uma aba (pasta do menu) | Botão **Nova Aba** (pasta com +) |
| Criar um módulo (item de menu) | Botão **Novo Módulo** (sinal +) |
| Editar uma aba | **Lápis** no cartão da aba |
| Excluir uma aba | **Lixeira** no cartão da aba (não aparece em itens protegidos) |
| Editar um módulo | **Caneta** na linha do módulo |
| Excluir um módulo | **Lixeira** na linha do módulo (não aparece em itens protegidos) |
| Procurar um módulo pronto | **Pasta aberta** ao lado de "URL do Arquivo" |
| Cancelar sem salvar | **Cancelar** (em qualquer janela) |

**Lembretes importantes:**
- **Aba = pasta**, **módulo = item dentro da pasta**. Uma aba pode ter sub-abas.
- Ao **editar módulo**, URL, Slug e Ícone ficam bloqueados.
- Excluir **aba** apaga tudo que está dentro dela, sem desfazer.
- O **menu lateral sempre atualiza sozinho** após salvar ou excluir.
