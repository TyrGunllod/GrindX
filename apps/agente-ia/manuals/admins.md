# Manual do Módulo Administradores

Bem-vindo ao manual do módulo **Administradores** do ERP GrindX! Aqui você aprende, passo a passo, tudo o que dá para fazer nessa tela: cadastrar novos administradores, editar os dados de quem já existe e ativar/desativar o acesso de cada um.

## Tela: Lista de Administradores

Esta é a primeira tela do módulo. Ela mostra todos os administradores cadastrados no sistema em uma lista (tabela), com o nome, o e-mail e o status de cada um.

- No topo você vê o título **Administradores** e, logo abaixo, a lista completa.
- Cada linha da lista representa um administrador.
- Ao lado de cada nome aparece um retrato com as iniciais (gerado automaticamente).
- Do lado direito do cabeçalho fica o botão **Novo Administrador**.

### Coluna Administrador

Mostra o nome completo do administrador com um retrato de iniciais ao lado. É só para identificar a pessoa.

### Coluna E-mail

Mostra o e-mail de acesso do administrador. É com esse e-mail que ele entra no sistema.

### Coluna Status

Mostra se o administrador está **Ativo** ou **Inativo**:

- **Ativo** (verde): a pessoa consegue acessar o sistema normalmente.
- **Inativo** (cinza): a pessoa está bloqueada e não consegue mais entrar.

O status também funciona como um botão: clicar nele liga ou desliga o acesso da pessoa. Para detalhes, veja **Botão Status (Ativar/Desativar)**.

### Botão Novo Administrador

- **O que faz:** abre a janela (modal) para cadastrar um novo administrador.
- **Como usar:** clique no botão **+ Novo Administrador**, no topo da tela. A janela "Cadastrar Administrador" vai abrir. Preencha os campos seguindo o passo a passo da seção **Tela: Modal de Cadastro / Edição de Administrador** e clique em **Salvar**.
- **Quando usar:** sempre que precisar dar acesso a uma nova pessoa no sistema.

### Botão Status (Ativar/Desativar)

- **O que faz:** ativa ou desativa o acesso do administrador, sem precisar apagar nada.
- **Como usar:** na lista, clique sobre o texto de status da pessoa (o "Ativo" verde ou o "Inativo" cinza).
- **Dica:** se está **Ativo**, um clique desativa. Se está **Inativo**, um clique ativa.
- **Quando usar:** para bloquear o acesso de quem saiu da empresa ou liberar quem voltou. Nenhum dado é apagado ao desativar.

### Botão Editar (lápis)

- **O que faz:** abre a janela (modal) para editar os dados de um administrador já cadastrado.
- **Como usar:** na linha do administrador, clique no ícone de lápis ✏️ (fica na coluna Ações, do lado direito). A janela "Editar Administrador" vai abrir com todos os dados já preenchidos.
- **Dica:** aqui você pode corrigir informações e também trocar a senha (deixe o campo Senha vazio se não quiser mudar).
- **Quando usar:** sempre que precisar atualizar os dados de um administrador.

## Tela: Modal de Cadastro / Edição de Administrador

Esta é a janela que aparece para cadastrar um administrador novo ou editar um existente.

**Como abrir:**

- Para cadastrar: clique em **Novo Administrador** na lista.
- Para editar: clique no ícone de lápis ✏️ na linha do administrador.

O título da janela muda conforme a situação: **"Cadastrar Administrador"** ou **"Editar Administrador"**.

A janela tem vários campos. Os com um asterisco são obrigatórios. Preencha com calma, seção por seção, e ao final clique em **Salvar**. Se mudar de ideia, clique em **Cancelar**.

### Campo Nome de Usuário

- **O que é:** o apelido (login) que o administrador usa para entrar no sistema.
- **Como preencher:** ele é preenchido sozinho conforme você digita o **Nome Completo** (ex.: "Maria da Silva" vira "marias"). Mas você pode trocar: clique no campo e digite o login que quiser.
- **Obrigatório?** Sim. Precisa ter pelo menos 3 caracteres.
- **Dica:** se você limpar o campo e sair dele, ele volta a preencher sozinho na próxima vez.

### Campo Perfil

- **O que é:** o tipo de acesso da pessoa.
- **Como preencher:** não precisa fazer nada. Ele já vem travado em **Administrador**, pois você está nesse módulo.

### Campo Nome Completo

- **O que é:** o nome completo e real da pessoa, que aparece na lista.
- **Como preencher:** digite o nome inteiro, sem abreviações.
- **Obrigatório?** Sim. Precisa ter pelo menos 2 caracteres.

### Campo E-mail

- **O que é:** o e-mail da pessoa, usado para acessar o sistema.
- **Como preencher:** digite um e-mail válido (tem que ter o "@").
- **Obrigatório?** Sim.

### Campo Senha

- **O que é:** a senha de acesso ao sistema.
- **Como preencher:** 
  - **Ao cadastrar:** é obrigatória e precisa ter no mínimo 6 caracteres.
  - **Ao editar:** deixe **vazio** para manter a senha atual. Digite uma nova senha (mínimo 6 caracteres) somente se quiser trocar.
- **Obrigatório?** Sim para cadastro novo, opcional na edição.
- **Dica:** abaixo do campo aparece a dica "Preencha apenas se deseja alterar a senha" para lembrar disso na edição.

