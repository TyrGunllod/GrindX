# Manual do Módulo Usuários

Este manual descreve, do ponto de vista do usuário final, tudo o que é possível ver e fazer no módulo **Usuários** do ERP GrindX. Ele cobre a tela principal de listagem, o cadastro e a edição de usuários, e a gestão de permissões de acesso.

## Tela Principal — Lista de Usuários

Ao abrir o módulo **Usuários**, você vê a tela "Gerenciamento de Usuários", com o subtítulo "Controle de acesso e permissões modulares". Nela há um cabeçalho, um botão para criar usuários e uma tabela com todos os usuários cadastrados (exceto administradores).

### Cabeçalho

- **Novo Usuário** — abre a janela de cadastro em branco para criar um novo usuário.

### Tabela de Usuários

A tabela lista os usuários com as seguintes colunas:

- **Usuário** — mostra a foto/avatar do usuário e o nome completo.
- **E-mail** — mostra o e-mail do usuário (esta coluna fica oculta em telas pequenas, como celulares).
- **Perfil** — mostra o perfil do usuário (ex.: LEITURA ou OPERADOR) em uma etiqueta colorida.
- **Status** — mostra se o usuário está Ativo ou Inativo, em uma etiqueta clicável.
- **Aprovador** — mostra se o usuário é aprovador (Sim) ou não (Não), em uma etiqueta clicável.
- **Ações** — botões para editar o usuário e gerenciar as permissões dele.

### Botões e ações da tabela

- **Etiqueta de Status (Ativo/Inativo)** — clicar sobre ela alterna o status do usuário. Se está "Ativo", clicar desativa; se está "Inativo", clicar ativa. Após a ação, uma mensagem confirma a alteração. O texto de dica (ao passar o mouse) também indica a ação.
- **Etiqueta de Aprovador (Sim/Não)** — clicar sobre ela alterna se o usuário é aprovador. Se está "Sim", clicar remove a condição de aprovador; se está "Não", clicar torna o usuário aprovador.
- **Editar (ícone de lápis)** — abre a janela do usuário já preenchida com os dados atuais, permitindo alterar e salvar.
- **Permissões (ícone de escudo)** — abre a janela "Gerenciar Permissões" daquele usuário.

## Cadastro de Usuário (janela "Cadastrar Usuário")

Para abrir, clique em **Novo Usuário** no topo da tela. A janela abre com os campos em branco e o título "Cadastrar Usuário". Preencha os campos na ordem abaixo e clique em **Salvar**.

### Dados do Usuário

- **Nome de Usuário** — nome de login do usuário. Mínimo de 3 caracteres e máximo de 50. Este campo é preenchido automaticamente a partir do **Nome Completo** (primeiro nome + iniciais dos demais nomes, ignorando conectivos como "de", "da", "do"). Se preferir, clique no campo e digite um nome de usuário personalizado.
- **Perfil** — lista suspensa com o perfil do usuário. Opções disponíveis: **Leitura** e **Operador**. (O perfil Administrador não aparece nesta lista.)
- **Nome Completo** — nome completo da pessoa. Obrigatório, com no mínimo 2 caracteres. Ao digitar, gera automaticamente o **Nome de Usuário**.
- **E-mail** — endereço de e-mail do usuário. Obrigatório e deve conter "@".
- **Senha** — senha de acesso do usuário. No cadastro é obrigatória e deve ter no mínimo 6 caracteres. A dica "Preencha apenas se deseja alterar a senha" aparece apenas quando você está editando um usuário existente.

### Dados Profissionais

- **Código** — código interno/matrícula do usuário (opcional).
- **C.B.O** — código da Classificação Brasileira de Ocupações. Ao digitar o código e sair do campo (ou clicar no botão de busca), o sistema preenche automaticamente o campo **Cargo** com a descrição da ocupação.
  - **Buscar CBO (botão de lupa)** — consulta o código CBO digitado e preenche o campo **Cargo** com a descrição correspondente. Se o código não for encontrado, exibe uma mensagem de erro.
