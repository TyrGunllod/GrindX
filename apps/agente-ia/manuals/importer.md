# Manual do Módulo Importar Módulos

## O que é este módulo

A tela **Importar Módulos** serve para você **instalar e atualizar módulos** do GrindX usando arquivos `.zip`. Se você recebeu um pacote de um novo módulo (ou uma atualização), é aqui que você o coloca para funcionar no sistema — sem precisar mexer em nada técnico.

A tela faz basicamente duas coisas:
- Mostra os módulos **que estão disponíveis para instalar** (os arquivos `.zip` que o sistema encontrou na pasta de importação do servidor).
- Mostra os módulos que **já estão instalados** no sistema.

Você também consegue **remover** módulos instalados por aqui. Para usar a tela, você precisa estar **logado no sistema** — sem login, você é redirecionado para a tela de entrada.

No topo da página, ao lado do título "Importar Módulos", aparece um selo com a **versão do sistema** em uso.

---

## Acessando a tela

1. Faça login no GrindX.
2. Abra o módulo **Importar Módulos** pelo menu do sistema.
3. A página abre com duas tabelas vazias e um aviso: *"Clique em 'Atualizar' para escanear a pasta de importação."* — é isso que você vai fazer primeiro.

> Dica para iniciantes: a primeira coisa a fazer ao abrir a tela é clicar no botão **Atualizar**. Sem isso, a lista de módulos disponíveis não é carregada.

---

## Botão Atualizar

Fica no canto superior direito da tela.

| Item | O que faz |
|------|-----------|
| Ícone de setas circulares (sincronizar) | Indica que é um botão de recarregar/refrescar. |
| Texto **Atualizar** | Aparece em telas maiores (desktop). Em telas pequenas (celular), o texto fica oculto e só o ícone aparece. |

**O que ele faz:** ele *escaneia* a pasta de importação do servidor à procura de arquivos `.zip` de módulos e atualiza as duas listas da tela:
- A tabela **Disponíveis para Importar** passa a mostrar os novos módulos encontrados.
- A tabela **Módulos Instalados** passa a mostrar o que está instalado naquele momento.

Use o **Atualizar** sempre que quiser conferir se há novidades, ou depois de colocar um novo `.zip` na pasta de importação. Enquanto a varredura acontece, aparece um **carregando (spinner)** no lugar da lista.

---

## Tabela: Disponíveis para Importar

É a primeira tabela da tela. Mostra os módulos encontrados na pasta de importação do servidor, prontos para serem instalados.

**Colunas:**

- **Módulo** — o nome do módulo.
- **Versão** — a versão do pacote que está disponível.
- **Schema** — o nome do esquema de banco de dados que o módulo usa. Você não precisa fazer nada com isso; é só informação.
- **Status** — mostra um selo (badge) colorido:
  - **Novo** (selo cinza) — o módulo ainda não foi instalado no sistema.
  - **Importado** (selo verde) — o módulo já está instalado. Nesse caso, o que está disponível na pasta é na prática uma **atualização** dele.
- **Ações** — o botão disponível para aquele módulo (veja abaixo).

**Botões da coluna Ações:**

| Botão/Ícone | Quando aparece | O que faz |
|-------------|----------------|-----------|
| **Importar** (ícone de seta para baixo/baixar) | Quando o status é **Novo** | Abre a janela **Importar Módulo** para instalar o módulo. Em celular, o texto some e fica só o ícone. |
| **Remover** (ícone de lata de lixo) | Quando o status é **Importado** | Abre a janela **Remover Módulo**. Aqui ele é útil se você instalou uma atualização e quer desinstalar. |

**Situações que você pode ver aqui:**

- *"Nenhum módulo disponível. Coloque um .zip na pasta import/ do servidor."* — não há nenhum pacote na pasta de importação. Você precisa que alguém com acesso ao servidor coloque o arquivo `.zip` do módulo lá.
- A tabela vazia com a mensagem *"Clique em 'Atualizar'..."* — você ainda não clicou em **Atualizar** nesta sessão.

> Observação de permissão: só aparece nesta lista o que realmente está na pasta de importação. Se o `.zip` estiver com nome errado ou corrompido, ele pode não aparecer — nesse caso, peça ajuda de quem administra o servidor.

---

## Tabela: Módulos Instalados

É a segunda tabela da tela. Mostra os módulos que **já estão rodando** no sistema.

**Colunas:**

- **Módulo** — o nome do módulo instalado.
- **Versão** — a versão instalada.
- **API** — o banco de dados onde o módulo funciona. Pode aparecer como **SQL Server** ou **PostgreSQL**. É só informação.
- **Ações** — o que você pode fazer com o módulo:

| Item | Quando aparece | O que faz |
|------|----------------|-----------|
| **Remover** (ícone de lata de lixo) | Quando o módulo pode ser desinstalado | Abre a janela **Remover Módulo** para desinstalá-lo. |
| **Padrão** (selo cinza) | Quando o módulo é essencial para o sistema | Esse módulo **não pode ser removido** por você. O selo indica que ele é um módulo padrão do GrindX. |

**Situações que você pode ver aqui:**

- *"Carregando módulos instalados..."* — a lista ainda está sendo carregada; aguarde um instante.
- *"Nenhum módulo instalado."* — não há nenhum módulo instalado no momento.

> Observação de permissão: o botão **Remover** só aparece para módulos que o sistema permite desinstalar. Módulos **Padrão** não têm esse botão justamente porque são protegidos.

