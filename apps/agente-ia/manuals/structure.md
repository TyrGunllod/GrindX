# Manual do Módulo Módulos & Abas

Este módulo permite gerenciar as **abas** do menu lateral do portal e os **módulos** que aparecem dentro delas. Aqui você cria, edita e exclui abas e módulos, além de definir a ordem de exibição e o perfil mínimo de acesso de cada módulo.

## Tela Principal — Estrutura do Portal

Ao abrir o módulo, você vê o título **"Estrutura do Portal"** e a descrição *"Gerencie as abas do menu lateral e os módulos do sistema."*.

No topo, à direita, há dois botões:

- **Nova Aba** — abre a tela para criar uma nova aba do menu.
- **Novo Módulo** — abre a tela para criar um novo módulo.

Logo abaixo, é exibida a estrutura atual do portal, organizada em cartões.

## Visualização da Estrutura

Cada **aba** é exibida em um cartão com:

- O **ícone** e o **nome** da aba no topo.
- Os botões de **Editar** (ícone de lápis) e **Excluir** (ícone de lixeira) no canto do cartão.
- A lista de **sub-abas** (abas aninhadas, mostradas com recuo à esquerda) e de **módulos** pertencentes à aba.

Cada **módulo** aparece como um item com:

- O **nome** do módulo.
- A **URL** de acesso.
- A **ordem** de exibição (quando definida).
- Os botões de **Editar** (ícone de caneta) e **Excluir** (ícone de lixeira).

Observações importantes:

- Abas e módulos **protegidos** pelo sistema não exibem o botão de **Excluir**, pois não podem ser removidos.
- Módulos localizados dentro de uma aba protegida também não podem ser excluídos.
- Se não houver nenhuma estrutura cadastrada, uma mensagem de "nenhuma estrutura cadastrada" é mostrada no lugar da lista.

## Criar Nova Aba

1. Clique no botão **Nova Aba**.
2. Na janela que abre, preencha os campos:
   - **Nome da Aba** — obrigatório.
   - **Ordem** — número que define a posição da aba no menu (padrão 0).
   - **Ícone da Aba** — escolha um ícone na lista disponível.
   - **Sub-aba de (opcional)** — selecione uma aba "pai" caso queira criar uma sub-aba; deixe em "Nenhuma (aba raiz)" para criar uma aba no nível principal.
3. Clique em **Salvar Aba** para confirmar, ou em **Cancelar** para desistir.

Após salvar, a estrutura é atualizada e o menu lateral do portal é recarregado.

## Editar Aba

1. No cartão da aba desejada, clique no botão **Editar** (lápis).
2. A mesma janela de cadastro é aberta, já preenchida com os dados atuais da aba.
3. Altere os campos desejados e clique em **Salvar Aba**.

## Excluir Aba

1. No cartão da aba, clique no botão **Excluir** (lixeira).
2. O sistema pede confirmação: *"Excluir esta aba e todos os seus módulos?"*.
3. Confirme para excluir a aba e todo o seu conteúdo.

Caso a aba seja essencial para o sistema (protegida), o botão de excluir não estará disponível.

## Criar Novo Módulo

1. Clique no botão **Novo Módulo**.
2. Na janela que abre, preencha os campos:
   - **URL do Arquivo** — obrigatório. Indica o caminho do módulo (ex.: `modules/home/index.html`). Ao lado, há o botão **Procurar módulo** (ícone de pasta) para selecionar um módulo já disponível no sistema.
   - **Aba Destino** — selecione a aba onde o módulo aparecerá.
   - **Nome do Módulo** — obrigatório.
   - **Ordem** — número que define a posição do módulo dentro da aba (padrão 0).
   - **Identificador (Slug)** — obrigatório. Identificador único do módulo.
   - **Perfil Mínimo** — perfil mínimo necessário para acessar o módulo (veja a seção "Permissões e Perfil Mínimo").
   - **Ícone do Módulo** — escolha um ícone (padrão: cubo).
3. Clique em **Salvar Módulo** para confirmar, ou em **Cancelar** para desistir.

## Selecionar Módulo pelo Buscador

Ao clicar no botão **Procurar módulo** (ícone de pasta), abre-se a janela **"Selecionar Módulo"**, que lista os módulos disponíveis no sistema.

- Há um campo de **busca** para filtrar a lista pelo nome ou pelo caminho.
- Cada item mostra o **nome**, o **caminho** e um selo indicando se já está **vinculado** a alguma aba (com o nome da aba) ou **não vinculado**.
- Clique em um módulo da lista para preencher automaticamente os campos de **URL**, **Nome** e **Identificador (Slug)** no formulário.

## Editar Módulo

1. No item do módulo desejado, clique no botão **Editar** (caneta).
2. A janela de cadastro é aberta com os dados atuais.
3. Você pode alterar o **Nome**, a **Aba Destino**, a **Ordem**, o **Perfil Mínimo** e o **Ícone**.
4. Os campos **URL do Arquivo**, **Identificador (Slug)** e **Ícone** ficam bloqueados (somente leitura) durante a edição.

Clique em **Salvar Módulo** para confirmar.

## Excluir Módulo

1. No item do módulo, clique no botão **Excluir** (lixeira).
2. O sistema pede confirmação: *"Excluir este módulo?"*.
3. Confirme para excluir o módulo.

Módulos protegidos, ou módulos dentro de abas protegidas, não exibem o botão de excluir.

## Permissões e Perfil Mínimo

Cada módulo possui um **Perfil Mínimo**, que determina qual perfil de usuário é necessário para acessá-lo. As opções são:

- **Leitura** — perfil com acesso somente de visualização.
- **Operador** — perfil de operação (padrão).
- **Administrador** — perfil com acesso completo.

Um texto de apoio abaixo do campo explica que se trata do *"Perfil mínimo necessário para acessar este módulo"*.
