# Manual do Módulo Skins

O módulo **Skins** é o lugar onde você personaliza a aparência do sistema para a sua empresa. Aqui você muda **as cores, as fontes, o logo, o texto de rodapé (copyright) e até os detalhes mais finos de estilo** de todo o ERP GrindX.

Pense no sistema como uma casa pronta: o módulo Skins é a "tinta", a "cortina" e o "quadro na parede". A estrutura continua a mesma, mas tudo fica com a cara da sua empresa.

Na tela principal aparece a frase **"Visual e tema customizável por empresa"** — ou seja, cada empresa pode ter sua própria aparência, e é aqui que você administra isso.

> **Antes de começar:** você precisa estar logado e ter acesso de **administrador**. O módulo fica na área de administração do sistema.

---

## Tela Principal — Gestão de Skins

Esta é a tela que você vê ao abrir o módulo. Ela tem três partes: o **cabeçalho**, os **botões de ação** e a **grade de skins**.

### Cabeçalho (bloco)
- **"Gestão de Skins"**: o título da tela. Ao lado dele aparece um selinho com a **versão do sistema** (só informação).
- **"Visual e tema customizável por empresa."**: um texto explicativo. Não é clicável.

### Botão Importar Skin
Ícone: seta entrando em um arquivo (importação). Fica no canto direito do topo, ao lado do botão "Usar Template".

O que faz: abre a janela de arquivos do seu computador para você **escolher um arquivo `.json`** de uma skin pronta e carregá-la no sistema. O sistema lê o arquivo e **cria a skin automaticamente** na lista, sem precisar preencher nada na mão.

Como usar, passo a passo:
1. Clique em **Importar Skin**.
2. Na janela que abrir, escolha o arquivo **`.json`** da skin (geralmente alguém da equipe te envia, ou você guardou de uma configuração anterior).
3. Pronto — o sistema cria a skin e mostra a mensagem **"Skin 'Nome' importada com sucesso!"**.

Avisos:
- O arquivo precisa ser JSON válido e conter o **nome** da skin. Se não tiver, aparece: *"Arquivo JSON inválido: campo 'name' é obrigatório."*
- Se algo der errado, aparece uma mensagem de erro explicando o problema.
- Depois de importar, use o botão **Editar** no cartão da skin para ajustar cores, fontes, logo etc.

### Botão Usar Template
Ícone: grade de quadrados (como um quebra-cabeça). Fica no canto direito do topo, ao lado de "Importar Skin".

O que faz: abre a janela **"Escolher Template"**, onde você escolhe um **modelo pronto** para criar uma skin nova. É o jeito mais rápido de começar uma skin do zero.

Como usar: veja o detalhamento na seção **Janela "Escolher Template"** mais abaixo.

> **Dica:** em telas pequenas (celular/tablet), o texto desses botões some e fica só o ícone.

### Grade de Skins (cartões) (bloco)
Abaixo dos botões, cada skin aparece como um **cartão**. Cada cartão mostra:
- **Nome da skin**: o nome que você deu (ex.: "Acme Corp Blue").
- **Selinho "ATIVA"**: aparece quando aquela é a skin em uso no sistema agora. Só uma skin pode estar ativa por vez.
- **Faixa de prévia de cores**: uma barrinha com 4 quadradinhos coloridos (cor principal, erro, sucesso e fundo) para você ver a cara da skin rapidinho.
- **3 botões de ação**: **Ativar** (ou o selo "Ativa" travado), **Editar** e **Excluir**.

Se não existir nenhuma skin, a tela mostra **"Nenhuma skin encontrada"**.

### Botão Ativar
Fica dentro do cartão de uma skin que **não está ativa** (azul).

O que faz: torna essa skin a **skin oficial** do sistema, a que todos os usuários da sua empresa vão ver. Ao clicar, o sistema aplica a nova aparência e recarrega a página.

