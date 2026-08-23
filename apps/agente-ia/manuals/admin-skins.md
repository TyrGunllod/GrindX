# Manual do Módulo Skins

## O que é o módulo Skins

O módulo **Skins** é onde você personaliza a aparência do sistema para a sua empresa. Com ele, você muda **as cores, as fontes, o logo, o texto de rodapé (copyright) e até os detalhes mais finos de estilo** de todo o ERP GrindX.

Imagine que o sistema é uma casa pronta: o módulo Skins é a "tinta", a "cortina" e o "quadro na parede". Você não muda a estrutura, mas deixa tudo com a cara da sua empresa.

A página principal mostra a frase **"Visual e tema customizável por empresa"** — ou seja, cada empresa que usa o GrindX pode ter a sua própria aparência, e você administra isso por aqui.

> **Antes de começar:** você precisa estar logado no sistema e ter acesso de **administrador** para chegar neste módulo. Ele fica dentro da área de administração.

---

## Tela Principal — Gestão de Skins

Essa é a primeira tela que você vê ao abrir o módulo. Ela tem três partes: o **cabeçalho**, os **botões de ação** e a **grade de skins**.

### Cabeçalho
- **"Gestão de Skins"**: o título da tela. Ao lado dele aparece a versão do sistema (um selinho pequeno), que serve só como informação.
- **"Visual e tema customizável por empresa."**: um texto explicativo. Não é clicável.

### Botões do cabeçalho
| Botão | Ícone | O que faz |
|---|---|---|
| **Importar Skin** | ícone de seta para dentro de um arquivo (importar) | Abre a janela do seu computador para você **escolher um arquivo `.json`** de uma skin pronta e carregá-la no sistema. |
| **Usar Template** | ícone de grade/quebra-cabeça (quadrados em forma de grade) | Abre a janela **"Escolher Template"**, onde você escolhe um **modelo pronto** para criar uma skin nova. |

> **Dica:** em telas pequenas (celular/tablet), o texto do botão some e fica só o ícone.

### Grade de skins (cards)
Abaixo dos botões, cada skin criada aparece como um **cartão**. Cada cartão mostra:

- **Nome da skin**: o nome que você deu (ex.: "Acme Corp Blue").
- **Selinho "ATIVA"**: aparece em laranja/ciano quando aquela skin é a que está em uso no sistema agora. Só uma skin pode estar ativa por vez.
- **Faixa de prévia de cores**: uma barrinha com 4 quadradinhos coloridos que mostra rapidinho a cara da skin (cor principal, cor de erro, cor de sucesso e cor de fundo).
- **3 botões de ação** (explicados abaixo).

Se não existir nenhuma skin ainda, a tela mostra a mensagem **"Nenhuma skin encontrada"**.

### Botões dentro de cada cartão
| Botão | O que faz |
|---|---|
| **Ativar** | Torna essa skin a **skin oficial** do sistema, que todos os usuários da sua empresa vão ver. Ao clicar, o sistema confirma, aplica a nova aparência e recarrega a página. |
| **Ativa** (cinza, desabilitado) | Quando a skin **já está ativa**, o botão "Ativar" vira um botão cinza travado escrito "Ativa". Não é clicável — só mostra que é a skin em uso. |
| **Editar** | Abre a **janela de edição** com todos os campos preenchidos com os valores atuais, para você alterar o que quiser. |
| **Excluir** | Apaga a skin. Antes de apagar, o sistema pergunta **"Tem certeza que deseja excluir esta skin?"** — clique em "OK" para confirmar ou "Cancelar" para voltar. |

> **Importante sobre excluir:** se a skin estiver **ativa**, o sistema **não deixa excluir**. Aparece um aviso dizendo que você precisa desativá-la primeiro (ative outra skin no lugar). Assim o sistema nunca fica sem aparência.

---

## Botão "Importar Skin" — como usar

1. Clique em **Importar Skin** (ícone de importação).
2. O sistema abre a janela de arquivos do seu computador.
3. Escolha um arquivo **`.json`** que contenha uma skin (geralmente alguém da equipe te envia esse arquivo, ou você guardou de uma configuração anterior).
4. O sistema carrega o arquivo e **cria a skin na lista automaticamente**.
5. Quando der certo, aparece uma mensagem tipo: **"Skin 'Nome' importada com sucesso!"**

