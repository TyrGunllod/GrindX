# Manual do Módulo Usuários

Bem-vindo ao manual do módulo **Usuários** do GrindX! Este módulo é onde você gerencia quem pode acessar o sistema. Aqui você cadastra novos colaboradores, edita os dados deles, controla se a pessoa pode entrar (ativo ou inativo), define quem é aprovador e escolhe quais telas (módulos) cada usuário pode ver.

Neste manual, tudo é explicado **passo a passo**, como se fosse a primeira vez que você abre a tela. Vamos lá!

---

## Tela Principal — Lista de Usuários

Essa é a primeira coisa que você vê ao abrir o módulo. No topo aparece o título **"Gerenciamento de Usuários"** com a frase *"Controle de acesso e permissões modulares"* logo abaixo. No cantinho, você também vê a **versão do sistema** — isso ajuda a saber se você está na tela mais recente.

O restante da tela é uma **tabela** com a lista de todos os usuários cadastrados (exceto administradores — eles não aparecem aqui). Cada linha da tabela é um usuário.

### Como chegar nessa tela
1. Entre no GrindX com seu login e senha.
2. No menu lateral, clique em **Usuários** (ou no caminho que leva ao módulo de usuários).
3. Pronto — a lista carrega sozinha. Enquanto isso, aparece uma mensagem *"Carregando usuários..."*.

> Se a sua sessão expirou, você verá a mensagem *"Sessão expirada. Faça login novamente."* — é só entrar de novo que a tela volta ao normal.

### Colunas da tabela

| Coluna | O que mostra |
|---|---|
| **Usuário** | A **foto/avatar** (gerada a partir do nome) e o **nome completo** da pessoa, lado a lado. |
| **E-mail** | O e-mail de acesso do usuário. Em telas menores (celular), essa coluna fica escondida para caber melhor. |
| **Perfil** | O tipo de acesso, em um selo colorido: **LEITURA** ou **OPERADOR**. |
| **Status** | Um selo que mostra se a pessoa está **Ativo** (verde) ou **Inativo** (cinza). Esse selo é clicável (veja abaixo). |
| **Aprovador** | Um selo que mostra **Sim** ou **Não** — indica se a pessoa pode ser aprovadora. Também é clicável. |
| **Ações** | Botões de ação de cada linha: editar e permissões (veja abaixo). |

> **Observação:** na versão de celular, a tabela vira cartões. Cada cartão mostra o nome do campo (ex.: "E-mail") seguido do valor, um embaixo do outro, com as ações separadas na parte de baixo. Nada muda no funcionamento — só muda o visual.

### Botões e ícones da tela principal

- **+ Novo Usuário** (botão no canto superior esquerdo) — abre a janela de **cadastro** de um novo usuário. Em telas pequenas, o texto some e fica só o ícone de "+".
- **Selo de Status (Ativo / Inativo)** — clique nele para **ativar ou desativar** a pessoa. Ao passar o mouse, aparece a dica *"Clique para desativar"* (se estiver ativo) ou *"Clique para ativar"* (se estiver inativo). Veja o passo a passo na seção de status.
- **Selo de Aprovador (Sim / Não)** — clique nele para **dar ou tirar** o papel de aprovador da pessoa. Ao passar o mouse, aparece a dica *"Clique para tornar aprovador"* ou *"Clique para remover aprovador"*. Veja mais na seção própria.
- **Ícone de lápis (✏️)** — na coluna Ações. **Edita o usuário**: abre a mesma janela do cadastro, já preenchida com os dados atuais, para você alterar. A dica ao passar o mouse é *"Editar Usuário"*.
- **Ícone de escudo (🛡️)** — na coluna Ações. **Abre a janela de Permissões** desse usuário, onde você escolhe quais módulos ele pode acessar. A dica ao passar o mouse é *"Permissões"*.

> **E se não houver nenhum usuário?** A tela mostra a mensagem *"Nenhum usuário encontrado."* — é só cadastrar um novo pelo botão **Novo Usuário**.

