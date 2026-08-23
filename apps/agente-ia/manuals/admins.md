# Manual do Módulo Administradores

Este manual explica, do ponto de vista de quem usa (você), tudo o que é possível ver e fazer no módulo **Administradores** do ERP GrindX. Aqui você pode **cadastrar**, **consultar**, **editar**, **ativar** e **desativar** os administradores do sistema — ou seja, as pessoas com o perfil mais alto de acesso.

> **Quem pode usar:** apenas usuários com perfil de **Administrador** acessam este módulo. Você precisa estar logado no sistema; se sua sessão estiver expirada, a tela não carrega os dados e mostra a mensagem "Sessão expirada. Faça login novamente.".

---

## Tela Principal (Lista de Administradores)

Quando você abre o módulo, vê:

- O título **Administradores** no topo.
- Ao lado do título, um selo com a **versão do sistema**.
- Logo abaixo, a descrição "Gerenciamento de administradores do sistema".
- No canto direito, o botão **Novo Administrador**.
- Mais abaixo, a **tabela** com todos os administradores cadastrados.

Enquanto os dados são buscados, você vê um indicador de carregamento com a mensagem "Carregando administradores...". Se não houver nenhum administrador cadastrado, a tabela mostra "Nenhum administrador encontrado." no centro.

### Botão do topo

- **Novo Administrador** (botão azul com o ícone de **+**) — abre a janela de cadastro em branco, para criar um novo administrador. Em telas pequenas (celular), o texto some e fica apenas o ícone **+**.

### Tabela de Administradores

A tabela tem estas colunas:

- **Administrador** — mostra a foto (avatar) e o **nome completo** da pessoa. O avatar é uma imagem gerada automaticamente a partir do nome, com fundo vermelho e as iniciais em branco.
- **E-mail** — mostra o e-mail do administrador. **Esta coluna fica oculta em telas pequenas** (celular).
- **Status** — mostra um selo indicando se o administrador está **Ativo** (verde) ou **Inativo** (cinza).
- **Ações** — mostra os botões de ação disponíveis para cada linha.

Em telas pequenas, a tabela vira uma lista de cartões, um para cada administrador, facilitando a visualização no celular.

### Selo de Status (Ativo/Inativo)

O selo de status é **clicável**. Ao clicar, você alterna o estado do administrador:

- Se está **Ativo**, clicar **desativa** o administrador (ele vira **Inativo**).
- Se está **Inativo**, clicar **ativa** o administrador (ele vira **Ativo**).

A ação acontece na hora e uma mensagem confirma o resultado, como "Administrador desativado com sucesso." ou "Administrador ativado com sucesso.". Ao passar o mouse sobre o selo, aparece uma dica: "Clique para desativar" ou "Clique para ativar". Não há janela de confirmação — o clique já efetiva a mudança.

### Botão da coluna Ações

- **Editar** (ícone de lápis) — abre a janela de edição já preenchida com os dados atuais do administrador, para você alterar o que precisar.

---

## Janela "Cadastrar Administrador"

**Como abrir:** clique no botão **Novo Administrador** no topo da tela.

A janela abre com o título **Cadastrar Administrador**, todos os campos em branco, e o cursor já posicionado no campo **Nome Completo**. Ela é dividida em cinco blocos: **Dados do Administrador**, **Dados Profissionais**, **Documentos**, **Endereço** e **Contato**. Se a janela for maior que a tela, dá para rolar o conteúdo para ver todos os campos.

### Dados do Administrador