**Regras e avisos:**
- O arquivo precisa ser JSON válido e ter um campo de **nome**. Se não tiver, aparece o aviso: *"Arquivo JSON inválido: campo 'name' é obrigatório."*
- Se algo der errado no arquivo, aparece uma mensagem de erro explicando o problema.
- Após importar, você pode clicar em **Editar** no cartão da skin para ajustar cores, fontes, logo etc. antes de ativá-la.

---

## Botão "Usar Template" — janela "Escolher Template"

Este é o jeito mais rápido de criar uma skin nova: você parte de um **modelo pronto** e depois personaliza.

### Como abrir
1. Clique em **Usar Template** (ícone de grade).
2. Abre a janela **"Esccolher Template"** com uma grade de cartões.

### Como preencher / escolher
Cada cartão de template mostra:
- **Nome do template** (ex.: nome do modelo).
- **Prévia de cores**: uma barrinha com 4 cores que mostra o estilo daquele modelo.

Para escolher, **clique no cartão** do template que você quer usar. Pronto — o sistema cria uma skin nova com esse visual e mostra a mensagem: **"Skin 'Nome' criada com sucesso!"**. Ela aparece na lista da tela principal pronta para ser editada ou ativada.

### Botões e ícones da janela
| Elemento | O que faz |
|---|---|
| **X** (no canto superior direito da janela) | Fecha a janela sem escolher nada. |
| **Cartão do template** (clique nele) | Seleciona o template e cria a skin. |
| **Cancelar** (botão no rodapé) | Fecha a janela sem escolher nada. |
| **Clicar fora da janela** (na área escura ao redor) | Também fecha a janela sem escolher nada. |

---

## Janela de Edição / Criação de Skin (modal)

Essa é a janela principal de trabalho. Ela abre de dois jeitos:
- **Criar**: usando **Usar Template** ou **Importar Skin** (aí você edita logo em seguida).
- **Editar**: clicando em **Editar** no cartão de uma skin.

O título da janela muda conforme a situação:
- **"Nova Skin"**: quando você está criando uma do zero.
- **"Editar: [Nome da Skin]"**: quando você está alterando uma existente.

A janela tem um **interruptor** e várias **seções** organizadas por assunto. Vamos ver tudo.

### Interruptor "Tokens Extras" (no topo da janela)
É uma **chavinha deslizante** no canto superior direito, ao lado do título.

- **Desligado (padrão)**: você vê apenas as configurações principais (identidade, cores, fontes básicas, etc.).
- **Ligado**: revela a seção **"Tokens Extras"** (ajustes finos de bordas e sombras) e mostra o botão **"Gerar Dark Mode"** no rodapé. Recomendado para quem já entende um pouco de design.

Quando você liga a chave, os ajustes avançados aparecem na hora; quando desliga, eles se escondem (mas o que você já configurou fica salvo).

---

### Seção "Identidade" — campos

São os dados de identificação da sua empresa e da skin.

| Campo | Obrigatório? | Como preencher |
|---|---|---|
| **Nome da Skin** | Sim | O nome interno da aparência. Ex.: `Acme Corp Blue`. O sistema avisa se você tentar salvar sem preencher. |
| **Nome da Empresa no Sistema** | Não | O nome da sua empresa. Ex.: `Acme Corporation`. **Atenção:** quando você digita aqui, o campo **Copyright** é preenchido automaticamente. |
| **Copyright** | Não (automático) | O texto de rodapé dos direitos autorais. Ele é **gerado sozinho** a partir do nome da empresa, no formato: `© 2026 Acme Corporation. Todos os direitos reservados.` (o ano é sempre o ano atual). Este campo é **somente leitura** — você não digita nele. Se você apagar o nome da empresa, ele limpa sozinho. |
| **Upload do Logo** | Não | Aqui você coloca o **logo** da empresa. Clique na área tracejada (ou arraste um arquivo de imagem para cima dela) e escolha a imagem. Depois de carregado, a área mostra uma prévia do logo. |