---

## Cadastrar Usuário

Aqui você cria o acesso de uma pessoa nova no sistema. Tudo é feito dentro de uma janela (modal) que divide os dados em **5 blocos** bem organizados, com um risco separando cada um.

### Como abrir
1. Clique no botão **+ Novo Usuário**, no canto superior direito da tela.
2. A janela **"Cadastrar Usuário"** abre, já posicionando o cursor no campo *Nome Completo* para você digitar direto.

### Como preencher — campo por campo

#### Bloco 1: Dados do Usuário
- **Nome de Usuário** — o nome que a pessoa vai usar para entrar no sistema. **Dica esperta:** ele é **gerado automaticamente** conforme você digita o *Nome Completo* (primeiro nome + iniciais dos sobrenomes, ignorando palavras como "de", "da", "do", "e"). Ex.: "Maria Silva Souza" vira `marias`. Se quiser um nome diferente, é só **clicar nesse campo e digitar por cima** — a partir daí o preenchimento automático para. Deve ter **no mínimo 3 caracteres**.
- **Perfil** — a lista para escolher o nível de acesso. As opções são:
  - **Leitura** — a pessoa só pode **ver** as telas (opção que já vem marcada por padrão).
  - **Operador** — além de ver, pode **fazer alterações** nas telas liberadas.
  - (O perfil *Administrador* não aparece aqui, pois ele é gerenciado à parte.)

#### Bloco 2: Dados Profissionais
- **Código** — um código interno do colaborador, se a sua empresa usar (opcional).
- **C.B.O** — a classificação da profissão (Código Brasileiro de Ocupação). Tem um botãozinho de **🔍 lupa** ao lado (explicado abaixo) que busca o cargo automaticamente.
- **Salário Base** — o salário da pessoa. É só digitar e, ao sair do campo, ele **se formata sozinho** no padrão brasileiro (ex.: `2.500,00`). Opcional.
- **Departamento** — em qual departamento a pessoa trabalha (opcional).
- **Cargo** — o cargo do colaborador. **Atenção:** esse campo você não digita — ele é **preenchido automaticamente** quando você busca o C.B.O. Por isso ele aparece "travado".
- **Classificação** — um nível de senioridade. Escolha na lista: `Junior`, `Pleno`, `Senior` ou os níveis `I`, `II`, `III`, `IV`, `V`. Obrigatório escolher uma (ou deixar em "Selecione..." se não souber).

#### Bloco 3: Documentos
- **CPF** — o CPF da pessoa. Ao sair do campo, ele se formata sozinho (ex.: `123.456.789-00`). Obrigatório.
- **RG** — o registro geral. Também se formata sozinho (ex.: `12.345.678-9`). Obrigatório.

#### Bloco 4: Endereço
- **Endereço** — a rua/avenida. **É preenchido automaticamente** pela busca de CEP, então fica "travado". Se precisar, é melhor usar a busca (veja abaixo).
- **Nº** — o número do imóvel.
- **CEP** — o código postal. Ao sair do campo, formata sozinho (ex.: `01310-100`).
- **Bairro**, **Cidade** e **UF** — também **preenchidos automaticamente** pela busca de CEP, ficam "travados". A UF aceita só 2 letras.

#### Bloco 5: Contato
- **Telefone** — telefone fixo, formata sozinho (ex.: `(11) 3456-7890`).
- **Celular** — celular, formata sozinho (ex.: `(11) 98765-4321`).

### Botões com ação dentro do formulário

- **🔍 (lupa, ao lado de C.B.O)** — busca o cargo a partir do CBO. **Como usar:** digite pelo menos 4 números do CBO no campo e clique na lupa (ou pressione **Enter** com o cursor no campo). Se encontrar, o campo **Cargo** é preenchido automaticamente. Se não achar, aparece um aviso de erro na tela.
- **🔍 (lupa, ao lado de CEP)** — busca o endereço a partir do CEP. **Como usar:** digite o CEP com 8 números e clique na lupa (ou pressione **Enter** no campo). Ele preenche **Endereço, Bairro, Cidade e UF** sozinho. Se não achar, aparece um aviso.

