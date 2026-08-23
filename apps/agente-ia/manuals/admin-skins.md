# Manual do Módulo Skins

## Tela Principal (Lista de Skins)

Ao abrir o módulo **Gestão de Skins**, o sistema carrega as skins (temas visuais) cadastradas para a empresa. No topo da tela aparecem o título "Gestão de Skins", a descrição "Visual e tema customizável por empresa." e a versão do sistema.

Cada skin cadastrada aparece em um cartão com:

- **Nome da skin**: identificação da skin.
- Selo **"Ativa"**: exibido somente na skin que está em uso no momento.
- **Faixa de pré-visualização**: mostra as cores principais da skin (primary, danger, success e background).
- Botões de ação do cartão (descritos abaixo).

Se não houver nenhuma skin cadastrada, aparece a mensagem "Nenhuma skin encontrada. Verifique o console (F12) para erros de API.".

### Botões do topo da tela

- **Importar Skin** — abre a seleção de arquivo para importar uma skin a partir de um arquivo JSON (ver seção "Importar uma Skin").
- **Usar Template** — abre a janela "Escolher Template" para criar uma skin a partir de um modelo pronto (ver seção "Escolher Template").

### Botões de cada cartão de skin

- **Ativar** — torna esta skin a ativa (a usada no sistema). Só aparece nas skins que ainda não estão ativas.
- **Ativa** — botão desabilitado, exibido apenas no cartão da skin que já está ativa (não pode ser clicado).
- **Editar** — abre a janela de edição com os dados desta skin preenchidos (ver seção "Janela de Edição").
- **Excluir** — remove a skin (ver seção "Excluir uma Skin").

## Importar uma Skin

Permite criar uma nova skin a partir de um arquivo JSON que contenha os dados da skin.

1. Clique no botão **Importar Skin** (topo da tela).
2. Na janela de seleção de arquivo, escolha um arquivo no formato **.json**.
3. O sistema valida o arquivo:
   - Se o arquivo estiver inválido ou faltar o campo **name**, aparece a mensagem "Arquivo JSON inválido: campo "name" é obrigatório.".
   - Se o arquivo estiver correto, a skin é criada e aparece a mensagem "Skin "<nome>" importada com sucesso!".
4. A lista de skins é atualizada automaticamente.

## Escolher Template

Cria uma skin automaticamente a partir de um modelo visual pronto.

1. Clique no botão **Usar Template** (topo da tela).
2. Abre a janela **"Escolher Template"** com os modelos disponíveis. Cada modelo aparece em um cartão com o **nome do template** e uma **amostra de suas cores**.
3. Clique no cartão do template desejado.
4. A skin é criada com o nome do template e aparece a mensagem "Skin "<nome>" criada com sucesso!".
5. A lista de skins é atualizada automaticamente.

### Botões da janela "Escolher Template"

- **X** (canto superior direito) — fecha a janela sem criar nenhuma skin.
- **Cancelar** (rodapé) — fecha a janela sem criar nenhuma skin.
- **Cartões de template** — ao clicar em um cartão, cria a skin correspondente e fecha a janela.

## Janela de Edição de Skin

A janela de edição abre com o título **"Nova Skin"** (ao criar) ou **"Editar: <nome>"** (ao editar uma skin existente). Ela é usada tanto para criar uma nova skin quanto para editar uma já existente. Todos os campos são opcionais, exceto **Nome da Skin**.

Para abrir a janela:
- Para **criar**: não há botão dedicado de "Nova Skin" na tela principal; uma nova skin é criada via **Importar Skin**, **Usar Template** ou editando. Caso exista um botão de criação, ele abre a janela com os campos em branco.
- Para **editar**: clique no botão **Editar** do cartão da skin desejada.

As configurações ficam agrupadas por seções. À medida que você altera valores, a pré-visualização de cada seção e o tema são atualizados em tempo real.

