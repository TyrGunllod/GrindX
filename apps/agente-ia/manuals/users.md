# Manual do Módulo Usuários

Neste módulo você gerencia as pessoas que usam o sistema (chamadas de **usuários**): cria novos usuários, edita os dados, controla se a pessoa está ativa ou inativa, define quem é aprovador e libera o acesso aos módulos do sistema.

O módulo é dividido em três áreas:

- **Tela principal**: a lista de usuários com o botão "Novo Usuário".
- **Janela de Cadastro/Edição**: onde você preenche os dados da pessoa.
- **Janela de Permissões**: onde você marca quais módulos a pessoa pode usar.

---

## Tela Principal — Gerenciamento de Usuários

Ao abrir o módulo **Usuários** no menu lateral, você vê a tela principal com:

- O título **"Gerenciamento de Usuários"**.
- A **versão do sistema** ao lado do título.
- O botão **"Novo Usuário"** no canto superior direito.
- A tabela com a lista de usuários cadastrados.

Quando a tela abre, ela carrega automaticamente os usuários. Enquanto isso, aparece o aviso **"Carregando usuários..."**. Se não houver nenhum usuário cadastrado, aparece a mensagem **"Nenhum usuário encontrado."**.

Cada linha da tabela representa um usuário e mostra as colunas a seguir.

### Campo Usuário

- Mostra a **foto (avatar)** e o **nome completo** da pessoa.
- O avatar é gerado automaticamente com as iniciais do nome; não é preciso cadastrar foto.

### Campo E-mail

- Mostra o e-mail de login da pessoa.
- Em telas pequenas (celular), essa coluna fica oculta para facilitar a leitura.

### Campo Perfil

- Mostra o perfil de acesso da pessoa em um selo colorido, por exemplo **"LEITURA"**.
- O selo apenas informa; a alteração do perfil é feita na janela de edição (campo **Perfil**).

### Campo Status (selo clicável)

- Mostra se o usuário está **"Ativo"** (selo verde) ou **"Inativo"** (selo cinza).
- **O selo é clicável**: clique em "Ativo" para desativar a pessoa, ou em "Inativo" para reativar.
- Ao clicar, o sistema salva a mudança, atualiza a tabela na hora e mostra um aviso confirmando ("Usuário desativado/ativado com sucesso").
- Uma pessoa inativa continua cadastrada, mas não poderá mais acessar o sistema.

### Campo Aprovador (selo clicável)

- Mostra se a pessoa é **aprovador** ("Sim") ou não ("Não").
- **O selo é clicável**: clique em "Sim" para remover a função de aprovador, ou em "Não" para tornar a pessoa aprovador.
- Ao clicar, a mudança é salva na hora e a tabela é atualizada.

### Botão Novo Usuário

- **Novo Usuário** — abre a janela **"Cadastrar Usuário"** para você preencher os dados de uma pessoa nova.
- Também existe a versão com apenas o ícone de **+** (em telas pequenas).

### Ícone de lápis (Editar)

- **Lápis** — abre a janela **"Editar Usuário"** com os dados daquela pessoa já preenchidos.
- Você pode alterar qualquer informação e clicar em **Salvar** para gravar.

### Ícone de escudo (Permissões)

- **Escudo** — abre a janela **"Gerenciar Permissões"** daquele usuário.
- É onde você marca quais módulos do sistema a pessoa pode usar.

---

## Janela de Cadastro e Edição de Usuário

Essa janela é usada para **criar** um usuário novo e para **editar** um usuário existente.

- **Como abrir para criar**: clique no botão **"Novo Usuário"** na tela principal. O título da janela será **"Cadastrar Usuário"**.
- **Como abrir para editar**: clique no **ícone de lápis** na linha da pessoa. O título da janela será **"Editar Usuário"** e todos os campos virão preenchidos com os dados atuais.