> **Atalho rápido:** dentro do formulário, apertar **Enter** pula para o próximo campo (e dispara as buscas de CBO e CEP quando você está neles).

### Rodapé da janela (botões finais)

- **Cancelar** — fecha a janela **sem salvar** nada. Tudo que você digitou é descartado e o formulário é limpo.
- **Salvar** — confere as informações, grava o usuário e fecha a janela. Se algum campo obrigatório estiver errado (usuário com menos de 3 letras, nome vazio, e-mail sem "@", ou senha com menos de 6 caracteres), aparece um aviso explicando o que corrigir e a janela **não** fecha. Quando salvar com sucesso, aparece a mensagem *"Usuário salvo com sucesso."* e o novo usuário entra na lista.

> **Sobre a senha:** no cadastro, o campo **Senha** é obrigatório (mínimo 6 caracteres) e a dica *"Preencha apenas se deseja alterar a senha"* fica visível já no cadastro.

---

## Editar Usuário

Quando você precisa corrigir ou atualizar os dados de alguém (mudou de cargo, telefone, departamento, etc.).

### Como fazer
1. Na lista, localize o usuário que quer editar.
2. Clique no **ícone de lápis (✏️)** na coluna **Ações** da linha dele.
3. A janela abre com o título **"Editar Usuário"** e **todos os campos já preenchidos** com os dados atuais.
4. Faça as alterações que quiser (mesmos campos do cadastro).
5. No rodapé:
   - **Salvar** — grava as mudanças e fecha a janela.
   - **Cancelar** — fecha sem alterar nada.

### Diferenças em relação ao cadastro
- O campo **Senha** agora é **opcional** e já vem vazio. Deixe em branco se a senha **não** vai mudar; preencha apenas se quiser trocá-la (aparece a dica *"Preencha apenas se deseja alterar a senha."*). É por isso que na edição não é obrigatório.
- O **Nome de Usuário** vem preenchido e **não** é gerado automaticamente (o preenchimento automático fica desligado para não sobrescrever o que já existe).

---

## Ativar e Desativar Usuário (Status)

O **Status** controla se a pessoa pode entrar no sistema. Quem está **Inativo** não consegue mais acessar — útil quando o colaborador sai da empresa, está de afastamento, etc. Ninguém é apagado do sistema; a pessoa só é desligada do acesso.

### Como desativar
1. Na coluna **Status**, localize o selo **Ativo** (verde) do usuário.
2. Clique nele. A mensagem *"Usuário desativado com sucesso."* aparece e o selo muda para **Inativo** (cinza).

### Como ativar
1. Localize o selo **Inativo** (cinza) do usuário.
2. Clique nele. Aparece *"Usuário ativado com sucesso."* e o selo volta para **Ativo** (verde), liberando o acesso.

> **Dica:** ao passar o mouse no selo, o sistema mostra uma dica confirmando o que o clique vai fazer. Sem risco de clicar sem querer.

---

## Definir e Remover Aprovador

O campo **Aprovador** marca as pessoas que exercem o papel de **aprovador** no sistema (quem aprova algo nos outros módulos). É um "sim ou não" por usuário.

### Como tornar alguém aprovador
1. Na coluna **Aprovador**, localize o selo **Não** do usuário.
2. Clique nele. Aparece *"Aprovador ativado com sucesso."* e o selo muda para **Sim** (verde).

### Como remover o papel de aprovador
1. Localize o selo **Sim** (verde) do usuário.
2. Clique nele. Aparece *"Aprovador desativado com sucesso."* e o selo volta para **Não**.

> **Dica:** a dica ao passar o mouse diz exatamente o que o clique fará ("Clique para tornar aprovador" / "Clique para remover aprovador").