- **Nome de Usuário** — nome de login do administrador. É **obrigatório** e deve ter no mínimo 3 caracteres (máximo de 50). Enquanto você digita o **Nome Completo**, este campo é preenchido **automaticamente** com uma sugestão: o primeiro nome + as iniciais dos demais nomes, ignorando conectivos como "de", "da", "do", "dos", "das" e "e". Por exemplo, "João da Silva Santos" vira "joãos". Se quiser usar outro nome, clique no campo e digite — a partir do momento em que você clica nele, a sugestão automática é desativada (se você limpar o campo, a geração automática volta a funcionar).
- **Perfil** — mostra o perfil de acesso. Aqui ele vem **fixado como "Administrador"** e não pode ser alterado (o campo fica desabilitado).
- **Nome Completo** — nome completo da pessoa. **Obrigatório**, com no mínimo 2 caracteres (máximo de 100). É o primeiro campo que recebe o foco quando a janela abre.
- **E-mail** — e-mail do administrador. **Obrigatório** e precisa conter o símbolo `@`.
- **Senha** — senha de acesso. No cadastro é **obrigatória** e deve ter no mínimo 6 caracteres. Abaixo do campo aparece a dica "Preencha apenas se deseja alterar a senha."

### Dados Profissionais

- **Código** — campo livre, normalmente usado para um código interno ou matrícula da pessoa. Opcional.
- **C.B.O** — código da Classificação Brasileira de Ocupações. Ao lado, há um botão de busca (ícone de lupa). Veja como usar na seção **Botões de busca** abaixo.
- **Salário Base** — valor do salário. Aceita casas decimais e é formatado automaticamente no padrão brasileiro (ex.: 1.500,00). Ao clicar no campo, a formatação é removida para facilitar a digitação, e ao sair do campo ela é aplicada de novo.
- **Departamento** — departamento ao qual o administrador pertence. Opcional.
- **Cargo** — descrição do cargo. Campo **somente leitura**: ele é preenchido automaticamente quando você consulta o **C.B.O**.
- **Classificação** — lista suspensa com o nível profissional. Opções: **Junior**, **Pleno**, **Senior**, **I**, **II**, **III**, **IV** e **V**. (A opção "Selecione..." é apenas o valor vazio inicial.)

### Documentos

- **CPF** — número do CPF. Aceita só números e, ao sair do campo, é formatado automaticamente no padrão `000.000.000-00`.
- **RG** — número do RG. Ao sair do campo, é formatado automaticamente no padrão `00.000.000-0`.

### Endereço

- **Endereço** — nome da rua/logradouro. Campo **somente leitura**: é preenchido automaticamente pela busca do CEP.
- **Nº** — número do endereço (máximo de 6 caracteres). Opcional.
- **CEP** — código postal. Aceita só números e, ao sair do campo, é formatado automaticamente no padrão `00000-000`. Ao lado, há um botão de busca (ícone de lupa).
- **Bairro** — bairro. Campo **somente leitura** (preenchido pela busca do CEP).
- **Cidade** — cidade. Campo **somente leitura** (preenchido pela busca do CEP).
- **UF** — sigla do estado. Campo **somente leitura** (preenchido pela busca do CEP).

### Contato

- **Telefone** — telefone fixo. Ao sair do campo, é formatado automaticamente no padrão `(00) 0000-0000`.
- **Celular** — celular. Ao sair do campo, é formatado automaticamente no padrão `(00) 00000-0000`.

### Botões de busca (dentro da janela)

- **Buscar CBO** (ícone de lupa ao lado do campo **C.B.O**) — consulta o código CBO digitado. Para funcionar, o código precisa ter pelo menos 4 números. Você pode acionar a busca clicando na lupa, pressionando **Enter** dentro do campo, ou simplesmente saindo do campo. Se o código existir, o campo **Cargo** é preenchido automaticamente com a descrição da ocupação. Se não existir, aparece a mensagem "CBO não encontrado.". Se houver um problema na consulta, aparece "Erro ao consultar CBO.".
- **Buscar CEP** (ícone de lupa ao lado do campo **CEP**) — consulta o CEP digitado. Para funcionar, o CEP precisa ter os **8 números**. Você aciona a busca clicando na lupa, pressionando **Enter** no campo, ou saindo do campo. Se o CEP existir, os campos **Endereço**, **Bairro**, **Cidade** e **UF** são preenchidos automaticamente. Se não existir, aparece "CEP não encontrado.". Se houver um problema na consulta, aparece "Erro ao consultar CEP.".

### Botões do rodapé da janela

