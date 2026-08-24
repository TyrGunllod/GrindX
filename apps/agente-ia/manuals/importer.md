# Manual do Módulo Importar Módulos

> Para quem pergunta: *"o que faz o botão X?"* — este manual explica, em linguagem simples, cada tela, campo e botão do módulo **Importar Módulos** do ERP GrindX.

---

## Tela Principal — "Importar Módulos"

Ao abrir o módulo, você vê o título **"Importar Módulos"**, a versão do sistema, e a descrição: *"Instale e atualize módulos via arquivos .zip."* Logo abaixo ficam duas listas (tabelas).

Quando a página carrega, o sistema já procura os módulos disponíveis. Se nada for encontrado, aparece a mensagem: **"Clique em 'Atualizar' para escanear a pasta de importação."**

### Bloco "Disponíveis para Importar"

Esta é a lista de módulos que estão na pasta de importação do servidor e **ainda não foram instalados** (ou que podem ser atualizados).

Cada linha da lista mostra estas informações:

- **Módulo** — o nome do pacote (.zip) que será instalado.
- **Versão** — a versão do arquivo.
- **Schema** — o banco de dados associado ao módulo (para saber em qual base ele será instalado).
- **Status** — o estado do módulo:
  - **Novo** (etiqueta azul) — ainda não foi instalado.
  - **Importado** (etiqueta verde) — já está instalado no sistema.
- **Ações** — o botão disponível para aquele módulo (Importar ou Remover, conforme o status).

### Botão Atualizar

- **O que faz:** escaneia de novo a pasta de importação do servidor e atualiza a lista de módulos disponíveis.
- **Quando usar:** depois que você colocar um novo arquivo .zip na pasta de importação, clique em **Atualizar** para o sistema enxergar o módulo. Use também se a lista parecer desatualizada.
- **Como usar:** basta clicar no botão (ícone de setas circulando). Enquanto escaneia, aparece um indicador de carregamento.

### Botão Importar (na lista de disponíveis)

- **O que faz:** abre a janela (modal) de confirmação para instalar o módulo no sistema.
- **Onde aparece:** na coluna **Ações**, para módulos com status **Novo** (botão azul com ícone de download).
- **Como usar:**
  1. Clique no botão **Importar** do módulo desejado.
  2. Uma janela de confirmação abre mostrando o nome do módulo.
  3. Clique em **Importar** para confirmar (detalhes no modal **Importar Módulo**).

### Botão Remover (na lista de disponíveis)

- **O que faz:** abre a janela de confirmação para **desinstalar** um módulo que já está instalado.
- **Onde aparece:** na coluna **Ações**, para módulos com status **Importado** (botão vermelho com ícone de lixeira).
- **Como usar:**
  1. Clique no botão **Remover** do módulo.
  2. Uma janela de confirmação abre avisando que os arquivos do módulo serão apagados.
  3. Clique em **Remover** para confirmar (detalhes no modal **Remover Módulo**).

### Bloco "Módulos Instalados"

Esta é a lista dos módulos que **já estão funcionando** no sistema.

Cada linha mostra:

- **Módulo** — o nome do módulo instalado.
- **Versão** — a versão instalada.
- **API** — o banco de dados usado pelo módulo (**SQL Server** ou **PostgreSQL**).
- **Ações** — botão disponível:
  - **Remover** — para módulos que podem ser desinstalados.
  - **Padrão** (etiqueta azul) — módulos do próprio sistema que **não podem** ser removidos.

Se não houver nenhum módulo instalado, a mensagem **"Nenhum módulo instalado."** aparece.

### Botão Remover (na lista de instalados)

- **O que faz:** abre a janela de confirmação para desinstalar o módulo.
- **Onde aparece:** na coluna **Ações** da lista de instalados, como botão vermelho com ícone de lixeira.
- **Como usar:**
  1. Clique no botão **Remover** do módulo.
  2. Confirme na janela que abre (detalhes no modal **Remover Módulo**).
- **Atenção:** módulos com a etiqueta **Padrão** não têm esse botão — eles fazem parte do sistema e não podem ser removidos.

---

## Modal "Importar Módulo"

Janela de confirmação que aparece ao clicar em **Importar** em um módulo disponível.

### Campo "Módulo"

- **O que é:** mostra o nome (identificador) do módulo que será instalado. Serve só para você confirmar que escolheu o pacote certo.
- **Como preencher:** não precisa digitar nada — o campo já vem preenchido com o nome do módulo que você clicou.

### Texto de confirmação

- Mostra a frase: *"Confirme para importar este módulo."*
- É só um aviso pedindo confirmação antes de instalar.

### Botão Importar

- **O que faz:** começa a instalação do módulo.
- **O que acontece ao clicar:**
  1. O botão muda para **"Importando..."** e fica desativado (para não clicar duas vezes).
  2. Dentro da janela aparece uma barra de carregamento e depois a lista de passos concluídos, marcados com ✓.
  3. Ao final aparece a mensagem **"Módulo importado com sucesso!"** e a janela fecha sozinha, atualizando as listas.
- **Dica:** se o servidor precisar reiniciar para concluir, o sistema mostra a mensagem **"Aguardando servidor reiniciar..."** e continua tentando sozinho. Isso pode levar até 1 minuto. Se der timeout, aparece o aviso para **recarregar a página**.

### Botão Cancelar

- **O que faz:** fecha a janela **sem** instalar nada.
- **Como usar:** clique em **Cancelar** se mudar de ideia. Nada é alterado no sistema.

### Botão X (fechar)

- **O que faz:** fecha a janela sem instalar o módulo — mesmo efeito do **Cancelar**.
- **Onde fica:** no canto superior direito da janela (o "×").

---

## Modal "Remover Módulo"

Janela de confirmação que aparece ao clicar em **Remover** em um módulo importado (na lista de disponíveis ou na de instalados).

### Campo "Módulo"

- **O que é:** mostra o nome (identificador) do módulo que será removido.
- **Como preencher:** não precisa digitar nada — o campo já vem preenchido automaticamente.

### Aviso de exclusão

- Mostra o aviso: *"Tem certeza que deseja remover este módulo? Os arquivos backend e frontend serão deletados."*
- **Leia com atenção:** ao remover, os arquivos do módulo são apagados do sistema. Não é possível recuperá-los pela tela.

### Botão Remover

- **O que faz:** apaga o módulo do sistema.
- **O que acontece ao clicar:**
  1. O botão muda para **"Removendo..."** e fica desativado.
  2. Aparece uma barra de carregamento.
  3. Ao terminar, mostra **"Módulo removido com sucesso!"** e a janela fecha sozinha, atualizando as listas.
- **Se der erro:** aparece a mensagem **"Falha: ..."** com o motivo. O botão volta ao normal para você tentar de novo.

### Botão Cancelar

- **O que faz:** fecha a janela **sem** remover nada.
- **Como usar:** clique em **Cancelar** se quiser manter o módulo instalado.

### Botão X (fechar)

- **O que faz:** fecha a janela sem remover o módulo — mesmo efeito do **Cancelar**.
- **Onde fica:** no canto superior direito da janela (o "×").

---

## Resumo rápido

| Situação | O que fazer |
| --- | --- |
| Coloquei um .zip na pasta de importação | Clique em **Atualizar** |
| Instalar um módulo novo | Botão **Importar** → confirme em **Importar** |
| Desinstalar um módulo | Botão **Remover** → confirme em **Remover** |
| Módulo marcado como **Padrão** | Não tem como remover — faz parte do sistema |
| Mudar de ideia no meio | Clique em **Cancelar** ou no **X** |
