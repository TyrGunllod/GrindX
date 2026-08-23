# Manual do Módulo Administradores

## Lista de Administradores

Ao abrir o módulo Administradores, o sistema carrega a lista de todos os administradores cadastrados. Cada linha da tabela mostra:

- **Administrador**: foto de perfil e nome completo.
- **E-mail**: e-mail do administrador.
- **Status**: um selo indicando se o administrador está **Ativo** ou **Inativo**.
- **Ações**: botão de editar.

Enquanto a lista carrega, aparece a mensagem "Carregando administradores...". Se não houver nenhum administrador, a tabela mostra "Nenhum administrador encontrado.".

No topo da tela há o botão **Novo Administrador**, usado para abrir o cadastro.

## Cadastrar Novo Administrador

1. Clique em **Novo Administrador**.
2. Será aberta uma janela com o título "Cadastrar Administrador".
3. Preencha os dados solicitados e clique em **Salvar**.

### Dados do Administrador

- **Nome de Usuário**: nome usado para acesso ao sistema. É gerado automaticamente a partir do nome completo, mas pode ser editado. Deve ter no mínimo 3 caracteres.
- **Perfil**: campo fixo, sempre "Administrador".
- **Nome Completo**: obrigatório, com no mínimo 2 caracteres.
- **E-mail**: obrigatório e precisa conter "@".
- **Senha**: obrigatória no cadastro, com no mínimo 6 caracteres.

### Dados Profissionais

- **Código**: código interno do administrador.
- **C.B.O**: código da ocupação, com botão de busca.
- **Salário Base**: valor do salário, formatado automaticamente.
- **Departamento**: departamento ao qual pertence.
- **Cargo**: preenchido automaticamente ao consultar o C.B.O.
- **Classificação**: opcional entre Junior, Pleno, Senior, I, II, III, IV e V.

### Documentos

- **CPF**: com máscara automática.
- **RG**: com máscara automática.

### Endereço

- **Endereço**: preenchido automaticamente ao consultar o CEP.
- **Nº**: número do local.
- **CEP**: com botão de busca e máscara automática.
- **Bairro**, **Cidade** e **UF**: preenchidos automaticamente ao consultar o CEP.

### Contato

- **Telefone**: com máscara automática.
- **Celular**: com máscara automática.

Ao salvar, o administrador é criado com status **Ativo** e a lista é atualizada.

## Editar Administrador

1. Na lista, clique no botão de editar (ícone de lápis) do administrador desejado.
2. A janela abre com o título "Editar Administrador" e os campos preenchidos com os dados atuais.
3. Altere o que for necessário e clique em **Salvar**.

Na edição, o campo **Senha** é opcional: deixe em branco para manter a senha atual. Se preenchido, a senha será alterada (mínimo 6 caracteres).

## Ativar e Desativar Administrador

Para mudar o status de um administrador, clique diretamente no selo de **Status** na linha correspondente:

- Clique em um administrador **Ativo** para desativá-lo.
- Clique em um administrador **Inativo** para ativá-lo.

O status é atualizado na hora e uma mensagem de confirmação é exibida.

## Buscas Automáticas

Alguns campos contam com busca automática ao preencher e sair do campo (ou clicar no botão de lupa):

- **CEP**: preenche automaticamente Endereço, Bairro, Cidade e UF. Se o CEP não for encontrado, aparece o aviso "CEP não encontrado.".
- **C.B.O**: preenche automaticamente o campo Cargo com a descrição da ocupação. Se não for encontrado, aparece o aviso "CBO não encontrado.".

## Cancelar e Fechar

Em qualquer momento, o botão **Cancelar** (ou o fechamento da janela) descarta as alterações e limpa o formulário.