No topo da janela há o botão de alternância **"Tokens Extras"** (ver seção "Tokens Extras"). No rodapé ficam os botões **Reset**, **Gerar Dark Mode**, **Cancelar** e **Salvar**.

### Botões da janela de edição

- **Tokens Extras** (interruptor no topo) — ativa ou desativa o modo avançado. Quando ativo, mostra a seção "Tokens Extras" e o botão "Gerar Dark Mode".
- **Reset** (rodapé) — volta todos os campos aos valores originais da skin. Só aparece quando há alguma alteração (ver seção "Resetar Alterações").
- **Gerar Dark Mode** (rodapé) — gera automaticamente as cores da seção "Dark Mode" a partir das cores claras. Só aparece com o modo avançado ativo (ver seção "Gerar Dark Mode").
- **Cancelar** (rodapé) — fecha a janela sem salvar as alterações.
- **Salvar** (rodapé) — grava a skin e fecha a janela (ver seção "Salvar uma Skin").

### Identidade

- **Nome da Skin**: obrigatório. Identifica a skin. Se ficar vazio, ao salvar aparece a mensagem "Nome da skin é obrigatório".
- **Nome da Empresa no Sistema**: nome da empresa exibido no sistema.
- **Copyright**: texto de direitos autorais. É preenchido automaticamente ao digitar o nome da empresa, no formato "© <ano> <empresa>. Todos os direitos reservados." (o ano é o ano atual). Se o nome da empresa for apagado, o campo também é limpo. Não pode ser editado diretamente.
- **Upload do Logo**: clique na área de upload e selecione uma imagem. A pré-visualização do logo é exibida. Ao editar uma skin, o logo é enviado imediatamente após a seleção.

### Cores Básicas

Campos de cor para: **Primary**, **Danger**, **Success**, **Warning**, **Background Main** e **Background Card**.

Cada cor pode ser ajustada de duas formas:
- Pelo **seletor de cor** (o quadradinho colorido), que atualiza o campo de texto ao lado.
- Digitando o valor no **campo de texto** ao lado, que aceita formatos como `#hex`, `rgb()`, `oklch()` e `color-mix()`. Quando o texto é um hexadecimal válido, o seletor de cor acompanha o valor.

Abaixo da seção há uma **pré-visualização** que atualiza em tempo real, mostrando um botão, os selos "Sucesso", "Erro" e "Atenção", e um cartão com fundo.

### Cores Avançadas

Campos de cor para: **Primary Hover**, **Text Main**, **Text Muted**, **Border Color** e **Focus Ring**.

Funcionam da mesma forma que as Cores Básicas (seletor de cor + campo de texto). A pré-visualização mostra o botão em estado de "hover", o texto principal, a legenda, a borda e um campo de input focado.

### Dark Mode

Cores usadas quando o sistema está no tema escuro: **Background Main Dark**, **Background Card Dark**, **Text Main Dark**, **Text Muted Dark** e **Border Color Dark**.

Funcionam da mesma forma (seletor de cor + campo de texto). A pré-visualização mostra como o botão, os selos e o cartão ficam no modo escuro.

### Tokens Extras

Esta seção fica oculta por padrão. Para exibi-la, ative o interruptor **"Tokens Extras"** no topo da janela. Ela contém:

- **Border Radius (md)**: arredondamento dos cantos em tamanho médio.
- **Border Radius (lg)**: arredondamento em tamanho grande.
- **Border Radius (sm)**: arredondamento em tamanho pequeno.
- **Border Radius (xl)**: arredondamento em tamanho extra grande.
- **Shadow Card**: sombra aplicada aos cartões.
- **Shadow Modal**: sombra aplicada às janelas (modais).

A pré-visualização mostra os cantos arredondados e as sombras em tempo real.

### Fontes

Escolha a fonte usada em cada parte do sistema. Cada campo é uma lista de seleção com as fontes disponíveis (Barlow Condensed, DM Sans, Inter, Roboto, Open Sans, Lato, Montserrat, Poppins, Nunito e Source Sans Pro). As fontes importadas via ZIP também aparecem nessas listas.