A janela é dividida em blocos com títulos: **Dados do Usuário**, **Dados Profissionais**, **Documentos**, **Endereço** e **Contato**. Os campos obrigatórios estão descritos abaixo.

> Dica: enquanto você preenche o formulário, a tecla **Enter** pula para o próximo campo. Nos campos de CBO e CEP, o Enter busca o dado na hora.

### Campo Nome de Usuário

- É o nome de acesso/login da pessoa (como `maria.silva`).
- Precisa ter **no mínimo 3 caracteres** (máximo 50).
- **Sugestão automática**: quando você digita o **Nome Completo**, o sistema preenche esse campo sozinho, usando o primeiro nome seguido das iniciais dos outros nomes (ignorando palavras como "de", "da", "do", "das", "dos" e "e").
- Se você tocar nesse campo para alterar o nome de usuário, o sistema para de preencher sozinho. Se você apagar o campo, o preenchimento automático volta a funcionar.

### Campo Perfil

- Define o **nível de acesso** da pessoa no sistema (por exemplo, leitura).
- O perfil "admin" não aparece nesta lista.
- Para um usuário novo, o padrão já vem como **"leitura"**.

### Campo Nome Completo

- É o nome real da pessoa (como aparece na lista).
- Precisa ter **no mínimo 2 caracteres** (máximo 100).
- É obrigatório.

### Campo E-mail

- E-mail de login/contato da pessoa.
- Precisa ser um e-mail válido (conter "@").
- É obrigatório.

### Campo Senha

- **Criando um usuário novo**: a senha é obrigatória e precisa ter **no mínimo 6 caracteres**.
- **Editando um usuário**: deixe em branco para manter a senha atual. Só preencha se quiser **alterar a senha** — por isso aparece o aviso *"Preencha apenas se deseja alterar a senha"*.

### Campo Código

- Código interno/funcional da pessoa (opcional).
- Use apenas números ou o código que a empresa utiliza.

### Campo C.B.O

- C.B.O. (Classificação Brasileira de Ocupações) — o código da ocupação/função da pessoa (opcional).
- Você pode digitar o código e aguardar que a busca aconteça ao sair do campo, **ou** usar o botão de lupa para buscar.
- A busca precisa de pelo menos 4 dígitos. Quando encontra, o sistema preenche automaticamente o campo **Cargo**. Se não encontrar, aparece o aviso "CBO não encontrado."

### Botão Buscar CBO (lupa)

- **Lupa (ao lado do campo C.B.O)** — consulta a ocupação a partir do código digitado.
- Ao encontrar, preenche o campo **Cargo** automaticamente com a descrição da ocupação.

### Campo Salário Base

- Salário base da pessoa (opcional).
- Digite o valor e, ao sair do campo, ele é formatado automaticamente no formato brasileiro (ex.: `1.234,56`).
- Ao tocar no campo para editar, a formatação é retirada temporariamente para facilitar a digitação.

### Campo Departamento

- Setor em que a pessoa trabalha, por exemplo "Financeiro", "TI" (opcional).

### Campo Cargo

- Cargo/função da pessoa.
- Esse campo é **preenchido automaticamente** pela busca de C.B.O e não pode ser digitado manualmente.

### Campo Classificação

- Nível da pessoa na carreira (opcional).
- As opções são: **Junior**, **Pleno**, **Senior**, **I**, **II**, **III**, **IV** e **V**.

### Campo CPF

- CPF da pessoa (opcional).
- Ao sair do campo, o número é formatado automaticamente (ex.: `123.456.789-00`).

### Campo RG

- RG da pessoa (opcional).
- Ao sair do campo, é formatado automaticamente (ex.: `12.345.678-9`).

### Campo Endereço

- Nome da rua/avenida.
- Esse campo é **preenchido automaticamente** pela busca de CEP e não pode ser digitado manualmente.

### Campo Nº

- Número do imóvel/endereço (opcional).
- Pode ser digitado normalmente (máximo 6 caracteres).

