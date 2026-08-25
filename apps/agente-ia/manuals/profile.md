# Manual do Módulo Meu Perfil

O **Meu Perfil** é o lugar onde você cuida dos seus dados pessoais e das suas preferências no ERP GrindX. Aqui você pode atualizar suas informações de contato, dados profissionais, alterar sua senha e escolher o visual do sistema.

Este manual mostra, passo a passo, o que cada campo e cada botão faz.

---

## Tela: Meus Dados

Ao abrir o **Meu Perfil**, você vê o bloco **Meus Dados**, com um formulário dividido em várias seções. Os campos em cinza (que não podem ser digitados) são apenas de consulta — eles são preenchidos automaticamente pelo sistema.

### Campo Nome de Usuário
Mostra o seu login de acesso. **Não pode ser editado** — é criado quando sua conta é cadastrada.

### Campo Perfil
Mostra qual é o seu tipo de acesso no sistema (ex.: Administrador, Operador ou Leitura). **Não pode ser editado** — é definido pelo responsável pela sua conta.

### Campo Nome Completo
Mostra seu nome por extenso. **Não pode ser editado** aqui — para corrigir, fale com o administrador do sistema.

### Campo Código
Identificador interno do seu cadastro de funcionário. Digite o código caso o campo esteja em branco.

### Campo C.B.O
Aqui você informa o código da sua ocupação (Classificação Brasileira de Ocupações), que é usado para preencher o seu cargo automaticamente.

**Como preencher:**
1. Digite o código do CBO (pelo menos 4 números).
2. Clique no botão de lupa (buscar) ao lado do campo, ou pressione **Enter**.
3. O sistema consulta a ocupação e preenche sozinho o campo **Cargo**.

### Botão Buscar CBO
Botão em formato de lupa (ícone 🔍) que fica ao lado do campo C.B.O. Ao clicar, o sistema procura a ocupação correspondente ao código digitado e preenche o campo **Cargo** automaticamente. Se o código não for encontrado, aparece uma mensagem "CBO não encontrado".

### Campo Salário Base
Digite o valor do seu salário base, usando vírgula para os centavos (ex.: `3.500,00`). O sistema formata o valor sozinho ao sair do campo.

### Campo Departamento
Digite o nome do seu departamento ou setor (ex.: Financeiro, TI, Vendas).

### Campo Cargo
Mostra o seu cargo. **Não pode ser digitado** — ele é preenchido automaticamente pelo sistema quando você informa o C.B.O.

### Campo Classificação
Selecione o nível da sua função na lista suspensa. As opções são: **Junior**, **Pleno**, **Senior**, **I**, **II**, **III**, **IV** ou **V**.

### Campo CPF
Digite seu CPF. O sistema formata os pontos e o traço automaticamente. Ao clicar no campo, a máscara some para você digitar só os números.

### Campo RG
Digite seu RG. O sistema formata os pontos e o traço automaticamente. Ao clicar no campo, a máscara some para você digitar só os números.

### Campo Endereço
Mostra o nome da sua rua. **Não pode ser digitado** — é preenchido automaticamente quando você informa o CEP.

### Campo Nº
Digite o número do seu endereço (máximo de 6 caracteres).

### Campo CEP
Digite seu CEP. O sistema formata com o hífen automaticamente.

**Como preencher:**
1. Digite os 8 números do CEP.
2. Clique no botão de lupa (buscar) ao lado do campo, ou pressione **Enter**.
3. O sistema consulta o CEP e preenche sozinho os campos **Endereço**, **Bairro**, **Cidade** e **UF**.

### Botão Buscar CEP
Botão em formato de lupa (ícone 🔍) ao lado do campo CEP. Ao clicar, o sistema consulta o CEP digitado e preenche automaticamente os campos de endereço, bairro, cidade e UF. Se o CEP não existir, aparece a mensagem "CEP não encontrado".

### Campo Bairro
Mostra o seu bairro. **Não pode ser digitado** — é preenchido automaticamente quando você informa o CEP.

### Campo Cidade
Mostra a sua cidade. **Não pode ser digitado** — é preenchida automaticamente quando você informa o CEP.

### Campo UF
Mostra a sigla do seu estado (ex.: SP, RJ, MG). **Não pode ser digitado** — é preenchida automaticamente quando você informa o CEP.

### Campo Telefone
Digite seu telefone fixo com DDD. O sistema formata no padrão `(11) 1234-5678` ao sair do campo. Ao clicar, a máscara some para você digitar só os números.