### Botão Ativa (desabilitado)
Quando uma skin **já está ativa**, o botão "Ativar" vira um botão **cinza e travado** escrito "Ativa". Ele não é clicável — só indica que essa é a skin em uso no momento.

### Botão Editar
Fica dentro de cada cartão de skin.

O que faz: abre a **janela de edição** com todos os campos já preenchidos com os valores atuais, para você alterar o que quiser. Veja o detalhamento na seção **Janela de Criação/Edição de Skin**.

### Botão Excluir
Fica dentro de cada cartão de skin (botão vermelho).

O que faz: apaga a skin do sistema. Antes de apagar, o sistema pergunta **"Tem certeza que deseja excluir esta skin?"** — clique em **OK** para confirmar ou **Cancelar** para voltar.

> **Importante sobre excluir:** se a skin estiver **ativa**, o sistema **não deixa excluir** e mostra um aviso dizendo que você precisa desativá-la primeiro (ative outra skin no lugar). Assim o sistema nunca fica sem aparência.

---

## Janela "Escolher Template"

Esta é a janela de modelos prontos. Você chega nela clicando no botão **Usar Template** na tela principal.

**Como abrir:**
1. Clique em **Usar Template** (ícone de grade) na tela principal.

A janela abre com o título **"Escolher Template"** e uma grade de cartões de modelos prontos.

### Grade de Templates (cartões) (bloco)
Cada cartão de template mostra:
- **Nome do template** (ex.: o nome do modelo).
- **Prévia de cores**: uma barrinha com 4 cores que mostra o estilo daquele modelo.

Para escolher, **clique no cartão** do template desejado. Pronto — o sistema **cria uma skin nova** com esse visual e mostra a mensagem **"Skin 'Nome' criada com sucesso!"**. Ela aparece na lista da tela principal, pronta para ser editada ou ativada.

### Botão Fechar (X)
Ícone: **X** no canto superior direito da janela.

O que faz: fecha a janela "Escolher Template" sem escolher nada. Nada é criado.

### Botão Cancelar
Fica no rodapé da janela (texto "Cancelar").

O que faz: fecha a janela "Escolher Template" sem escolher nada, igual ao botão X.

> **Dica:** você também pode fechar a janela clicando **fora dela**, na área escura ao redor.

---

## Janela de Criação/Edição de Skin

Esta é a janela principal de trabalho, onde você configura tudo da skin. Ela abre de dois jeitos:
- **Criar**: usando **Usar Template** ou **Importar Skin** — a skin nasce pronta e você clica em **Editar** para continuar personalizando.
- **Editar**: clicando em **Editar** no cartão de uma skin existente.

O título da janela muda conforme a situação:
- **"Nova Skin"**: quando você está criando uma do zero.
- **"Editar: [Nome da Skin]"**: quando está alterando uma existente.

A janela tem um **interruptor** no topo e várias **seções** organizadas por assunto: **Identidade**, **Cores Básicas**, **Cores Avançadas**, **Dark Mode**, **Tokens Extras**, **Fontes**, **Importar Fontes (ZIP)** e **Importar Fonte de Icones**. No rodapé ficam os botões **Reset**, **Gerar Dark Mode**, **Cancelar** e **Salvar**.

### Interruptor "Tokens Extras" (bloco)
É uma **chavinha deslizante** no canto superior direito da janela, ao lado do título.

- **Desligado (padrão)**: você vê as configurações principais (identidade, cores, fontes etc.).
- **Ligado**: revela a seção **"Tokens Extras"** (ajustes finos de bordas e sombras) e mostra o botão **"Gerar Dark Mode"** no rodapé. Indicado para quem já entende um pouco de design.

Quando você liga, os ajustes avançados aparecem na hora; quando desliga, eles se escondem (o que já foi configurado continua salvo).

### Campo Nome da Skin
O nome interno da aparência. **Obrigatório** — o sistema avisa se você tentar salvar sem preencher.

Como preencher: digite um nome que ajude a identificar a skin. Ex.: `Acme Corp Blue`.