**Explicando a área de upload do logo:**
- Parece uma caixa tracejada com o ícone de nuvem com seta para cima e o texto **"Arraste um arquivo ou clique para selecionar"**.
- Clicar nela abre o seletor de arquivos (aceita imagens).
- Ao escolher, a imagem aparece dentro da caixa como prévia.
- Ao editar uma skin que já tem logo, a caixa já vem mostrando o logo atual. Se a imagem quebrar/erro, ela volta ao estado padrão.

---

### Seção "Cores Básicas" — campos

Aqui ficam as cores mais importantes. Cada cor tem **dois controles juntos**:
- **Um quadradinho de cor** (seletor de cor): clica nele e o seletor visual do sistema abre.
- **Um campo de texto** ao lado: mostra o código da cor e permite digitar formatos avançados.

> **Dica importante sobre os dois campos:** quando você usa o quadradinho, o texto é preenchido sozinho. No campo de texto você pode digitar formatos mais avançados (ex.: `rgb(0, 194, 224)`, `oklch(...)`, `color-mix(...)`). Quando você digita um código de cor comum (`#00c2e0`), o quadradinho acompanha; se você digita um formato avançado, o quadradinho fica desabilitado (é normal).

| Cor | O que ela controla | Valor padrão |
|---|---|---|
| **Primary** | A cor principal do sistema — botões principais, destaques, links. | `#00c2e0` (ciano) |
| **Danger** | A cor de **erro/perigo** — mensagens de erro, botões de excluir. | `#ef4444` (vermelho) |
| **Success** | A cor de **sucesso** — mensagens de confirmação, status positivos. | `#10b981` (verde) |
| **Warning** | A cor de **atenção/aviso**. | `#f59e0b` (amarelo/laranja) |
| **Background Main** | A cor de **fundo** principal da tela. | `#f8fafc` (cinza bem claro) |
| **Background Card** | A cor de **fundo dos cartões** (caixas, quadros de informações). | `#ffffff` (branco) |

**Prévia "Cores Básicas"** (embaixo das cores): um mini-teste ao vivo que mostra como vai ficar. Ele exibe um **botão**, selos de **Sucesso / Erro / Atenção** e um **cartão com fundo**. Conforme você mexe nas cores, essa prévia atualiza na hora.

---

### Seção "Cores Avançadas" — campos

Ajustes mais finos de cores. Funcionam do mesmo jeito (quadradinho + campo de texto).

| Cor | O que ela controla | Valor padrão |
|---|---|---|
| **Primary Hover** | A cor do botão principal **quando o mouse passa por cima** dele. | `#00a8c4` (ciano mais escuro) |
| **Text Main** | A cor do **texto principal** (títulos e conteúdo). | `#1e293b` (azul-escuro) |
| **Text Muted** | A cor do **texto secundário** — legendas, descrições, textos de apoio. | `#64748b` (cinza) |
| **Border Color** | A cor das **bordas** — contornos de campos, caixas e divisões. | `#e2e8f0` (cinza claro) |
| **Focus Ring** | A cor do **anel de destaque** quando você clica/tabula em um campo (foco). | `rgba(0, 194, 224, 0.35)` (ciano transparente) |

**Prévia "Cores Avançadas"**: mostra um botão com o efeito hover, um **texto principal**, uma **legenda** (texto secundário), uma **caixa com borda** e um **campo de input focado** (com o anel de foco).

---

### Seção "Dark Mode" — campos

São as cores usadas quando o sistema está no **modo escuro** (tema noturno). Funcionam igual às outras.

| Cor | O que ela controla | Valor padrão |
|---|---|---|
| **Background Main Dark** | Fundo principal no modo escuro. | `#0f172a` (azul quase preto) |
| **Background Card Dark** | Fundo dos cartões no modo escuro. | `#1e293b` (azul-escuro) |
| **Text Main Dark** | Cor do texto principal no modo escuro. | `#f8fafc` (quase branco) |
| **Text Muted Dark** | Cor do texto secundário no modo escuro. | `#94a3b8` (cinza claro) |
| **Border Color Dark** | Cor das bordas no modo escuro. | `rgba(255, 255, 255, 0.05)` (branco bem transparente) |

