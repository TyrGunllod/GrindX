# Manual do Módulo Administradores

Este manual descreve, do ponto de vista do usuário final, como utilizar o módulo **Administradores** do ERP GrindX. Ele serve para cadastrar, consultar, editar, ativar e desativar os administradores do sistema.

## Tela Principal (Lista de Administradores)

Ao abrir o módulo, você vê o título **Administradores**, o subtítulo "Gerenciamento de administradores do sistema" e uma tabela com todos os administradores cadastrados.

A tabela possui as seguintes colunas:

- **Administrador** — mostra a foto (avatar) e o nome completo do administrador.
- **E-mail** — mostra o e-mail de cada administrador (não aparece em telas pequenas).
- **Status** — mostra um selo indicando se o administrador está **Ativo** (verde) ou **Inativo** (cinza).
- **Ações** — mostra os botões de ação disponíveis para cada linha.

### Botões da Tela Principal

- **Novo Administrador** (botão azul com o ícone de `+`, no topo da tela) — abre a janela de cadastro para criar um novo administrador.

### Botões da Coluna "Ações"

- **Editar** (ícone de lápis) — abre a janela de cadastro preenchida com os dados do administrador selecionado, para que você possa alterá-los.

### Botão da Coluna "Status"

- **Selo de Status** (texto "Ativo" ou "Inativo") — ao clicar, alterna o status do administrador: se está **Ativo**, passa para **Inativo**; se está **Inativo**, passa para **Ativo**. Passe o mouse sobre o selo para ver a dica "Clique para desativar" ou "Clique para ativar".

> **Permissão:** apenas usuários com o perfil de Administrador conseguem acessar e operar este módulo. Sem uma sessão válida (login), a tela não carrega os dados e exibe a mensagem para fazer login novamente.

---

## Janela "Cadastrar Administrador"

Esta janela é aberta ao clicar em **Novo Administrador**. Ela permite informar todos os dados de um novo administrador.

A janela é dividida nas seguintes seções: **Dados do Administrador**, **Dados Profissionais**, **Documentos**, **Endereço** e **Contato**.

### Dados do Administrador

- **Nome de Usuário** — campo de texto que identifica o administrador no sistema. É obrigatório e deve ter no mínimo 3 caracteres. Enquanto você digita o **Nome Completo**, este campo é preenchido automaticamente com um nome de usuário sugerido (primeiro nome + iniciais dos demais nomes). Se quiser definir um nome diferente, basta clicar no campo e digitar; a partir daí a sugestão automática é desativada.
- **Perfil** — campo de seleção que já vem fixado como **Administrador**. Não pode ser alterado.
- **Nome Completo** — campo de texto obrigatório (mínimo 2 caracteres). Digite o nome completo da pessoa. É o campo que fica em foco quando a janela abre.
- **E-mail** — campo de texto obrigatório. Digite um e-mail válido (precisa conter o símbolo `@`).
- **Senha** — campo de texto para a senha. No cadastro de um novo administrador, é obrigatória e deve ter no mínimo 6 caracteres. A dica "Preencha apenas se deseja alterar a senha" é exibida, mas na criação a senha é obrigatória.

### Dados Profissionais

- **Código** — campo de texto livre para informar um código do administrador.
- **C.B.O** — campo de texto para o código CBO (Classificação Brasileira de Ocupações). Possui um botão de busca (ícone de lupa) ao lado.
- **Salário Base** — campo numérico para informar o salário. Aceita valores com vírgula decimal e formata automaticamente no padrão brasileiro (ex.: "1.500,00").
- **Departamento** — campo de texto livre para informar o departamento.
- **Cargo** — campo de texto somente leitura. É preenchido automaticamente com a descrição do cargo ao consultar o CBO.
- **Classificação** — campo de seleção com as opções: **Junior**, **Pleno**, **Senior**, **I**, **II**, **III**, **IV** e **V**. Use para indicar o nível do administrador.

### Documentos

- **CPF** — campo de texto para o CPF. Formata automaticamente no padrão `000.000.000-00`.
- **RG** — campo de texto para o RG. Formata automaticamente no padrão `00.000.000-0`.

### Endereço

- **Endereço** — campo de texto somente leitura. É preenchido automaticamente com o logradouro ao consultar o CEP.
- **Nº** — campo de texto para informar o número do endereço (até 6 caracteres).
- **CEP** — campo de texto para o CEP. Formata automaticamente no padrão `00000-000`. Possui um botão de busca (ícone de lupa) ao lado.
- **Bairro** — campo de texto somente leitura. Preenchido automaticamente pelo CEP.
- **Cidade** — campo de texto somente leitura. Preenchido automaticamente pelo CEP.
- **UF** — campo de texto somente leitura. Preenchido automaticamente pelo CEP.

### Contato

- **Telefone** — campo de texto para o telefone fixo. Formata automaticamente no padrão `(00) 0000-0000`.
- **Celular** — campo de texto para o celular. Formata automaticamente no padrão `(00) 00000-0000`.

### Botões de Busca (dentro da janela)

- **Buscar CBO** (ícone de lupa ao lado do campo C.B.O) — consulta o código CBO digitado e preenche automaticamente o campo **Cargo** com a descrição correspondente. Se o código não existir, mostra uma mensagem de erro.
- **Buscar CEP** (ícone de lupa ao lado do campo CEP) — consulta o CEP digitado e preenche automaticamente os campos **Endereço**, **Bairro**, **Cidade** e **UF**. Se o CEP não existir, mostra uma mensagem de erro.

### Botões do Rodapé da Janela

- **Cancelar** — fecha a janela sem salvar as alterações. Todos os campos são limpos.
- **Salvar** — valida os campos e grava o novo administrador. Em caso de sucesso, a janela fecha e o administrador aparece na tabela. Se houver erro de preenchimento ou de gravação, uma mensagem é exibida.

### Validações exibidas ao Salvar

- "Nome de usuário deve ter no mínimo 3 caracteres."
- "Nome completo é obrigatório."
- "E-mail inválido."
- "Senha deve ter no mínimo 6 caracteres."

---

## Janela "Editar Administrador"

Esta janela é aberta ao clicar no ícone de **Editar** de um administrador na tabela. Ela possui os mesmos campos da janela de cadastro, mas já vem preenchida com os dados atuais do administrador.

A principal diferença é a **Senha**: na edição, a senha **não é obrigatória**. A dica "Preencha apenas se deseja alterar a senha" orienta que o campo deve ser deixado em branco caso você não queira mudar a senha. Se preencher, a senha será atualizada.

Os campos **Cargo**, **Endereço**, **Bairro**, **Cidade** e **UF** (somente leitura) também podem ser recarregados usando os botões de busca de CBO e CEP.

### Botões do Rodapé da Janela

- **Cancelar** — fecha a janela sem salvar as alterações. Os dados anteriores são mantidos.
- **Salvar** — valida os campos e grava as alterações do administrador. Em caso de sucesso, a janela fecha e a tabela é atualizada com os novos dados.

---

## Resumo de Botões do Módulo

- **Novo Administrador** — abre a janela de cadastro de um novo administrador.
- **Editar** (lápis) — abre a janela de edição com os dados do administrador selecionado.
- **Selo de Status** — alterna entre Ativo e Inativo ao clicar.
- **Buscar CBO** (lupa) — preenche o campo Cargo a partir do código CBO.
- **Buscar CEP** (lupa) — preenche os campos de endereço a partir do CEP.
- **Cancelar** — fecha a janela sem salvar.
- **Salvar** — valida e grava os dados do administrador.