### Campo Nome da Empresa no Sistema
O nome da sua empresa. Ex.: `Acme Corporation`.

Como preencher: digite o nome. **Atenção:** assim que você digita, o campo **Copyright** é preenchido automaticamente com esse nome. Se você apagar o nome da empresa, o copyright é limpo junto.

### Campo Copyright
O texto de rodapé de direitos autorais. Ex.: `© 2026 Acme Corporation. Todos os direitos reservados.`

Como preencher: **não precisa** — ele é **gerado sozinho** a partir do campo "Nome da Empresa no Sistema" (o ano é sempre o ano atual). O campo é **somente leitura**, ou seja, você não digita nele.

### Upload do Logo (bloco)
Aqui você coloca o **logo** da empresa. A área parece uma caixa tracejada com o ícone de nuvem com seta para cima e o texto **"Arraste um arquivo ou clique para selecionar"**.

Como usar:
1. Clique na área tracejada (ou arraste um arquivo de imagem para cima dela).
2. Escolha a imagem no seletor de arquivos (aceita imagens).
3. A imagem aparece como prévia dentro da caixa.
4. Ao editar uma skin que já tem logo, a caixa já vem mostrando o logo atual. Se houver erro ao carregar a imagem, a caixa volta ao estado padrão.

### Campo Primary (Cores Básicas)
A **cor principal** do sistema — botões principais, destaques e links. Padrão: `#00c2e0` (ciano).

Como preencher: cada cor tem dois controles juntos — um **quadradinho de cor** (seletor visual) e um **campo de texto** ao lado. Você pode usar o quadradinho ou digitar o código. Ao digitar, o campo de texto aceita formatos avançados como `rgb(...)`, `oklch(...)` e `color-mix(...)`.

> **Dica importante:** quando você usa o quadradinho, o texto é preenchido sozinho. Se você digitar um formato avançado, o quadradinho fica desabilitado (é normal — ele só funciona com cores simples tipo `#00c2e0`). Sua cor continua válida e é salva normalmente.

### Campo Danger (Cores Básicas)
A cor de **erro/perigo** — mensagens de erro e botões de excluir. Padrão: `#ef4444` (vermelho).

Como preencher: igual ao campo Primary (quadradinho de cor + campo de texto).

### Campo Success (Cores Básicas)
A cor de **sucesso** — mensagens de confirmação e status positivos. Padrão: `#10b981` (verde).

Como preencher: igual ao campo Primary.

### Campo Warning (Cores Básicas)
A cor de **atenção/aviso**. Padrão: `#f59e0b` (amarelo/laranja).

Como preencher: igual ao campo Primary.

### Campo Background Main (Cores Básicas)
A cor de **fundo principal** da tela. Padrão: `#f8fafc` (cinza bem claro).

Como preencher: igual ao campo Primary.

### Campo Background Card (Cores Básicas)
A cor de **fundo dos cartões** (caixas, quadros de informações). Padrão: `#ffffff` (branco).

Como preencher: igual ao campo Primary.

### Prévia das Cores Básicas (bloco)
Um mini-teste ao vivo embaixo das cores que mostra como vai ficar: um **botão**, selos de **Sucesso / Erro / Atenção** e um **cartão com fundo**. Conforme você mexe nas cores, a prévia atualiza na hora.

### Campo Primary Hover (Cores Avançadas)
A cor do botão principal **quando o mouse passa por cima** dele. Padrão: `#00a8c4` (ciano mais escuro).

Como preencher: igual ao campo Primary (quadradinho + campo de texto).

### Campo Text Main (Cores Avançadas)
A cor do **texto principal** (títulos e conteúdo). Padrão: `#1e293b` (azul-escuro).

Como preencher: igual ao campo Primary.

### Campo Text Muted (Cores Avançadas)
A cor do **texto secundário** — legendas, descrições e textos de apoio. Padrão: `#64748b` (cinza).

Como preencher: igual ao campo Primary.