### Bloco Dados Profissionais

Aqui você informa os dados de trabalho do administrador: código, CBO, salário, departamento, cargo e classificação. Preencha os que fizerem sentido.

#### Campo Código

- **O que é:** um código interno para identificar o administrador na empresa.
- **Como preencher:** digite o código (número ou texto) que a empresa utiliza.

#### Campo C.B.O

- **O que é:** a Classificação Brasileira de Ocupações, ou seja, o código da profissão.
- **Como preencher:** digite o código numérico do CBO e saia do campo (ou use o botão de busca ao lado). O sistema consulta e preenche o **Cargo** automaticamente.
- **Dica:** se o cargo não for preenchido, confira se o código foi digitado certo.

### Botão Buscar CBO (lupa)

- **O que faz:** consulta o código CBO digitado e preenche o campo **Cargo** automaticamente.
- **Como usar:** digite o código do CBO no campo **C.B.O** e clique no botão de lupa 🔍 ao lado dele.
- **Dica:** se o CBO não for encontrado, aparece um aviso na tela.

#### Campo Salário Base

- **O que é:** o salário de referência do administrador.
- **Como preencher:** digite o valor. Ao sair do campo, ele é formatado sozinho no padrão brasileiro (ex.: 1.500,00).
- **Dica:** você pode digitar com ou sem pontos/vírgula; o sistema ajusta a formatação.

#### Campo Departamento

- **O que é:** o setor onde o administrador trabalha.
- **Como preencher:** digite o nome do departamento (ex.: "TI", "Financeiro").

#### Campo Cargo

- **O que é:** o cargo/função do administrador.
- **Como preencher:** normalmente ele é preenchido sozinho ao consultar o **CBO**. Não é possível digitar direto.
- **Dica:** se não preencher, use o botão de busca do campo **C.B.O**.

#### Campo Classificação

- **O que é:** o nível da pessoa na carreira.
- **Como preencher:** clique no campo e escolha uma opção da lista: Junior, Pleno, Senior, I, II, III, IV ou V.

### Bloco Documentos

Aqui você informa os documentos do administrador.

#### Campo CPF

- **O que é:** o CPF da pessoa.
- **Como preencher:** digite os números. Ao sair do campo, o sistema formata sozinho (ex.: 123.456.789-00).

#### Campo RG

- **O que é:** o RG da pessoa.
- **Como preencher:** digite os números. Ao sair do campo, o sistema formata sozinho.

### Bloco Endereço

Aqui você informa o endereço do administrador.

#### Campo CEP

- **O que é:** o CEP da pessoa.
- **Como preencher:** digite o CEP (só números). Ao sair do campo, o sistema formata sozinho (ex.: 01001-000) e preenche automaticamente o **Endereço**, **Bairro**, **Cidade** e **UF**.
- **Dica:** dá para usar o botão de busca ao lado do campo para consultar o CEP.

### Botão Buscar CEP (lupa)

- **O que faz:** consulta o CEP digitado e preenche sozinho os campos de endereço (Endereço, Bairro, Cidade e UF).
- **Como usar:** digite o CEP no campo **CEP** e clique no botão de lupa 🔍 ao lado.
- **Dica:** se o CEP não for encontrado, aparece um aviso na tela.

#### Campo Endereço

- **O que é:** a rua/avenida do administrador.
- **Como preencher:** é preenchido sozinho ao consultar o **CEP**. Para corrigir, você pode digitar por cima.

#### Campo Nº

- **O que é:** o número do imóvel no endereço.
- **Como preencher:** digite o número (até 6 caracteres).

#### Campo Bairro

- **O que é:** o bairro do endereço.
- **Como preencher:** é preenchido sozinho ao consultar o **CEP**. Para corrigir, você pode digitar por cima.

#### Campo Cidade

- **O que é:** a cidade do endereço.
- **Como preencher:** é preenchido sozinho ao consultar o **CEP**. Para corrigir, você pode digitar por cima.

#### Campo UF

- **O que é:** a sigla do estado (ex.: SP, RJ, MG).
- **Como preencher:** é preenchido sozinho ao consultar o **CEP** e não pode ser digitado.

### Bloco Contato

Aqui você informa os telefones do administrador.

#### Campo Telefone

- **O que é:** o telefone fixo da pessoa.
- **Como preencher:** digite os números. Ao sair do campo, o sistema formata sozinho (ex.: (11) 1234-5678).

#### Campo Celular

- **O que é:** o celular da pessoa.
- **Como preencher:** digite os números. Ao sair do campo, o sistema formata sozinho (ex.: (11) 91234-5678).

### Botão Cancelar

- **O que faz:** fecha a janela sem salvar nada.
- **Como usar:** clique em **Cancelar**, no canto inferior direito da janela.
- **Quando usar:** quando desistir do cadastro ou da edição. Nada do que você digitou será salvo.

### Botão Salvar

- **O que faz:** grava as informações do administrador.
- **Como usar:** depois de preencher todos os campos obrigatórios, clique em **Salvar**, no canto inferior direito da janela.
- **O que acontece:** 
  - Se for um cadastro novo, o administrador é criado como **Ativo** e aparece na lista.
  - Se for uma edição, os dados são atualizados.
- **Dica:** se algum campo obrigatório estiver errado ou faltando, o sistema avisa o que precisa ser corrigido e nada é salvo.