### Campo Celular
Digite seu celular com DDD. O sistema formata no padrão `(11) 91234-5678` ao sair do campo. Ao clicar, a máscara some para você digitar só os números.

### Campo E-mail
Digite seu e-mail de contato. Este campo é obrigatório — se você deixá-lo em branco ou digitar um endereço inválido, o sistema mostra um aviso de erro abaixo do campo.

### Botão Salvar
Botão azul com ícone de disquete (💾) que fica no final do bloco **Meus Dados**. Ele salva todas as alterações que você fez nos campos. Enquanto salva, o botão mostra "Salvando..." e fica desabilitado. Ao terminar, aparece a mensagem "Dados salvos com sucesso!".

**Dica:** se o sistema acusar erro no e-mail, a mensagem aparece em vermelho logo abaixo do campo E-mail.

---

## Tela: Configurações

Logo abaixo do bloco **Meus Dados** há o bloco **Configurações**, com dois botões de atalho para ajustes gerais da sua conta.

### Botão Alterar Senha
Botão com ícone de chave (🔑). Ao clicar, abre a janela (modal) para você trocar a sua senha de acesso. Veja a seção [Modal Alterar Senha](#modal-alterar-senha).

### Botão Preferências
Botão com ícone de paleta de cores (🎨). Ao clicar, abre a janela (modal) para você personalizar o tema e o layout do sistema. Veja a seção [Modal Preferências](#modal-preferências).

---

## Modal Alterar Senha

Esta janela abre quando você clica no botão **Alterar Senha** na tela de Configurações. Ela serve para trocar a sua senha de acesso ao sistema.

### Como abrir
1. Na tela **Meu Perfil**, role até o bloco **Configurações**.
2. Clique no botão **Alterar Senha**.

### Campo Senha Atual
Digite a sua senha atual (a que você usa hoje para entrar no sistema). Os caracteres ficam ocultos como bolinhas.

### Campo Nova Senha
Digite a nova senha que você quer usar. Ela deve ter **no mínimo 6 caracteres**.

### Campo Confirmar Nova Senha
Digite novamente a nova senha, exatamente igual ao campo anterior, para confirmar.

### Botão Salvar (modal Alterar Senha)
Botão azul com ícone de disquete (💾) no rodapé da janela. Salva a nova senha e fecha a janela. **Importante:** depois de salvar, o sistema recarrega a página — você deverá entrar novamente com a nova senha.

**Avisos que podem aparecer:**
- Se algum campo ficar em branco: "Preencha todos os campos de senha."
- Se a nova senha e a confirmação não forem iguais: "Nova senha e confirmação não conferem."
- Se a nova senha for muito curta: "Nova senha deve ter no mínimo 6 caracteres."

Esses avisos aparecem em vermelho no rodapé da janela.

### Botão Cancelar (modal Alterar Senha)
Botão com contorno, no rodapé da janela. Fecha a janela sem salvar nada. Você também pode fechar clicando fora da janela, na área escura ao redor.

---

## Modal Preferências

Esta janela abre quando você clica no botão **Preferências** na tela de Configurações. Ela serve para personalizar a aparência do sistema: o tema (claro ou escuro) e o layout (posição da barra de menu).

### Como abrir
1. Na tela **Meu Perfil**, role até o bloco **Configurações**.
2. Clique no botão **Preferências**.

### Opção Tema — Claro / Escuro
Escolha o visual do sistema. Toque em **Claro** (ícone ☀️) para usar o tema claro, ou **Escuro** (ícone 🌙) para usar o tema escuro. A opção escolhida fica destacada.

### Opção Layout Desktop — Topbar / Sidebar
Escolha onde fica o menu quando você usa o sistema no computador:
- **Topbar** (ícone de janela): menu na parte de cima da tela.
- **Sidebar** (ícone de três linhas): menu em uma barra lateral.

### Opção Layout Celular / Tablet — Topbar / Sidebar
Escolha o layout usado em telas menores, como celulares e tablets (telas abaixo de 768px). A escolha é aplicada automaticamente nesses aparelhos.
- **Topbar**: menu na parte de cima.
- **Sidebar**: menu em uma barra lateral.

### Botão Salvar (modal Preferências)
Botão azul com ícone de disquete (💾) no rodapé da janela. Salva as preferências, aplica o novo visual na hora e fecha a janela. O sistema recarrega a página para aplicar as mudanças por completo.

### Botão Cancelar (modal Preferências)
Botão com contorno, no rodapé da janela. Fecha a janela sem salvar nada. Você também pode fechar clicando fora da janela, na área escura ao redor.