- **Cancelar** — fecha a janela **sem salvar** nada. Todos os campos preenchidos são descartados e limpos.
- **Salvar** — confere os campos e grava o novo administrador. Em caso de sucesso, a janela fecha e o novo administrador aparece na tabela (com a mensagem "Administrador salvo com sucesso."). Se houver problema, uma mensagem de erro aparece sem fechar a janela.

### Validações que aparecem ao Salvar

Antes de gravar, o sistema confere o formulário. Se algo estiver errado, você vê uma destas mensagens (como aviso no canto da tela):

- "Nome de usuário deve ter no mínimo 3 caracteres."
- "Nome completo é obrigatório."
- "E-mail inválido."
- "Senha deve ter no mínimo 6 caracteres."

Essas mensagens somem sozinhas depois de alguns segundos.

---

## Janela "Editar Administrador"

**Como abrir:** clique no ícone de **Editar** (lápis) na linha do administrador desejado na tabela.

A janela abre com o título **Editar Administrador** e **todos os campos já preenchidos** com os dados atuais da pessoa. Os campos e blocos são os mesmos do cadastro (veja a seção anterior). As diferenças são:

- **Senha** — **não é obrigatória**. Deixe em branco para manter a senha atual; preencha somente se quiser trocá-la (mínimo de 6 caracteres). A dica "Preencha apenas se deseja alterar a senha." fica visível para orientar.
- **Nome de Usuário** — já vem preenchido e pode ser editado manualmente (a geração automática fica desativada).

Você pode refazer as buscas de **CBO** e **CEP** normalmente durante a edição para atualizar os campos **Cargo** e de endereço.

### Botões do rodapé da janela

- **Cancelar** — fecha a janela **sem salvar**. Os dados originais são mantidos (as alterações feitas são descartadas).
- **Salvar** — grava as alterações do administrador. Em caso de sucesso, a janela fecha e a tabela é atualizada (mensagem "Administrador salvo com sucesso."). Em caso de erro, uma mensagem é exibida e a janela permanece aberta.

---

## Como o sistema se comporta (dicas de uso)

- **Foco inicial:** ao abrir a janela de cadastro, o cursor já vai para o campo **Nome Completo**.
- **Fechar a janela:** além do botão **Cancelar**, você pode fechar a janela pressionando a tecla **Esc**.
- **Navegação por teclado:** pressionar **Enter** em um campo pula para o próximo campo da janela (exceto nos campos C.B.O e CEP, onde o Enter aciona a busca). A tecla **Tab** também percorre os campos e, ao chegar no último, volta para o primeiro.
- **Máscaras automáticas:** os campos de CPF, RG, CEP, Telefone, Celular e Salário se formatam sozinhos quando você sai deles, e liberam a formatação quando você clica neles para editar. Não se preocupe em digitar traços ou pontos — digite só os números.
- **Mensagens (toasts):** confirmações e avisos aparecem como pequenas notificações no canto da tela e desaparecem sozinhas depois de alguns segundos. Elas podem ser de sucesso (verde), aviso (amarelo) ou erro (vermelho).

---

## Resumo de Botões e Ícones do Módulo

| Botão / Ícone | Onde fica | O que faz |
|---|---|---|
| **+** (ícone de adição) | Botão "Novo Administrador" no topo | Abre a janela de cadastro de um novo administrador |
| **Selo de Status** (Ativo/Inativo) | Coluna "Status" da tabela | Alterna o administrador entre ativo e inativo ao clicar |
| **Lápis** | Coluna "Ações" da tabela | Abre a janela de edição com os dados do administrador |
| **Lupa** (ao lado de C.B.O) | Dentro da janela de cadastro/edição | Consulta o CBO e preenche o campo Cargo |
| **Lupa** (ao lado de CEP) | Dentro da janela de cadastro/edição | Consulta o CEP e preenche os campos de endereço |
| **Cancelar** | Rodapé da janela | Fecha a janela sem salvar |
| **Salvar** | Rodapé da janela | Valida e grava o cadastro ou a edição |

> **Lembre-se:** não existe botão para **excluir** um administrador neste módulo. Para tirar um administrador de uso, basta **desativá-lo** clicando no selo de status.
