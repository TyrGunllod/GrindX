# Manual do Módulo Meu Perfil

O módulo **Meu Perfil** é onde você visualiza e gerencia seus dados pessoais dentro do GrindX. Por aqui você pode atualizar suas informações (contato, endereço, dados profissionais), alterar sua senha de acesso e personalizar a aparência do sistema (tema e layout).

Tudo o que você salva aqui fica associado ao seu usuário logado — ou seja, somente você vê e altera essas informações.

---

## Meu Perfil (tela principal)

Ao abrir o módulo, você vê o título **"Meu Perfil"**, a descrição *"Gerencie seus dados pessoais e preferências."* e, ao lado do título, um selo com a **versão do sistema** (por exemplo: "v1.0.0"). Esse selo é apenas informativo.

A tela é dividida em **dois cartões** (blocos):

1. **Meus Dados** — com todos os seus dados pessoais e profissionais.
2. **Configurações** — com botões para alterar senha e preferências.

### Como a tela carrega
Assim que você abre o módulo, o sistema carrega automaticamente as suas informações (nome, e-mail, CPF, endereço etc.) e preenche os campos para você. Você não precisa buscar nada manualmente — apenas confira e edite o que for necessário.

---

## Meus Dados

Cartão com o ícone de **usuário** (🪪) e o título **"Meus Dados"**. Ele contém todos os seus dados em um formulário.

> 💡 **Dica geral:** campos acinzentados (com aparência desabilitada) **não podem ser editados** — eles são informações controladas pelo sistema. Campos brancos normais podem ser preenchidos e alterados por você.

### Campos de identificação (somente leitura)

Esses três primeiros campos são informativos e **não podem ser editados**:

| Campo | O que é | Editável? |
|-------|---------|-----------|
| **Nome de Usuário** | Seu login de acesso ao sistema (sempre em minúsculas). | ❌ Não |
| **Perfil** | Seu nível de acesso dentro do sistema: **Administrador**, **Operador** ou **Leitura**. | ❌ Não |
| **Nome Completo** | Seu nome cadastrado no sistema. | ❌ Não |

> **Sobre o Perfil (permissões):** o valor mostrado aqui indica o seu nível de acesso. **Administrador** tem acesso total, **Operador** executa as operações do dia a dia e **Leitura** apenas visualiza as informações. Se você acha que seu perfil está errado, procure o administrador do sistema — não é possível alterá-lo por aqui.

Logo abaixo, uma linha divisória separa os dados de identificação dos dados editáveis.

### Campos de dados profissionais

| Campo | O que é | Como preencher |
|-------|---------|----------------|
| **Código** | Um código de identificação do funcionário (pode ser seu código/matrícula). | Digite o texto/código desejado. Opcional. |
| **C.B.O** | A **Classificação Brasileira de Ocupações** — o número oficial da sua profissão (ex.: 2525-05 para Analista de Sistemas). | Digite o número do CBO. **Mínimo de 4 dígitos.** Ao sair do campo, o sistema consulta automaticamente. |
| **Salário Base** | O valor do seu salário base. | Digite o valor. **Sem símbolo de R$** — apenas números. Ao sair do campo, o sistema formata sozinho (ex.: `1500,00` vira `1.500,00`). |
| **Departamento** | O setor em que você trabalha (ex.: TI, Financeiro, RH). | Digite o nome do departamento. |
| **Cargo** | Seu cargo no sistema (ex.: Analista de Sistemas). | ⚠️ **Somente leitura** — é preenchido automaticamente pelo sistema quando você informa o **C.B.O**. |
| **Classificação** | O nível/senioridade do seu cargo. | Selecione na lista suspensa: **Junior**, **Pleno**, **Senior**, **I**, **II**, **III**, **IV** ou **V**. |

### Campos de documentos

| Campo | O que é | Como preencher |
|-------|---------|----------------|
| **CPF** | Seu Cadastro de Pessoa Física. | Digite apenas números. Ao sair do campo, o sistema formata sozinho (ex.: `12345678901` vira `123.456.789-01`). |
| **RG** | Seu Registro Geral (documento de identidade). | Digite apenas números. Ao sair do campo, o sistema formata sozinho (ex.: `123456789` vira `12.345.678-9`). |

> 💡 **Comportamento das máscaras:** quando você clica em um campo de CPF, RG, telefone, CEP ou salário para editar, o sistema **remove a formatação** automaticamente para facilitar a digitação. Ao sair do campo, a máscara é aplicada de novo. Digite apenas os números.

### Campos de endereço

| Campo | O que é | Editável? |
|-------|---------|-----------|
| **Endereço** | Nome da sua rua/avenida. | ⚠️ **Somente leitura** — preenchido automaticamente pela busca de CEP. |
| **Nº** | Número do seu endereço. | ✅ Sim — digite o número (até 6 dígitos). |
| **CEP** | Seu Código de Endereçamento Postal. | ✅ Sim — digite os 8 números; o sistema formata sozinho (ex.: `01310100` vira `01310-100`). Ao sair do campo, busca os dados automaticamente. |
| **Bairro** | Seu bairro. | ⚠️ **Somente leitura** — preenchido pela busca de CEP. |
| **Cidade** | Sua cidade. | ⚠️ **Somente leitura** — preenchido pela busca de CEP. |
| **UF** | Sua unidade federativa (estado). | ⚠️ **Somente leitura** — preenchido pela busca de CEP. |