---

## Gerenciar Permissões

Essa é a janela onde você escolhe **quais telas (módulos) cada usuário pode ver e usar**. Pense nela como uma lista de "checkboxes" de acesso: o que estiver marcado, a pessoa vê; o que não estiver, ela não vê.

### Como abrir
1. Na lista de usuários, localize a pessoa.
2. Clique no **ícone de escudo (🛡️)** na coluna **Ações**.
3. A janela **"Gerenciar Permissões"** abre mostrando *"Carregando permissões..."* por um instante e, em seguida, a lista completa de módulos.

### Como entender a tela
A janela traz os módulos do sistema **agrupados por abas** (as seções do menu do GrindX). Cada grupo aparece dentro de um cartão com o nome da aba e um ícone. Exemplo de como seria a organização:

- **Aba do sistema** (ex.: *Início*, *Financeiro*, *Estoque*...) — cada aba é um cartão.
  - Dentro de cada cartão, ficam os **módulos** daquela aba, cada um com uma **checkbox** (caixinha de marcar), um ícone e o nome do módulo.
  - Alguns módulos têm **subgrupos** — aparece um nome de seção menor com os módulos filhos recuados à direita, com uma barrinha na lateral para você entender a hierarquia.
  - Alguns módulos têm um selo vermelho **"ADMIN"** ao lado do nome. Isso significa que é um módulo **exclusivo de administradores** — mesmo que você marque, apenas perfis de admin realmente o usam.

### Controles da janela (campo a campo)

- **Checkbox de cada módulo** — marque para **liberar** o módulo para o usuário; desmarque para **bloquear**. Você pode marcar e desmarcar à vontade antes de salvar.
- **"Selecionar todos" / "Limpar"** — no canto direito do cabeçalho de cada aba (grupo). Uma caixinha de seleção em massa:
  - Se **nenhum** (ou só alguns) módulos da aba estiver marcado, aparece o texto **"Selecionar todos"**. Marque essa caixinha para **liberar todos os módulos** daquela aba de uma vez — o texto muda para "Limpar".
  - Se **todos** os módulos da aba já estiverem marcados, aparece **"Limpar"**. Clique para **remover o acesso a todos** os módulos daquela aba de uma vez — o texto volta para "Selecionar todos".

> **Dica:** se a lista for longa, a janela rola sozinha por dentro. Os botões de salvar/cancelar ficam sempre visíveis no rodapé.

### Rodapé da janela (botões finais)

- **Cancelar** — fecha a janela **sem aplicar** nenhuma mudança.
- **Salvar Permissões** — grava as permissões marcadas e fecha a janela. Ao concluir, aparece a mensagem *"Permissões atualizadas com sucesso."*.

> **E se der erro ao carregar?** A janela mostra a mensagem *"Erro ao carregar permissões."* — nesse caso, feche e tente abrir de novo. Se persistir, avise o suporte.

---

## Resumo rápido (colinha)

| Quero fazer... | Onde clico |
|---|---|
| Cadastrar usuário | Botão **+ Novo Usuário** |
| Editar dados de alguém | **✏️ lápis** na linha da pessoa |
| Abrir/fechar acesso de alguém | **Selo Status** (Ativo/Inativo) |
| Dar/tirar papel de aprovador | **Selo Aprovador** (Sim/Não) |
| Liberar/bloquear telas | **🛡️ escudo** na linha da pessoa |
| Buscar cargo pelo CBO | **🔍 lupa** ao lado do campo C.B.O |
| Buscar endereço pelo CEP | **🔍 lupa** ao lado do campo CEP |
| Trocar senha de alguém | **✏️ lápis** → preencher o campo **Senha** |
| Cancelar sem salvar | **Cancelar** (no rodapé de qualquer janela) |

Se ainda tiver dúvidas sobre algum campo ou botão, é só perguntar — o manual está aqui para isso!
