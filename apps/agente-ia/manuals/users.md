# Manual do Módulo Usuários

## Visão Geral

O módulo **Usuários** permite gerenciar as contas de acesso ao sistema: cadastrar pessoas, definir seus perfis (níveis de acesso), ativar ou desativar contas, indicar quem pode aprovar solicitações e liberar o acesso de cada usuário aos módulos do portal.

Ao abrir o módulo, você vê uma tabela com todos os usuários cadastrados (exceto os administradores), contendo as colunas: **Usuário**, **E-mail**, **Perfil**, **Status**, **Aprovador** e **Ações**.

## Lista de Usuários

A tela inicial exibe a relação de usuários. Cada linha mostra:

- **Usuário** — foto (avatar) e nome completo da pessoa.
- **E-mail** — endereço de e-mail cadastrado.
- **Perfil** — nível de acesso: **Leitura**, **Operador** ou **Administrador**.
- **Status** — indica se a conta está **Ativa** ou **Inativa**.
- **Aprovador** — indica se a pessoa é aprovadora (**Sim** ou **Não**).
- **Ações** — botões para **Editar** e **Permissões**.

Se não houver usuários cadastrados, a tabela exibe a mensagem "Nenhum usuário encontrado".

## Cadastrar Novo Usuário

1. Na tela principal, clique no botão **Novo Usuário**.
2. Uma janela "Cadastrar Usuário" será aberta com o formulário de cadastro.
3. Preencha os campos conforme as seções abaixo.
4. Ao final, clique em **Salvar**. Clique em **Cancelar** para desistir.

### Dados do Usuário

- **Nome de Usuário** — identificador de acesso. Ao digitar o **Nome Completo**, este campo é preenchido automaticamente. Você pode alterá-lo manualmente se desejar (mínimo de 3 caracteres).
- **Perfil** — selecione o nível de acesso: **Leitura**, **Operador** ou **Administrador**.
- **Nome Completo** — nome da pessoa (obrigatório).
- **E-mail** — e-mail válido da pessoa (obrigatório).
- **Senha** — senha de acesso (obrigatória no cadastro, mínimo de 6 caracteres).

### Dados Profissionais

- **Código** — código interno do usuário na empresa.
- **C.B.O** — código da ocupação. Use o botão de busca (lupa) para consultar e preencher o **Cargo** automaticamente.
- **Salário Base** — valor do salário. O campo é formatado automaticamente no padrão brasileiro.
- **Departamento** — departamento ao qual a pessoa pertence.
- **Cargo** — preenchido automaticamente ao consultar o C.B.O (campo somente leitura).
- **Classificação** — selecione o nível: Junior, Pleno, Senior, I, II, III, IV ou V.

### Documentos

- **CPF** — número do CPF, formatado automaticamente.
- **RG** — número do RG, formatado automaticamente.

### Endereço

- **Endereço**, **Bairro**, **Cidade** e **UF** — preenchidos automaticamente ao consultar o CEP.
- **Nº** — número do imóvel.
- **CEP** — use o botão de busca (lupa) para preencher o endereço completo automaticamente.

### Contato

- **Telefone** — telefone fixo, formatado automaticamente.
- **Celular** — telefone celular, formatado automaticamente.

## Consultar CEP e C.B.O

Em alguns campos, há um botão de busca (lupa) ao lado:

- **CEP** — digite o CEP e clique na lupa (ou pressione Enter). Os campos de Endereço, Bairro, Cidade e UF são preenchidos automaticamente. Se o CEP não for encontrado, uma mensagem de erro é exibida.
- **C.B.O** — digite o código e clique na lupa (ou pressione Enter). O campo **Cargo** é preenchido automaticamente com a descrição da ocupação. Se o código não for encontrado, uma mensagem de erro é exibida.

## Editar Usuário

1. Na lista de usuários, localize a pessoa desejada.
2. Clique no ícone de **edição** (lápis) na coluna **Ações**.
3. A janela "Editar Usuário" será aberta com os dados preenchidos.
4. Altere os campos necessários. O campo **Senha** fica em branco — preencha-o apenas se desejar alterar a senha.
5. Clique em **Salvar** para confirmar as alterações.

## Ativar ou Desativar Usuário

O **Status** de cada usuário pode ser alterado diretamente na lista:

1. Na coluna **Status**, clique sobre o indicador **Ativo** ou **Inativo**.
2. O sistema alterna o status: clicar em "Ativo" desativa a conta; clicar em "Inativo" ativa a conta.

## Definir Aprovador

A marcação de **Aprovador** também pode ser alterada diretamente na lista:

1. Na coluna **Aprovador**, clique sobre o indicador **Sim** ou **Não**.
2. O sistema alterna a marcação: "Sim" indica que a pessoa é aprovadora; "Não" remove essa condição.

## Gerenciar Permissões

As permissões definem quais módulos do portal o usuário pode acessar.

1. Na lista de usuários, clique no ícone de **escudo** (Permissões) na coluna **Ações**.
2. A janela "Gerenciar Permissões" será aberta, organizada por abas do portal.
3. Marque ou desmarque os módulos desejados usando as caixas de seleção.
4. Para marcar ou desmarcar todos os módulos de uma aba de uma só vez, use a opção **"Selecionar todos"** / **"Limpar"** no topo de cada aba.
5. Módulos restritos a administradores aparecem com o marcador **Admin** ao lado do nome.
6. Clique em **Salvar Permissões** para confirmar, ou em **Cancelar** para desistir.

## Permissões Visíveis ao Usuário

- O perfil **Leitura** permite visualizar as informações, sem alterações.
- O perfil **Operador** permite operar as rotinas do dia a dia.
- O perfil **Administrador** possui acesso total, incluindo o gerenciamento de usuários e da estrutura do portal.
