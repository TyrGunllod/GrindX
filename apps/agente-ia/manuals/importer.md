# Manual do Módulo Importar Módulos

O módulo **Importar Módulos** permite instalar e atualizar módulos do GrindX a partir de arquivos `.zip`, além de remover módulos já instalados. Nesta tela você encontra duas listas: os módulos **disponíveis para importar** e os módulos **já instalados**.

---

## Tela Inicial (Importar Módulos)

Ao abrir o módulo, você vê o cabeçalho com o título "Importar Módulos", a versão do sistema e duas tabelas principais. A tabela "Disponíveis para Importar" começa vazia, com a mensagem para clicar em **Atualizar**. A tabela "Módulos Instalados" é carregada automaticamente ao entrar na tela.

### Botões do cabeçalho

- **Atualizar** (ícone de seta circular) — escaneia a pasta de importação do servidor e atualiza a lista "Disponíveis para Importar" com os módulos encontrados.

---

## Disponíveis para Importar

Esta tabela lista os módulos que estão na pasta de importação do servidor e ainda não foram importados (ou que foram importados, mas aparecem para controle). Use o botão **Atualizar** no cabeçalho para carregar esta lista.

### Colunas e campos

- **Módulo** — nome do módulo disponível.
- **Versão** — versão do módulo no arquivo `.zip`.
- **Schema** — nome do banco/schema que o módulo utiliza.
- **Status** — indica o estado do módulo:
  - **Importado** (selo verde) — o módulo já foi instalado.
  - **Novo** (selo azul) — o módulo ainda não foi instalado.
- **Ações** — botão de ação de cada linha (ver abaixo).

### Botões da tabela

- **Importar** (ícone de seta para baixo) — abre a janela de confirmação para instalar o módulo da linha. Aparece apenas quando o módulo ainda não foi importado.
- **Remover** (ícone de lixeira) — abre a janela de confirmação para remover o módulo da linha. Aparece apenas quando o módulo já foi importado.

### Mensagens possíveis

- **"Nenhum módulo disponível. Coloque um .zip na pasta import/ do servidor."** — exibida quando não há nenhum arquivo `.zip` na pasta de importação. Para resolver, adicione o arquivo do módulo na pasta indicada no servidor e clique em **Atualizar**.

---

## Módulos Instalados

Esta tabela mostra os módulos que já estão instalados no sistema. Ela é carregada automaticamente ao entrar na tela.

### Colunas e campos

- **Módulo** — nome do módulo instalado.
- **Versão** — versão instalada do módulo.
- **API** — plataforma do banco de dados usada pelo módulo (por exemplo, "SQL Server" ou "PostgreSQL").
- **Ações** — botão ou selo de cada linha (ver abaixo).

### Botões e indicadores da tabela

- **Remover** (ícone de lixeira) — abre a janela de confirmação para remover o módulo instalado. Aparece apenas para módulos que podem ser removidos.
- **Padrão** (selo azul) — indica que o módulo é padrão do sistema e não pode ser removido. Nesses casos, nenhum botão é exibido.

### Mensagens possíveis

- **"Nenhum módulo instalado."** — exibida quando ainda não há módulos instalados.
- **"Carregando módulos instalados..."** — exibida momentaneamente enquanto a lista é carregada.

---

## Janela: Importar Módulo

Abre ao clicar no botão **Importar** de um módulo na tabela "Disponíveis para Importar". É usada para confirmar a instalação do módulo.

### Como preencher

- **Módulo** — campo somente leitura que mostra o nome do módulo que será importado. Não é editável.
- **Confirmação** — leia a mensagem de confirmação exibida.

### Botões da janela

- **Cancelar** — fecha a janela sem importar nada.
- **Importar** — confirma a operação e inicia a instalação do módulo. Durante o processo, o botão muda para **Importando...** e fica desabilitado até terminar.
- **X** (no canto superior direito) — fecha a janela sem realizar a operação.

### Resultado da importação

Após clicar em **Importar**, é exibido um registro (log) do progresso, com um passo marcado com "✓" para cada etapa concluída. Ao final:

- **"Módulo importado com sucesso!"** — a instalação foi concluída e a janela fecha automaticamente, recarregando as listas.
- **"Aguardando servidor reiniciar..."** — o servidor precisa reiniciar para concluir a instalação. Aguarde a mensagem mudar para "Módulo importado com sucesso!".
- **"Timeout: servidor não respondeu. Recarregue a página."** — o servidor demorou demais para responder. Recarregue a página e tente novamente.

---

## Janela: Remover Módulo

Abre ao clicar no botão **Remover** de um módulo (na tabela "Disponíveis para Importar" ou "Módulos Instalados"). É usada para confirmar a exclusão do módulo.

### Como preencher

- **Módulo** — campo somente leitura que mostra o nome do módulo que será removido. Não é editável.
- **Aviso** — leia a mensagem de aviso: os arquivos do módulo (backend e frontend) serão apagados.

### Botões da janela

- **Cancelar** — fecha a janela sem remover nada.
- **Remover** — confirma a operação e apaga o módulo. Durante o processo, o botão muda para **Removendo...** e fica desabilitado até terminar.
- **X** (no canto superior direito) — fecha a janela sem realizar a operação.

### Resultado da remoção

- **"Módulo removido com sucesso!"** — a remoção foi concluída e a janela fecha automaticamente, recarregando as listas.
- **"Falha: ..."** — ocorreu um erro e o módulo não foi removido. O botão **Remover** volta a ficar disponível para nova tentativa.

---

## Permissões

Este módulo exige autenticação: ao acessar a tela sem estar autenticado, o usuário é redirecionado para a tela de login do sistema. As ações de importar e remover só ficam disponíveis para módulos em que a opção correspondente é apresentada (módulos "Padrão" não exibem o botão de remoção).
