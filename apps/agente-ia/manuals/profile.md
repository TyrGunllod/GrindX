# Manual do Módulo Meu Perfil

O módulo **Meu Perfil** permite que você visualize e edite seus dados pessoais, altere sua senha e personalize suas preferências de exibição (tema e layout). Tudo o que você altera aqui vale apenas para a sua própria conta de usuário.

---

## Meus Dados

Esta é a tela principal do módulo. Nela você vê e edita suas informações pessoais e profissionais. Ao entrar no módulo, seus dados atuais são carregados automaticamente.

Alguns campos aparecem **preenchidos e bloqueados** (não podem ser editados), pois são gerenciados pela administração do sistema. Os demais podem ser editados por você.

### Campos de identificação (somente leitura)

- **Nome de Usuário** — seu login de acesso ao sistema. Não pode ser alterado por você.
- **Perfil** — o nível de permissão da sua conta. Pode aparecer como **Administrador**, **Operador**, **Leitura** ou **Usuário**. Este campo é informativo e não pode ser alterado por você.
- **Nome Completo** — seu nome cadastrado. Não pode ser alterado por você.

### Campos profissionais

- **Código** — seu código de funcionário (matrícula). Preencha com o código informado pela empresa, caso esteja vazio.
- **C.B.O** — código da Classificação Brasileira de Ocupações do seu cargo. Digite o código e use o botão de busca (lupa) para preencher o cargo automaticamente (veja abaixo).
- **Salário Base** — seu salário. Digite apenas números; o valor é formatado automaticamente com separador de milhar e vírgula decimal (ex.: `2500,00`).
- **Departamento** — nome do departamento ao qual você pertence.
- **Cargo** — descrição da sua função. É preenchido automaticamente ao consultar o C.B.O; por isso não pode ser digitado manualmente.
- **Classificação** — seu nível de classificação. Selecione uma das opções: **Junior**, **Pleno**, **Senior**, **I**, **II**, **III**, **IV** ou **V**.

### Campos de documentos

- **CPF** — seu CPF. Digite apenas números; a máscara `000.000.000-00` é aplicada automaticamente ao sair do campo.
- **RG** — seu RG. Digite apenas números; a máscara é aplicada automaticamente ao sair do campo.

### Campos de endereço

- **Endereço** — nome da rua/logradouro. É preenchido automaticamente ao consultar o CEP; por isso não pode ser digitado manualmente.
- **Nº** — número da residência. Este campo é preenchido por você.
- **CEP** — seu CEP. Digite apenas números; a máscara `00000-000` é aplicada automaticamente. Ao sair do campo (ou clicar na lupa), o sistema preenche endereço, bairro, cidade e UF.
- **Bairro** — preenchido automaticamente pela consulta de CEP; não editável.
- **Cidade** — preenchida automaticamente pela consulta de CEP; não editável.
- **UF** — preenchida automaticamente pela consulta de CEP; não editável.

### Campos de contato

- **Telefone** — seu telefone fixo. Digite apenas números; a máscara `(00) 0000-0000` é aplicada automaticamente.
- **Celular** — seu celular. Digite apenas números; a máscara `(00) 00000-0000` é aplicada automaticamente.
- **E-mail** — seu e-mail de contato. Campo obrigatório. Se estiver vazio ou inválido, o sistema exibe uma mensagem de erro ao salvar.

### Botões desta tela

- **Buscar CBO** (ícone de lupa ao lado do campo C.B.O) — consulta o código de C.B.O digitado e preenche automaticamente o campo **Cargo** com a descrição da ocupação. Se o código não for encontrado, exibe a mensagem "CBO não encontrado.".
- **Buscar CEP** (ícone de lupa ao lado do campo CEP) — consulta o CEP digitado e preenche automaticamente os campos **Endereço**, **Bairro**, **Cidade** e **UF**. Se o CEP não for encontrado, exibe a mensagem "CEP não encontrado.".
- **Salvar** — grava todas as alterações feitas nos campos editáveis. Ao clicar, o botão mostra "Salvando..." e, ao concluir, exibe a mensagem "Dados salvos com sucesso!". Se o e-mail estiver inválido, o erro é exibido logo abaixo do campo E-mail.