### Campo Border Color (Cores Avançadas)
A cor das **bordas** — contornos de campos, caixas e divisões. Padrão: `#e2e8f0` (cinza claro).

Como preencher: igual ao campo Primary.

### Campo Focus Ring (Cores Avançadas)
A cor do **anel de destaque** quando você clica ou tabula em um campo (foco). Padrão: `rgba(0, 194, 224, 0.35)` (ciano transparente).

Como preencher: igual ao campo Primary.

### Prévia das Cores Avançadas (bloco)
Mostra como vão ficar: um **botão com efeito hover**, um **texto principal**, uma **legenda** (texto secundário), uma **caixa com borda** e um **campo focado** (com o anel de foco). Atualiza ao vivo.

### Campo Background Main Dark (Dark Mode)
A cor de **fundo principal no modo escuro** (tema noturno). Padrão: `#0f172a` (azul quase preto).

Como preencher: igual ao campo Primary.

### Campo Background Card Dark (Dark Mode)
A cor de **fundo dos cartões no modo escuro**. Padrão: `#1e293b` (azul-escuro).

Como preencher: igual ao campo Primary.

### Campo Text Main Dark (Dark Mode)
A cor do **texto principal no modo escuro**. Padrão: `#f8fafc` (quase branco).

Como preencher: igual ao campo Primary.

### Campo Text Muted Dark (Dark Mode)
A cor do **texto secundário no modo escuro**. Padrão: `#94a3b8` (cinza claro).

Como preencher: igual ao campo Primary.

### Campo Border Color Dark (Dark Mode)
A cor das **bordas no modo escuro**. Padrão: `rgba(255, 255, 255, 0.05)` (branco bem transparente).

Como preencher: igual ao campo Primary.

### Prévia do Dark Mode (bloco)
Mostra como ficam o botão, os selos de **sucesso/erro** e um cartão **com fundo escuro**, para você conferir o contraste. Atualiza ao vivo.

> **Dica:** dá para gerar essas cores automaticamente! Ligue o interruptor **"Tokens Extras"** e use o botão **Gerar Dark Mode** no rodapé (explicado mais abaixo).

### Campo Border Radius (sm) (Tokens Extras)
Controla o arredondamento dos cantos dos elementos **pequenos** (ex.: botões pequenos). Padrão: `0.25rem`.

Como preencher: valores **maiores = cantos mais arredondados**. Só aparece com o interruptor **"Tokens Extras" ligado**.

### Campo Border Radius (md) (Tokens Extras)
Arredondamento dos elementos **médios** (ex.: campos de formulário). Padrão: `0.5rem`.

Como preencher: igual ao Border Radius (sm).

### Campo Border Radius (lg) (Tokens Extras)
Arredondamento dos elementos **grandes** (ex.: cartões). Padrão: `0.75rem`.

Como preencher: igual ao Border Radius (sm).

### Campo Border Radius (xl) (Tokens Extras)
Arredondamento bem forte (ex.: alguns modais e banners). Padrão: `1.5rem`.

Como preencher: igual ao Border Radius (sm).

### Campo Shadow Card (Tokens Extras)
A **sombra dos cartões** (o relevo embaixo deles). Padrão: `0 10px 25px rgba(0,0,0,0.1)`.

Como preencher: é um código de estilo — mexa com cuidado. A prévia mostra o efeito aplicado.

### Campo Shadow Modal (Tokens Extras)
A **sombra das janelas** (modais). Padrão: `0 20px 25px -5px rgba(0,0,0,0.2)`.

Como preencher: igual ao Shadow Card.

### Prévia dos Tokens Extras (bloco)
Mostra 4 caixas (sm, md, lg, xl) com os arredondamentos aplicados e 2 caixas com as sombras de **card** e de **modal**. Atualiza ao vivo.

### Campo Fonte de Títulos (Fontes)
A letra usada nos **títulos e cabeçalhos**. Padrão: **Barlow Condensed**.

