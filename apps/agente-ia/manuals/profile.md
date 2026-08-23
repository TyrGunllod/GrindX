# Manual do Módulo Meu Perfil

O módulo **Meu Perfil** permite que o usuário visualize e edite seus dados pessoais, altere a senha e ajuste as preferências de aparência do sistema.

## Visão Geral da Tela

Ao abrir o módulo, o usuário vê o título "Meu Perfil" com o subtítulo "Gerencie seus dados pessoais e preferências." e, ao lado do título, o número da versão do sistema.

A tela é dividida em duas áreas principais:

1. **Meus Dados** — um cartão com o formulário de dados pessoais.
2. **Configurações** — um cartão com dois botões: **Alterar Senha** e **Preferências**.

## Meus Dados

Este cartão exibe os dados do usuário carregados automaticamente ao abrir o módulo.

Alguns campos são somente leitura e não podem ser editados:

- **Nome de Usuário**
- **Perfil** (mostra o tipo de acesso: Administrador, Operador ou Leitura)
- **Nome Completo**
- **Cargo** (preenchido automaticamente ao consultar o C.B.O.)
- **Endereço, Bairro, Cidade e UF** (preenchidos automaticamente ao consultar o CEP)

Os demais campos podem ser editados pelo usuário:

- **Código**
- **C.B.O** (com botão de busca)
- **Salário Base**
- **Departamento**
- **Classificação** (lista de opções: Junior, Pleno, Senior, I, II, III, IV e V)
- **CPF**
- **RG**
- **Nº**
- **CEP** (com botão de busca)
- **Telefone**
- **Celular**
- **E-mail** (obrigatório)

Os campos CPF, RG, CEP, Telefone e Celular são formatados automaticamente (máscara) quando o usuário sai do campo. O salário é exibido no formato brasileiro (por exemplo, 1.234,56).

Para salvar as alterações, o usuário clica no botão **Salvar** no final do cartão. Ao salvar com sucesso, aparece a mensagem "Dados salvos com sucesso!". Caso o e-mail informado já esteja em uso, uma mensagem de erro é exibida abaixo do campo E-mail.

## Consulta de C.B.O

Ao lado do campo C.B.O existe um botão de busca (ícone de lupa). Ao clicar nele (ou ao sair do campo após digitar o código), o sistema consulta o código informado e preenche automaticamente o campo **Cargo** com a descrição correspondente.

Se o código não for encontrado, o usuário vê a mensagem "CBO não encontrado."

## Consulta de CEP

Ao lado do campo CEP existe um botão de busca (ícone de lupa). Ao clicar nele (ou ao sair do campo após digitar um CEP válido), o sistema preenche automaticamente os campos **Endereço**, **Bairro**, **Cidade** e **UF**.

Se o CEP não for encontrado, o usuário vê a mensagem "CEP não encontrado."

## Alterar Senha

Ao clicar no botão **Alterar Senha** (no cartão Configurações), abre-se uma janela com três campos:

1. **Senha Atual**
2. **Nova Senha** (mínimo de 6 caracteres)
3. **Confirmar Nova Senha**

O usuário deve preencher os três campos e clicar em **Salvar**.

O sistema valida as informações:

- Se algum campo estiver vazio, exibe "Preencha todos os campos de senha."
- Se a nova senha não tiver ao menos 6 caracteres, exibe "Nova senha deve ter no mínimo 6 caracteres."
- Se a confirmação não for igual à nova senha, exibe "Nova senha e confirmação não conferem."
- Se a senha atual estiver incorreta, exibe uma mensagem de erro.

Após salvar com sucesso, a janela fecha e a página é atualizada. Para desistir, o usuário clica em **Cancelar** ou clica fora da janela.

## Preferências

Ao clicar no botão **Preferências** (no cartão Configurações), abre-se uma janela com as seguintes opções:

- **Tema**: escolher entre **Claro** e **Escuro**.
- **Layout Desktop**: escolher entre **Topbar** e **Sidebar**.
- **Layout Celular / Tablet**: escolher entre **Topbar** e **Sidebar** — aplicado automaticamente em telas menores que 768px.

O usuário clica na opção desejada (ela fica destacada) e, em seguida, clica em **Salvar**. As preferências são aplicadas imediatamente e a página é atualizada.

Para desistir, o usuário clica em **Cancelar** ou clica fora da janela.