---

## Janela (Modal): Importar Módulo

Essa janela aparece quando você clica em **Importar** em um módulo disponível.

### Como abrir
1. Clique em **Atualizar** para carregar a lista de disponíveis.
2. Na linha do módulo desejado, clique no botão **Importar** (ícone de seta para baixo).

### O que você vê
- **Título:** "Importar Módulo".
- **Módulo:** o nome do módulo que você escolheu (apenas para conferir).
- Uma mensagem: *"Confirme para importar este módulo."*

### Como preencher/agir — campo a campo
Não há campos para digitar. A janela só pede uma confirmação:

| Elemento | O que faz |
|----------|-----------|
| **X** (canto superior direito) | Fecha a janela sem importar nada. |
| **Cancelar** | Fecha a janela sem importar nada. Mesmo efeito do **X**. |
| **Importar** (botão azul) | Confirma e inicia a instalação do módulo. |

### O que acontece depois que você confirma
1. O botão muda para **"Importando..."** e fica desativado (você não pode clicar de novo).
2. Dentro da janela aparece uma área de **log** (o passo a passo da instalação), com uma animação de carregamento.
3. Cada passo concluído aparece com uma marca de visto **✓** em verde.
4. Ao terminar, aparece a mensagem **"Módulo importado com sucesso!"** e a janela fecha sozinha depois de alguns segundos. A lista é atualizada automaticamente.

### Se o sistema precisar reiniciar
Alguns módulos exigem que o servidor seja reiniciado para terminar a instalação. Nesse caso, você verá:
- A mensagem **"Aguardando servidor reiniciar..."** e um contador de tentativas (ex.: `1/30`).
- O sistema fica aguardando o servidor voltar e conferindo sozinho se o módulo foi importado. Isso pode levar até 1 minuto.
- Quando o servidor volta e o módulo é confirmado, aparece **"✓ Módulo importado com sucesso!"** e a janela fecha.
- Se o servidor não responder, aparece a mensagem de erro *"Timeout: servidor não respondeu. Recarregue a página."* Nesse caso, recarregue a página e clique em **Atualizar** para ver se o módulo foi instalado.

---

## Janela (Modal): Remover Módulo

Essa janela aparece quando você clica em **Remover** em um módulo (disponível ou instalado, desde que ele possa ser removido).

### Como abrir
- Na tabela **Disponíveis para Importar**: no módulo com status **Importado**, clique no botão **Remover** (lata de lixo).
- Na tabela **Módulos Instalados**: no módulo que não tem o selo **Padrão**, clique no botão **Remover** (lata de lixo).

### O que você vê
- **Título:** "Remover Módulo".
- **Módulo:** o nome do módulo que você escolheu.
- Uma mensagem de aviso: *"Tem certeza que deseja remover este módulo? Os arquivos backend e frontend serão deletados."*

### Como agir — campo a campo
Também não há campos para digitar, só confirmação:

| Elemento | O que faz |
|----------|-----------|
| **X** (canto superior direito) | Fecha a janela sem remover nada. |
| **Cancelar** | Fecha a janela sem remover nada. Mesmo efeito do **X**. |
| **Remover** (botão azul) | Confirma e remove o módulo do sistema. |

> ⚠️ **Atenção:** a remoção é definitiva. Os arquivos do módulo são apagados. Só confirme se tiver certeza.

### O que acontece depois que você confirma
1. O botão muda para **"Removendo..."** e fica desativado.
2. Aparece o **log** com cada passo da remoção marcado com **✓** em verde.
3. Ao terminar, aparece **"Módulo removido com sucesso!"** e a janela fecha sozinha. A lista é atualizada automaticamente.
4. Se algo der errado, aparece uma mensagem em vermelho tipo **"Falha: ..."** com o motivo. O botão volta ao normal para você tentar novamente.

---

## Resumo rápido dos botões e ícones

| Ícone | Nome | Onde fica | O que faz |
|-------|------|-----------|-----------|
| 🔄 setas circulares | **Atualizar** | Topo da tela | Escaneia a pasta de importação e recarrega as duas listas. |
| ⬇️ seta para baixo | **Importar** | Linha de um módulo **Novo** | Abre a janela para instalar o módulo. |
| 🗑️ lata de lixo | **Remover** | Linha de um módulo **Importado** ou instalado | Abre a janela para desinstalar o módulo. |
| ✖️ X | **Fechar** | Canto do modal | Fecha a janela sem fazer nada. |
| — | **Cancelar** | Rodapé do modal | Fecha a janela sem fazer nada. |
| — | **Importar** (no modal) | Rodapé do modal | Confirma a instalação. |
| — | **Remover** (no modal) | Rodapé do modal | Confirma a remoção. |
| 🏷️ selo cinza **Padrão** | — | Linha de um módulo instalado | Indica módulo essencial que não pode ser removido. |

---

## Dicas finais

- **Sempre clique em Atualizar** depois de colocar um novo `.zip` na pasta de importação do servidor — senão o módulo não aparece na lista.
- Depois de importar ou remover um módulo, a tela se atualiza sozinha; não precisa recarregar a página manualmente.
- Em celular, as tabelas viram cartões e os rótulos das colunas aparecem acima de cada valor, para ficar mais fácil de ler.
- Se um módulo aparecer com status **Importado** na tabela de disponíveis, é porque já existe uma versão instalada — nesse caso você pode importar para atualizar ou remover.