Como preencher: é uma lista suspensa. Escolha uma das opções: Barlow Condensed, DM Sans, Inter, Roboto, Open Sans, Lato, Montserrat, Poppins, Nunito ou Source Sans Pro. (Fontes que você importar na seção "Importar Fontes (ZIP)" também aparecem aqui.)

### Campo Fonte de Texto (Fontes)
A letra usada no **corpo dos textos** (conteúdo em geral). Padrão: **DM Sans**.

Como preencher: mesma lista suspensa da Fonte de Títulos.

### Campo Fonte dos Módulos (Fontes)
A letra usada no **menu lateral (sidebar) e na barra de cima (topbar)** do sistema. Padrão: **DM Sans**.

Como preencher: mesma lista suspensa da Fonte de Títulos.

### Prévia das Fontes (bloco)
Mostra um **título exemplo**, um **parágrafo de texto** e uma linha indicando os **módulos (Sidebar/Topbar)**. Tudo atualiza ao vivo conforme você troca as fontes.

### Upload de Fontes (ZIP) (bloco)
Aqui você coloca **fontes próprias** (personalizadas) dentro do sistema, enviando um arquivo ZIP.

Como usar, passo a passo:
1. **Prepare o arquivo**: um ZIP contendo arquivos de fonte. Formatos aceitos: `.ttf`, `.otf`, `.woff`, `.woff2`.
2. Clique na área tracejada (**"Clique para selecionar um arquivo ZIP"**, com ícone de pasta compactada) e escolha o `.zip`.
3. O sistema mostra **"Processando ZIP..."** e depois informa quantas fontes foram importadas. Se alguma já existia, ela é ignorada com aviso (ex.: *"2 fonte(s) importada(s), 1 ignorada(s) (já existem)"*).
4. As fontes importadas passam a aparecer nas listas da seção **Fontes** (Fonte de Títulos, Fonte de Texto, Fonte dos Módulos).

Extras desta seção:
- **Status de importação**: uma caixa que mostra o resultado ("Processando...", "X fontes importadas" ou mensagem de erro em vermelho).
- **Link "Baixe fontes gratuitas no Font Squirrel"**: abre em nova aba um site com fontes gratuitas para baixar.

> **Dica:** se o ZIP não tiver nenhuma fonte, aparece: *"Nenhum arquivo de fonte encontrado no ZIP."*

### Campo Nome da Fonte de Icones (Importar Fonte de Icones)
O nome que você quer dar à fonte de ícones. Ex.: `Material Icons`.

Como preencher: digite o nome. Se deixar em branco, o sistema usa o nome do arquivo.

### Upload de Fonte de Icones (bloco)
Aqui você adiciona uma **fonte de ícones** personalizada.

Como usar, passo a passo:
1. Preencha o campo **Nome da Fonte de Icones** (opcional).
2. Clique na área tracejada (ícone de ícones) e escolha um arquivo. Formatos aceitos: `.woff2`, `.ttf`, `.woff`, `.otf`.
3. O sistema mostra **"Enviando..."** e depois **"Fonte de icones 'Nome' importada com sucesso."**.
4. Depois de importada, aparece o botão **"Remover fonte de icones"** para desfazer.

Aviso: se o formato for inválido, aparece: *"Formato nao suportado. Use .woff2, .woff, .ttf ou .otf."*

### Botão Remover Fonte de Icones
Fica na seção "Importar Fonte de Icones" e **só aparece depois que uma fonte de ícones foi importada**.

O que faz: apaga a fonte de ícones da skin atual e volta a área ao estado inicial. Ícone: lixeira.

### Botão Reset
Fica no rodapé da janela. Ícone: seta curva para a esquerda (desfazer).

**Quando aparece:** só aparece se você **mexeu em alguma coisa** e ainda não salvou.

O que faz: **desfaz todas as suas alterações** e volta a janela para os valores originais (como estava quando a janela abriu).

### Botão Gerar Dark Mode
Fica no rodapé da janela. Ícone: meia-lua/luz (ajustar).