> 💡 **Como funciona a busca por CEP:** basta digitar o CEP completo (8 números). Ao sair do campo, o sistema consulta o endereço e **preenche automaticamente** Endereço, Bairro, Cidade e UF. Você só precisa digitar o **Nº** da sua casa. Se o CEP não for encontrado, aparece uma mensagem de aviso.

### Campos de contato

| Campo | O que é | Como preencher |
|-------|---------|----------------|
| **Telefone** | Seu telefone fixo. | Digite apenas números (DDD + número, ex.: `1133334444`). O sistema formata sozinho (ex.: `(11) 3333-4444`). |
| **Celular** | Seu celular. | Digite apenas números (DDD + número, ex.: `11988887777`). O sistema formata sozinho (ex.: `(11) 98888-7777`). |
| **E-mail** | Seu e-mail para contato. | Digite um e-mail válido (ex.: `voce@empresa.com.br`). **Campo obrigatório** — o botão Salvar só funciona com um e-mail válido. |

> ⚠️ **E-mail:** se o e-mail digitado for inválido ou já estiver em uso por outro usuário, o sistema mostra uma mensagem de erro **em vermelho logo abaixo do campo**. Corrija e tente salvar novamente.

### Botão Salvar

- **Ícone:** disco de salvar (💾) + texto **"Salvar"**.
- **O que faz:** salva todas as alterações que você fez no cartão Meus Dados.
- **Enquanto salva:** o botão muda para *"Salvando..."* com um ícone de carregamento girando, e fica desabilitado até terminar.
- **Quando funciona:** ao concluir, aparece a confirmação **"Dados salvos com sucesso!"** no canto da tela (notificação que desaparece sozinha).
- **O que ele NÃO faz:** não limpa os campos nem fecha a tela. Se algo der errado, você verá uma mensagem de erro na notificação (ou abaixo do e-mail, se o problema for o e-mail).

> 💡 **Dica:** use o botão **Salvar** ao final, depois de preencher tudo. Você pode preencher todos os campos e salvar de uma vez. Campos que você não preencheu ficam vazios — sem problema.

### Atalhos de teclado no formulário

- Pressione **Enter** em qualquer campo do formulário para **pular para o próximo campo**.
- No campo **C.B.O**, pressionar **Enter** faz a consulta da ocupação (mesma coisa que sair do campo).
- No campo **CEP**, pressionar **Enter** faz a consulta do endereço.

---

## Configurações

Cartão com o ícone de **engrenagem** (⚙️) e o título **"Configurações"**. Ele tem dois botões grandes:

| Botão | Ícone | O que faz |
|-------|-------|-----------|
| **Alterar Senha** | Chave (🔑) | Abre a janela (modal) para trocar sua senha de acesso. |
| **Preferências** | Paleta de cores (🎨) | Abre a janela (modal) para personalizar tema e layout do sistema. |

---

### Alterar Senha (janela/modal)

**Como abrir:** clique no botão **"Alterar Senha"** no cartão Configurações.

Uma janela (modal) aparece sobre a tela, com o título **"Alterar Senha"** e o ícone de chave. Nela há 3 campos de senha e 2 botões.

#### Campos do modal

| Campo | O que é | Regras |
|-------|---------|--------|
| **Senha Atual** | A senha que você usa hoje para entrar. | Obrigatório. |
| **Nova Senha** | A nova senha que você quer usar. | Obrigatório. **Mínimo de 6 caracteres.** |
| **Confirmar Nova Senha** | A nova senha digitada de novo, para confirmar. | Obrigatório. Deve ser **exatamente igual** à "Nova Senha". |

Os pontos ficam ocultos (••••) enquanto você digita — isso é normal.

#### Botões do modal

| Botão | Ícone | O que faz |
|-------|-------|-----------|
| **Salvar** | Disco de salvar (💾) | Valida e salva a nova senha. Se algum campo estiver vazio, se a nova senha tiver menos de 6 caracteres ou se a confirmação não bater com a nova senha, o sistema mostra o erro **em vermelho** dentro da janela e não salva. Se tudo der certo, a janela fecha, o sistema **atualiza a página automaticamente** e você passa a usar a nova senha no próximo login. |
| **Cancelar** | — (texto) | Fecha a janela **sem salvar** nada. |

**Como fechar sem salvar:** além do botão Cancelar, você pode clicar **fora da janela** (na área escurecida ao redor) para fechá-la.

> 💡 **Importante:** depois de alterar a senha, o sistema recarrega a página sozinho. Isso é normal — é para aplicar a mudança. Você continuará logado.