### Campo CEP

- CEP do endereço (opcional).
- Ao sair do campo, o número é formatado automaticamente (ex.: `12345-678`).
- Assim que você informa um CEP com 8 dígitos, o sistema busca e preenche **Endereço**, **Bairro**, **Cidade** e **UF** automaticamente. Se não encontrar, aparece o aviso "CEP não encontrado."

### Botão Buscar CEP (lupa)

- **Lupa (ao lado do campo CEP)** — consulta o endereço a partir do CEP digitado.
- Ao encontrar, preenche automaticamente os campos **Endereço**, **Bairro**, **Cidade** e **UF**.

### Campo Bairro

- Bairro do endereço.
- É **preenchido automaticamente** pela busca de CEP e não pode ser digitado manualmente.

### Campo Cidade

- Cidade do endereço.
- É **preenchida automaticamente** pela busca de CEP e não pode ser digitada manualmente.

### Campo UF

- Sigla do estado (ex.: "SP", "RJ").
- É **preenchida automaticamente** pela busca de CEP e não pode ser digitada manualmente.

### Campo Telefone

- Telefone fixo (opcional).
- Ao sair do campo, é formatado automaticamente (ex.: `(11) 2345-6789`).

### Campo Celular

- Celular (opcional).
- Ao sair do campo, é formatado automaticamente (ex.: `(11) 91234-5678`).

### Botão Salvar

- **Salvar** — grava o usuário novo ou as alterações, fecha a janela e atualiza a tabela.
- Antes de salvar, o sistema valida os campos obrigatórios:
  - **Nome de usuário** com menos de 3 caracteres → aviso "Nome de usuário deve ter no mínimo 3 caracteres."
  - **Nome completo** vazio ou muito curto → aviso "Nome completo é obrigatório."
  - **E-mail** inválido → aviso "E-mail inválido."
  - **Senha** ausente ou com menos de 6 caracteres (apenas na criação) → aviso "Senha deve ter no mínimo 6 caracteres."
- Se algo estiver errado, aparece um aviso e a janela **não fecha**. Corrija e tente de novo.
- Se tudo estiver certo, aparece "Usuário salvo com sucesso."

### Botão Cancelar

- **Cancelar** — fecha a janela **sem salvar** nada.
- Qualquer dado digitado é descartado.

---

## Janela de Gerenciamento de Permissões

Essa janela controla **quais módulos do sistema cada usuário pode acessar**.

- **Como abrir**: clique no **ícone de escudo** na linha do usuário na tela principal.
- Ao abrir, a janela mostra **"Carregando permissões..."** e em seguida lista os módulos do sistema.

Os módulos aparecem organizados em **abas/grupos** (ex.: um grupo para cada área do sistema), cada um com seu próprio título. Dentro de cada grupo, os módulos aparecem com um ícone e uma caixinha de seleção (checkbox). Os módulos que a pessoa já pode acessar aparecem **marcados**.

### Campo Selecionar todos / Limpar

- No topo de cada grupo de módulos há a opção **"Selecionar todos"**.
- Clique nela para marcar **todas** as caixinhas daquele grupo de uma vez. O texto muda para **"Limpar"**.
- Clique em **"Limpar"** para desmarcar todas as caixinhas daquele grupo.

### Campo Marcação de Admin

- Módulos exclusivos para administradores aparecem com o selo **"Admin"** ao lado do nome.
- Marque com cuidado: dar acesso a módulos de admin a um usuário comum pode liberar funções sensíveis.

### Botão Salvar Permissões

- **Salvar Permissões** — grava as permissões marcadas, fecha a janela e mostra o aviso "Permissões atualizadas com sucesso."
- Depois de salvar, o usuário já pode usar (ou deixar de usar) os módulos marcados.

### Botão Cancelar

- **Cancelar** — fecha a janela **sem salvar** as mudanças feitas nas permissões.