**Quando aparece:** só aparece com o interruptor **"Tokens Extras" ligado**.

O que faz: **gera automaticamente** as cores da seção **Dark Mode** a partir das suas cores claras. Ele analisa cada cor clara e cria a versão escura correspondente. Economiza tempo na hora de configurar o modo noturno.

### Botão Cancelar
Fica no rodapé da janela. Ícone: **X**.

O que faz: **fecha a janela sem salvar** nada. Tudo que você mexeu é descartado.

### Botão Salvar
Fica no rodapé da janela (o botão principal). Ícone: disquete (salvar).

O que faz: **salva a skin** com tudo que você configurou.

O que acontece ao clicar:
1. Se o **Nome da Skin** estiver vazio, aparece o aviso "Nome da skin é obrigatório" e nada é salvo.
2. Se tudo certo, a skin é salva (criação nova ou atualização da existente).
3. Aparece a mensagem **"Skin salva com sucesso."**.
4. O sistema **recarrega a página** automaticamente para aplicar a nova aparência em toda a interface.

---

## Fluxos completos passo a passo

### Criar uma skin nova
1. Abra o módulo **Skins**.
2. Clique em **Usar Template** (a forma mais prática de começar).
3. Na janela "Escolher Template", clique no **cartão** do modelo que mais combina com você.
4. O sistema cria a skin. No cartão dela, clique em **Editar**.
5. Preencha a seção **Identidade** (nome da skin, nome da empresa — o copyright é preenchido sozinho — e logo, se quiser).
6. Ajuste as cores nas seções **Cores Básicas**, **Cores Avançadas** e **Dark Mode**. (Dica: ligue "Tokens Extras" e use **Gerar Dark Mode** para facilitar.)
7. Escolha as fontes na seção **Fontes** (e importe fontes/ícones próprios se quiser).
8. Clique em **Salvar**.
9. Clique em **Ativar** no cartão da skin para aplicá-la a todo o sistema.

### Editar uma skin existente
1. No cartão da skin, clique em **Editar**.
2. A janela abre com todos os valores atuais preenchidos. Faça as mudanças.
3. Use o botão **Reset** se quiser descartar as mudanças, ou **Salvar** para confirmar.
4. Se a skin estiver ativa, a mudança é aplicada automaticamente ao recarregar.

### Trocar a skin ativa
1. No cartão da skin que você quer usar, clique em **Ativar**.
2. O sistema aplica e recarrega. A outra skin deixa de ter o selinho "ATIVA".

### Excluir uma skin
1. No cartão da skin, clique em **Excluir**.
2. Confirme na pergunta de segurança.
3. Se a skin estiver ativa, o sistema recusa e pede para você ativar outra primeiro.

---

## Perguntas frequentes

**Posso ter mais de uma skin salva?**
Sim, quantas quiser. Mas **apenas uma fica ativa** (com o selinho "ATIVA") e é a que os usuários veem.

**Como faço para o sistema usar a skin nova?**
Depois de criar/editar, clique em **Ativar** no cartão. O sistema recarrega e passa a usar a nova aparência.

**Esqueci o nome da empresa e o copyright sumiu.**
O copyright é gerado automaticamente a partir do campo "Nome da Empresa no Sistema". Preencha esse campo e o texto volta sozinho.

**Não estou achando a seção "Tokens Extras".**
Ligue o interruptor **"Tokens Extras"** no topo da janela (a chavinha ao lado do título). É assim que essa seção e o botão "Gerar Dark Mode" aparecem.

**Digitando uma cor no campo de texto, o quadradinho de cor desligou.**
Isso acontece quando você usa um formato de cor avançado (ex.: `color-mix()`). O quadradinho só funciona com cores simples (`#hex`). Sua cor avançada continua válida e será salva normalmente.

**Não consigo excluir uma skin.**
Se a skin está ativa, o sistema impede a exclusão para o sistema nunca ficar sem aparência. Ative outra skin e tente de novo.