---

### Preferências (janela/modal)

**Como abrir:** clique no botão **"Preferências"** no cartão Configurações.

Uma janela (modal) aparece com o título **"Preferências"** e o ícone de paleta. Nela você personaliza a aparência do GrindX.

#### Campos do modal

**1. Tema**
Escolha o visual geral do sistema com os botões de alternância (o selecionado fica com a borda colorida):

| Opção | Ícone | Efeito |
|-------|-------|--------|
| **Claro** | Sol (☀️) | Fundo branco/claro no sistema. |
| **Escuro** | Lua (🌙) | Fundo escuro no sistema. |

**2. Layout Desktop**
Define como o menu/navegação aparece no **computador**:

| Opção | Ícone | Efeito |
|-------|-------|--------|
| **Topbar** | Janela maximizada (🖥️) | Menu na **barra superior** da tela. |
| **Sidebar** | Menu hambúrguer (☰) | Menu em uma **barra lateral** (coluna à esquerda). |

**3. Layout Celular / Tablet**
Define a navegação em **telas pequenas** (celular e tablet):

| Opção | Ícone | Efeito |
|-------|-------|--------|
| **Topbar** | Janela maximizada (🖥️) | Menu na barra superior. |
| **Sidebar** | Menu hambúrguer (☰) | Menu em barra lateral. |

Abaixo dessa opção aparece a dica: *"Aplicado automaticamente em telas menores que 768px."* — ou seja, em celulares/tablets essa escolha vale automaticamente; em computadores vale a escolha de "Layout Desktop".

> 💡 **Qual já está selecionado?** O sistema mostra com a borda destacada a opção que está ativa no momento. Clique na que você quiser para trocar — só uma fica selecionada por vez.

#### Botões do modal

| Botão | Ícone | O que faz |
|-------|-------|-----------|
| **Salvar** | Disco de salvar (💾) | Aplica as preferências escolhidas, fecha a janela e **atualiza a página automaticamente**. Você já verá o novo visual (tema/layout) em ação. |
| **Cancelar** | — (texto) | Fecha a janela **sem aplicar** nenhuma mudança. |

**Como fechar sem salvar:** clique no botão **Cancelar** ou **fora da janela** (na área escurecida) para fechar sem aplicar as mudanças.

> 💡 **Dica:** quando você troca de tema, a mudança vale para todo o sistema, não só para a tela do Meu Perfil. E as preferências ficam salvas para as próximas vezes que você entrar.

---

## Resumo: todos os botões e ícones do módulo

| Onde | Botão / Ícone | Ação |
|------|---------------|------|
| Meus Dados | **Salvar** (💾) | Salva os dados pessoais editados. |
| Meus Dados — C.B.O | **Lupa (🔍)** ao lado do campo C.B.O | Consulta a ocupação do CBO digitado e preenche o campo Cargo. |
| Meus Dados — CEP | **Lupa (🔍)** ao lado do campo CEP | Consulta o CEP digitado e preenche Endereço, Bairro, Cidade e UF. |
| Configurações | **Alterar Senha** (🔑) | Abre o modal para trocar a senha. |
| Configurações | **Preferências** (🎨) | Abre o modal de tema e layout. |
| Modal Alterar Senha | **Salvar** (💾) | Valida e grava a nova senha. |
| Modal Alterar Senha | **Cancelar** | Fecha o modal sem salvar. |
| Modal Preferências | **Salvar** (💾) | Aplica tema/layout e recarrega a página. |
| Modal Preferências | **Cancelar** | Fecha o modal sem aplicar. |
| Qualquer modal | Clique fora da janela | Fecha o modal sem salvar. |

---

## Perguntas rápidas (FAQ)

**Por que alguns campos estão apagados/cinza e não consigo digitar?**
Porque são informações controladas pelo sistema: Nome de Usuário, Perfil, Nome Completo, Cargo, Endereço, Bairro, Cidade e UF. O Cargo vem do CBO, e o endereço vem da busca do CEP — o sistema preenche sozinho.

**Preciso preencher tudo para salvar?**
Não. Só o **E-mail** é obrigatório. Os demais podem ficar vazios, mas quanto mais completos, melhor para o sistema.

**O Cargo não preencheu sozinho. O que fazer?**
Confira se o **C.B.O** tem pelo menos 4 números e aguarde a consulta ao sair do campo (ou clique na lupa 🔍). Se a ocupação não for encontrada, o sistema avisa.

**Tirei o campo CEP e o endereço não preencheu.**
Confira se digitou os **8 números** do CEP e saia do campo (ou clique na lupa 🔍). Se o CEP não existir, o sistema avisa com uma mensagem.

**Troquei o tema e nada mudou?**
Clique em **Salvar** no modal Preferências — é só depois de salvar que o visual é aplicado e a página é recarregada.

**Esqueci minha senha nova que acabei de criar?**
O sistema não mostra a senha em lugar nenhum por segurança. Se você esquecer, procure o administrador do sistema para redefinir o acesso.