**Prévia "Dark Mode"**: mostra como ficam o botão e os selos de sucesso/erro e um cartão **com o fundo escuro**, para você conferir o contraste.

> **Dica:** dá para gerar essas cores automaticamente! Ligue o interruptor **"Tokens Extras"** e use o botão **"Gerar Dark Mode"** no rodapé (explicado mais abaixo).

---

### Seção "Tokens Extras" — campos (só aparece com o interruptor ligado)

Esses ajustes controlam o **arredondamento das bordas** (quão "redondinhos" são os cantos) e as **sombras** (o relevo dos elementos).

| Campo | O que controla | Valor padrão |
|---|---|---|
| **Border Radius (sm)** | Cantos dos elementos **pequenos** (ex.: botões pequenos). | `0.25rem` |
| **Border Radius (md)** | Cantos dos elementos **médios** (ex.: campos de formulário). | `0.5rem` |
| **Border Radius (lg)** | Cantos dos elementos **grandes** (ex.: cartões). | `0.75rem` |
| **Border Radius (xl)** | Cantos bem arredondados (ex.: alguns modais/banners). | `1.5rem` |
| **Shadow Card** | A **sombra** dos cartões. | `0 10px 25px rgba(0,0,0,0.1)` |
| **Shadow Modal** | A **sombra** das janelas (modais). | `0 20px 25px -5px rgba(0,0,0,0.2)` |

> **Sobre os valores:** para bordas, valores maiores = cantos mais arredondados. Para sombras, é um código de estilo CSS — mexa com cuidado. A prévia mostra 4 caixas (sm, md, lg, xl) com os raios aplicados e duas caixas com as sombras de card e de modal.

---

### Seção "Fontes" — campos

Aqui você escolhe as **fontes (letras)** do sistema. Cada campo é uma lista suspensa (menu de escolha) com opções prontas.

| Campo | O que controla | Padrão |
|---|---|---|
| **Fonte de Títulos** | A letra usada nos **títulos e cabeçalhos**. | Barlow Condensed |
| **Fonte de Texto** | A letra usada no **corpo dos textos** (conteúdo em geral). | DM Sans |
| **Fonte dos Módulos (Sidebar/Topbar)** | A letra usada no **menu lateral e na barra de cima** do sistema. | DM Sans |

**Opções disponíveis em cada lista:** Barlow Condensed, DM Sans, Inter, Roboto, Open Sans, Lato, Montserrat, Poppins, Nunito e Source Sans Pro. (Se você importar fontes próprias — seção abaixo — elas também aparecem nessas listas.)

**Prévia "Fontes"**: mostra um **título exemplo**, um **parágrafo de texto** e uma linha indicando os **módulos (Sidebar/Topbar)**, todos atualizando ao vivo conforme você troca as fontes.

---

### Seção "Importar Fontes (ZIP)" — como usar

Aqui você coloca **fontes próprias** (personalizadas) dentro do sistema, enviando um arquivo ZIP.

1. **Prepare o arquivo**: um ZIP contendo os arquivos de fonte. Formatos aceitos: `.ttf`, `.otf`, `.woff`, `.woff2`.
2. Clique na área tracejada (**"Clique para selecionar um arquivo ZIP"**, com ícone de pasta compactada) e escolha o `.zip`.
3. O sistema mostra **"Processando ZIP..."** e depois informa quantas fontes foram importadas. Se alguma já existia, ela é ignorada com aviso (ex.: *"2 fonte(s) importada(s), 1 ignorada(s) (já existem)"*).
4. As fontes importadas passam a aparecer nas listas da seção **Fontes** (Fonte de Títulos, Fonte de Texto, Fonte dos Módulos).

**Extras desta seção:**
- **Status de importação**: uma caixa que mostra o resultado ("Processando...", "X fontes importadas", ou mensagem de erro em vermelho).
- **Link "Baixe fontes gratuitas no Font Squirrel"** (com ícone de link externo): abre em nova aba um site com fontes gratuitas para você baixar.

