# Manual do Módulo Skins

## Tela Principal (Lista de Skins)

Ao abrir o módulo **Gestão de Skins**, o sistema carrega as skins (temas visuais) cadastradas para a empresa. O topo da tela mostra o título "Gestão de Skins", a descrição "Visual e tema customizável por empresa." e a versão do sistema.

Cada skin aparece em um cartão com:

- **Nome da skin**.
- Selo **"Ativa"**, exibido apenas na skin que está em uso no momento.
- Uma faixa de pré-visualização com as cores principais da skin.
- Botões de ação: **Ativar**, **Editar** e **Excluir**.

Se não houver nenhuma skin cadastrada, aparece a mensagem "Nenhuma skin encontrada.".

No topo da tela há dois botões:

- **Importar Skin**: cria uma skin a partir de um arquivo.
- **Usar Template**: cria uma skin a partir de um modelo pronto.

## Importar uma Skin

1. Clique em **Importar Skin**.
2. Selecione um arquivo no formato JSON que contenha os dados da skin.
3. O sistema valida o arquivo. Se estiver incorreto ou faltar o nome da skin, é exibida uma mensagem de erro.
4. Se o arquivo estiver correto, a skin é criada e aparece a mensagem "Skin ... importada com sucesso!".

## Usar um Template

1. Clique em **Usar Template**.
2. É aberta a janela "Escolher Template" com os modelos disponíveis, cada um com uma amostra das suas cores.
3. Clique no template desejado.
4. A skin é criada automaticamente com o nome do template e aparece a mensagem "Skin ... criada com sucesso!".

Para fechar a janela sem escolher nada, clique no "X" ou em **Cancelar**.

## Criar e Editar uma Skin (Janela de Edição)

A janela de edição abre com o título "Nova Skin" (nova) ou "Editar: <nome>" (edição). Nela, cada grupo de configurações fica separado por seções. No rodapé ficam os botões **Reset**, **Gerar Dark Mode**, **Cancelar** e **Salvar**.

### Identidade

- **Nome da Skin**: obrigatório. Identifica a skin.
- **Nome da Empresa no Sistema**: nome exibido no sistema.
- **Copyright**: texto de direitos autorais. É preenchido automaticamente ao digitar o nome da empresa, no formato "© <ano> <empresa>. Todos os direitos reservados.".
- **Upload do Logo**: clique na área de upload e selecione uma imagem. Uma pré-visualização do logo é exibida.

### Cores Básicas

Campos de cor para: **Primary**, **Danger**, **Success**, **Warning**, **Background Main** e **Background Card**.

Cada cor pode ser ajustada de duas formas: pelo seletor de cor ou digitando o valor no campo de texto (aceita formatos como `#hex`, `rgb()`, `oklch()` e `color-mix()`). Abaixo da seção há uma pré-visualização que atualiza na hora, mostrando um botão, selos de status e um cartão.

### Cores Avançadas

Campos de cor para: **Primary Hover**, **Text Main**, **Text Muted**, **Border Color** e **Focus Ring**. Também possuem pré-visualização em tempo real.

### Dark Mode

Cores usadas quando o sistema está no tema escuro: **Background Main Dark**, **Background Card Dark**, **Text Main Dark**, **Text Muted Dark** e **Border Color Dark**. A pré-visualização mostra como esses elementos ficam no modo escuro.

## Tokens Extras (Modo Avançado)

No topo da janela há o botão de alternância **Tokens Extras**. Ao ativá-lo, uma nova seção aparece com:

- **Border Radius (sm, md, lg, xl)**: arredondamento dos cantos em diferentes tamanhos.
- **Shadow Card** e **Shadow Modal**: sombras aplicadas a cartões e janelas.

Quando o modo avançado está ativo, o botão **Gerar Dark Mode** também fica disponível no rodapé.

## Fontes

Nesta seção, escolha a fonte usada em cada parte do sistema:

- **Fonte de Títulos**: fonte dos títulos.
- **Fonte de Texto**: fonte do corpo do texto.
- **Fonte dos Módulos (Sidebar/Topbar)**: fonte dos menus e módulos.

Cada escolha é refletida na pré-visualização logo abaixo.

## Importar Fontes (ZIP)

Para usar fontes personalizadas:

1. Clique na área de upload e selecione um arquivo ZIP contendo os arquivos de fonte.
2. O sistema processa o ZIP e envia as fontes encontradas.
3. Uma mensagem indica quantas fontes foram importadas e quantas foram ignoradas (por já existirem).

As fontes importadas passam a aparecer nas listas de seleção da seção **Fontes**. Há também um link para baixar fontes gratuitas no site Font Squirrel.

## Importar Fonte de Ícones

1. Digite um **Nome da Fonte de Ícones** (opcional; se vazio, é usado o nome do arquivo).
2. Clique na área de upload e selecione um arquivo de fonte (`.woff2`, `.ttf`, `.woff` ou `.otf`).
3. Após o envio, a fonte de ícones é aplicada e aparece o botão **Remover fonte de ícones**.

Para desfazer, clique em **Remover fonte de ícones**.

## Gerar Dark Mode Automático

Com o modo avançado ativo, o botão **Gerar Dark Mode** cria automaticamente as cores da seção Dark Mode a partir das cores claras já definidas, evitando digitar cada uma manualmente.

## Resetar Alterações

O botão **Reset** (no rodapé) aparece apenas quando há alterações em relação ao conteúdo original da skin. Ao clicar, todos os campos voltam aos valores originais.

## Salvar

1. Preencha as configurações desejadas.
2. Clique em **Salvar**.
3. Se o **Nome da Skin** estiver vazio, é exibida a mensagem "Nome da skin é obrigatório".
4. Ao salvar, a skin é gravada e o sistema é recarregado para aplicar o novo visual.

## Ativar uma Skin

Na tela principal, clique em **Ativar** no cartão da skin desejada. A skin passa a ser a ativa (com o selo "Ativa") e o sistema é recarregado com o novo visual. A skin que já está ativa não pode ser ativada novamente (o botão fica desabilitado).

## Excluir uma Skin

1. Na tela principal, clique em **Excluir** no cartão da skin desejada.
2. Confirme a exclusão na mensagem "Tem certeza que deseja excluir esta skin?".
3. A skin é removida da lista.

Não é possível excluir a skin que está ativa; nesse caso, o sistema informa que é necessário desativá-la (ativando outra) primeiro.

## Permissões de Acesso

O módulo exige que o usuário esteja autenticado no sistema. Usuários não logados são redirecionados para a tela de login.