> Dica: pressionar **Enter** dentro de um campo avança para o próximo campo do formulário. Ao pressionar Enter no campo C.B.O ou CEP, a respectiva consulta é executada automaticamente.

---

## Configurações

Esta tela dá acesso às opções de segurança e personalização da sua conta. Ela contém dois botões.

### Botões desta tela

- **Alterar Senha** — abre a janela para trocar a sua senha de acesso (veja a seção "Alterar Senha").
- **Preferências** — abre a janela para definir o tema e o layout do sistema (veja a seção "Preferências").

---

## Alterar Senha

Janela usada para trocar a sua senha de acesso. Para abri-la, clique no botão **Alterar Senha** na tela **Configurações**. Para fechar sem salvar, clique em **Cancelar** ou clique fora da janela.

### Como preencher

1. **Senha Atual** — digite a senha que você usa atualmente para entrar no sistema.
2. **Nova Senha** — digite a nova senha que deseja usar. Deve ter no mínimo 6 caracteres.
3. **Confirmar Nova Senha** — digite novamente a nova senha, exatamente igual à anterior.

Regras de validação:
- Todos os três campos são obrigatórios. Se algum estiver vazio, aparece a mensagem "Preencha todos os campos de senha.".
- A **Nova Senha** deve ser igual à **Confirmar Nova Senha**. Se não conferirem, aparece "Nova senha e confirmação não conferem.".
- A **Nova Senha** deve ter no mínimo 6 caracteres. Caso contrário, aparece "Nova senha deve ter no mínimo 6 caracteres.".

### Botões desta janela

- **Salvar** — valida os campos e envia a troca de senha. Ao concluir com sucesso, a janela é fechada e a página é recarregada. Se a senha atual estiver incorreta, o erro é exibido dentro da própria janela.
- **Cancelar** — fecha a janela sem realizar nenhuma alteração.

---

## Preferências

Janela usada para personalizar a aparência do sistema. Para abri-la, clique no botão **Preferências** na tela **Configurações**. Para fechar sem salvar, clique em **Cancelar** ou clique fora da janela.

### Como preencher

1. **Tema** — escolha o esquema de cores do sistema:
   - **Claro** — aplica o tema com fundo claro.
   - **Escuro** — aplica o tema com fundo escuro.
   Apenas uma das duas opções pode ficar selecionada por vez; a selecionada fica destacada.

2. **Layout Desktop** — escolha como a navegação aparece no computador:
   - **Topbar** — menu de navegação na parte superior.
   - **Sidebar** — menu de navegação na lateral.
   Apenas uma opção pode ficar selecionada por vez.

3. **Layout Celular / Tablet** — escolha como a navegação aparece em telas menores:
   - **Topbar** — menu na parte superior.
   - **Sidebar** — menu na lateral.
   Esta preferência é aplicada automaticamente em telas com menos de 768px de largura.

### Botões desta janela

- **Salvar** — grava o tema e os layouts escolhidos. Ao concluir, a janela é fechada e a página é recarregada para aplicar as novas preferências.
- **Cancelar** — fecha a janela sem salvar nenhuma alteração.

---

## Resumo de permissões

- A edição dos dados e preferências aplica-se apenas à sua própria conta.
- Campos como **Nome de Usuário**, **Perfil**, **Nome Completo**, **Cargo**, **Endereço**, **Bairro**, **Cidade** e **UF** são preenchidos automaticamente ou gerenciados pela administração e não podem ser alterados diretamente por você.
- O campo **Perfil** exibe seu nível de acesso (**Administrador**, **Operador**, **Leitura** ou **Usuário**) apenas de forma informativa.