> **Dica:** se o ZIP não tiver nenhuma fonte, aparece o aviso: *"Nenhum arquivo de fonte encontrado no ZIP."*

---

### Seção "Importar Fonte de Icones" — como usar

Aqui você adiciona uma **fonte de ícones** personalizada (para o sistema usar ícones de outro estilo).

1. **Nome da Fonte de Icones** (campo de texto): dê um nome. Ex.: `Material Icons`. Se deixar em branco, o sistema usa o nome do arquivo.
2. **Arquivo de fonte**: clique na área tracejada (ícone de ícones) e escolha um arquivo. Formatos aceitos: `.woff2`, `.ttf`, `.woff`, `.otf`.
3. O sistema mostra **"Enviando..."** e depois a mensagem **"Fonte de icones 'Nome' importada com sucesso."**
4. Depois de importada, aparece o botão **"Remover fonte de icones"** (ícone de lixeira) para desfazer.

**Avisos:**
- Se o formato for inválido, aparece: *"Formato nao suportado. Use .woff2, .woff, .ttf ou .otf."*
- O botão **"Remover fonte de icones"** (lixeira) só aparece depois que uma fonte foi importada. Clicar nele apaga a fonte de ícones da skin atual e volta a área ao estado inicial.

---

### Botões do rodapé da janela (parte de baixo)

| Botão | Ícone | Quando aparece | O que faz |
|---|---|---|---|
| **Reset** | seta curva para a esquerda (desfazer) | Só aparece se você **mexeu em alguma coisa** e ainda não salvou | **Desfaz todas as suas alterações** e volta a janela para os valores originais (como estava quando a janela abriu). |
| **Gerar Dark Mode** | meia-lua/luz (ajustar) | Só aparece com o interruptor **"Tokens Extras" ligado** | **Gera automaticamente** as cores da seção Dark Mode a partir das suas cores claras (ele analisa cada cor clara e cria a versão escura correspondente). Economiza tempo na hora de configurar o modo noturno. |
| **Cancelar** | X | Sempre | **Fecha a janela sem salvar** nada. Tudo que você mexeu é descartado. |
| **Salvar** | disquete (salvar) | Sempre | **Salva a skin** com tudo que você configurou. |

**O que acontece ao clicar em Salvar:**
1. Se o **Nome da Skin** estiver vazio, aparece o aviso "Nome da skin é obrigatório" e nada é salvo.
2. Se tudo certo, a skin é salva (criação nova ou atualização da existente).
3. Aparece a mensagem de sucesso **"Skin salva com sucesso."**
4. O sistema **recarrega a página** automaticamente para aplicar a nova aparência em toda a interface.

---

## Fluxos completos passo a passo

### Criar uma skin nova do zero
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

## Perguntas frequentes (dúvidas comuns)

**Posso ter mais de uma skin salva?**
Sim, você pode salvar quantas quiser. Mas **apenas uma fica ativa** (com o selinho "ATIVA") e é a que os usuários veem.

**Como faço para o sistema usar a skin nova?**
Depois de criar/editar, clique em **Ativar** no cartão. O sistema recarrega e passa a usar a nova aparência.

**Esqueci o nome da empresa e o copyright sumiu.**
O copyright é gerado automaticamente a partir do campo "Nome da Empresa no Sistema". Preencha esse campo e o texto volta sozinho.

**Não estou achando a seção "Tokens Extras".**
Ligue o interruptor **"Tokens Extras"** no topo da janela (a chavinha ao lado do título). É assim que essa seção e o botão "Gerar Dark Mode" aparecem.

**Digitando uma cor no campo de texto, o quadradinho de cor desligou.**
Isso acontece quando você usa um formato de cor avançado (ex.: `color-mix()`). O quadradinho de cor só funciona com cores simples (`#hex`). Sua cor avançada continua válida e será salva normalmente.

**Não consigo excluir uma skin.**
Se a skin está ativa, o sistema impede a exclusão para o sistema nunca ficar sem aparência. Ative outra skin e tente de novo.