- **Fonte de Títulos**: fonte usada nos títulos.
- **Fonte de Texto**: fonte usada no corpo do texto.
- **Fonte dos Módulos (Sidebar/Topbar)**: fonte usada nos menus e módulos.

A pré-visualização abaixo mostra um título, um texto de corpo e um exemplo de módulo na fonte escolhida.

### Importar Fontes (ZIP)

Permite adicionar fontes personalizadas para usar nas listas da seção "Fontes".

1. Clique na área de upload e selecione um arquivo **ZIP** contendo os arquivos de fonte (`.ttf`, `.otf`, `.woff` ou `.woff2`).
2. O sistema processa o ZIP e envia as fontes encontradas.
3. Ao final, uma mensagem indica quantas fontes foram importadas e quantas foram ignoradas (por já existirem). Se nenhum arquivo de fonte for encontrado no ZIP, aparece a mensagem "Nenhum arquivo de fonte encontrado no ZIP.".

Há também um link **"Baixe fontes gratuitas no Font Squirrel"**, que abre o site Font Squirrel em outra aba para baixar fontes gratuitas.

### Importar Fonte de Ícones

Permite usar uma fonte de ícones personalizada.

1. Digite o **Nome da Fonte de Ícones** (opcional; se ficar vazio, é usado o nome do arquivo).
2. Clique na área de upload e selecione um arquivo de fonte (`.woff2`, `.ttf`, `.woff` ou `.otf`).
3. Após o envio, aparece a mensagem "Fonte de icones "<nome>" importada com sucesso." e a fonte é aplicada.

Botões desta seção:

- **Remover fonte de icones** — remove a fonte de ícones personalizada e limpa o campo de nome. Só aparece depois que uma fonte de ícones é importada.

## Gerar Dark Mode Automático

Com o modo avançado ativo (interruptor **Tokens Extras** ligado), o botão **Gerar Dark Mode** fica disponível no rodapé da janela de edição. Ao clicar, ele cria automaticamente as cores da seção "Dark Mode" a partir das cores claras já definidas (Background Main, Background Card, Text Main, Text Muted e Border Color), evitando digitar cada uma manualmente.

## Resetar Alterações

O botão **Reset** (rodapé da janela de edição) só aparece quando há alguma alteração em relação ao conteúdo original da skin. Ao clicar, todos os campos voltam aos valores originais da skin (ou aos valores padrão, se for uma skin nova).

## Salvar uma Skin

1. Preencha as configurações desejadas na janela de edição.
2. Clique no botão **Salvar**.
3. Se o **Nome da Skin** estiver vazio, aparece a mensagem "Nome da skin é obrigatório" e nada é salvo.
4. Se estiver tudo certo, a skin é gravada, a janela fecha e aparece a mensagem "Skin salva com sucesso.". O sistema é recarregado para aplicar o novo visual.

## Ativar uma Skin

1. Na tela principal, clique no botão **Ativar** do cartão da skin desejada.
2. A skin passa a ser a ativa (recebe o selo "Ativa") e o sistema é recarregado com o novo visual.

A skin que já está ativa não pode ser ativada novamente: em seu cartão aparece o botão desabilitado **Ativa**.

## Excluir uma Skin

1. Na tela principal, clique no botão **Excluir** do cartão da skin desejada.
2. Confirme a exclusão na mensagem "Tem certeza que deseja excluir esta skin?".
3. A skin é removida da lista e aparece a mensagem "Skin excluída com sucesso.".

Não é possível excluir a skin que está ativa. Nesse caso, aparece a mensagem "Não é possível excluir uma skin ativa. Desative-a primeiro." (para "desativar", ative outra skin).

## Permissões de Acesso

O módulo exige que o usuário esteja autenticado no sistema. Usuários não logados são redirecionados para a tela de login.