- **Salário Base** — valor do salário do usuário. Aceita casas decimais.
- **Departamento** — departamento ao qual o usuário pertence (opcional).
- **Cargo** — descrição do cargo. Este campo é **somente leitura**: é preenchido automaticamente pela busca do CBO.
- **Classificação** — lista suspensa com o nível do usuário. Opções: **Junior**, **Pleno**, **Senior**, **I**, **II**, **III**, **IV** e **V**.

### Documentos

- **CPF** — número do CPF. Ao sair do campo, recebe a máscara automática (000.000.000-00).
- **RG** — número do RG. Ao sair do campo, recebe a máscara automática (00.000.000-0).

### Endereço

- **Endereço** — nome da rua/logradouro. Campo **somente leitura**: é preenchido automaticamente pela busca do CEP.
- **Nº** — número da residência/estabelecimento (máximo de 6 caracteres).
- **CEP** — código postal. Ao digitar o CEP e sair do campo (ou clicar no botão de busca), o sistema preenche automaticamente os campos **Endereço**, **Bairro**, **Cidade** e **UF**.
  - **Buscar CEP (botão de lupa)** — consulta o CEP digitado e preenche os campos de endereço. Se o CEP não for encontrado, exibe uma mensagem de erro.
- **Bairro** — bairro do endereço. Campo **somente leitura** (preenchido pela busca do CEP).
- **Cidade** — cidade do endereço. Campo **somente leitura** (preenchido pela busca do CEP).
- **UF** — unidade federativa (sigla do estado). Campo **somente leitura** (preenchido pela busca do CEP).

### Contato

- **Telefone** — telefone fixo. Ao sair do campo, recebe a máscara automática (00) 0000-0000.
- **Celular** — telefone celular. Ao sair do campo, recebe a máscara automática (00) 00000-0000.

### Botões da janela de cadastro

- **Cancelar** — fecha a janela sem salvar, descartando todas as alterações feitas.
- **Salvar** — grava o novo usuário, fecha a janela e atualiza a tabela. Exibe uma mensagem de confirmação "Usuário salvo com sucesso".

## Edição de Usuário (janela "Editar Usuário")

Para abrir, clique no botão **Editar (ícone de lápis)** na linha do usuário desejado. A janela abre com o título "Editar Usuário" e todos os campos preenchidos com os dados atuais. Os campos são os mesmos do cadastro (ver seção acima), com duas diferenças:

- A **Senha** não é obrigatória. Deixe em branco para manter a senha atual; preencha somente se quiser alterá-la (mínimo de 6 caracteres).
- O **Nome de Usuário** não é mais gerado automaticamente ao digitar o nome completo — ele já está preenchido e pode ser editado manualmente.

### Botões da janela de edição

- **Cancelar** — fecha a janela sem salvar, descartando as alterações.
- **Salvar** — grava as alterações, fecha a janela e atualiza a tabela. Exibe a mensagem "Usuário salvo com sucesso".

## Gerenciar Permissões (janela "Gerenciar Permissões")

Para abrir, clique no botão **Permissões (ícone de escudo)** na linha do usuário desejado. A janela mostra a lista de módulos e abas do sistema organizados em grupos, cada um com uma caixa de seleção (checkbox). Uma caixa marcada significa que o usuário tem acesso àquele módulo.

### Como preencher

1. Para liberar um módulo ao usuário, marque a caixa de seleção ao lado do nome do módulo.
2. Para remover o acesso, desmarque a caixa.
3. Módulos com a etiqueta **Admin** são restritos ao perfil Administrador e não podem ser liberados a usuários comuns.
4. Em cada grupo (aba), há um atalho **Selecionar todos** que marca todas as caixas daquele grupo de uma vez. Quando todas já estão marcadas, o atalho muda para **Limpar**, que desmarca todas as caixas do grupo.
5. Subgrupos (pastas) podem conter módulos adicionais; as caixas funcionam da mesma forma.

### Botões da janela de permissões

- **Cancelar** — fecha a janela sem salvar, descartando as alterações de permissão.
- **Salvar Permissões** — grava as permissões selecionadas para o usuário e fecha a janela. Exibe a mensagem "Permissões atualizadas com sucesso".
