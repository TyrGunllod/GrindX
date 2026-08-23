# Manual do Módulo Importar Módulos

## Acesso ao Módulo

Ao abrir o módulo **Importar Módulos**, o sistema verifica se você está autenticado. Caso não esteja logado, você é redirecionado para a tela de login. Somente usuários autenticados conseguem utilizar as funcionalidades desta tela.

Na parte superior da página, é exibido o título **Importar Módulos** com a descrição "Instale e atualize módulos via arquivos .zip.".

## Atualizar Lista de Módulos

No topo da página, há o botão **Atualizar** (ícone de seta circular). Ao clicar, o sistema escaneia a pasta de importação do servidor e atualiza as duas tabelas da tela:

- **Disponíveis para Importar**: módulos encontrados na pasta de importação.
- **Módulos Instalados**: módulos já instalados no sistema.

Se não houver nenhum módulo disponível, a tabela exibe a mensagem "Nenhum módulo disponível. Coloque um .zip na pasta import/ do servidor.".

## Disponíveis para Importar

Esta seção lista os módulos que estão na pasta de importação e ainda podem ser instalados ou removidos. A tabela contém as colunas:

- **Módulo**: nome do módulo.
- **Versão**: versão do módulo.
- **Schema**: identificador do schema do módulo.
- **Status**: pode ser **Importado** (badge verde) ou **Novo** (badge cinza/azulado).
- **Ações**: botão disponível conforme o status do módulo.

Para cada módulo **Novo**, é exibido o botão **Importar** (ícone de download). Para cada módulo **Importado**, é exibido o botão **Remover** (ícone de lixeira).

## Importar um Módulo

Para importar um módulo:

1. Clique em **Atualizar** para escanear a pasta de importação.
2. Na tabela **Disponíveis para Importar**, localize o módulo desejado com status **Novo**.
3. Clique no botão **Importar**.
4. Uma janela é aberta exibindo o nome do módulo e a mensagem "Confirme para importar este módulo.".
5. Clique em **Importar** para confirmar ou em **Cancelar** para desistir.

Durante a importação, o botão muda para **Importando...** e é exibida uma lista de etapas com marcações de sucesso (✓). Ao final, é mostrada a mensagem "Módulo importado com sucesso!" e a tela é atualizada automaticamente.

Se o servidor precisar reiniciar para concluir a importação, o sistema exibe "Aguardando servidor reiniciar..." e verifica o status periodicamente até confirmar que o módulo foi importado. Caso o servidor não responda dentro do tempo limite, aparece a mensagem "Timeout: servidor não respondeu. Recarregue a página.".

## Remover um Módulo

Para remover um módulo já importado:

1. Na tabela **Disponíveis para Importar**, localize o módulo com status **Importado**.
2. Clique no botão **Remover**.
3. Uma janela é aberta exibindo o nome do módulo e a mensagem "Tem certeza que deseja remover este módulo? Os arquivos backend e frontend serão deletados.".
4. Clique em **Remover** para confirmar ou em **Cancelar** para desistir.

Durante a remoção, o botão muda para **Removendo...** e é exibida uma lista de etapas. Ao final, é mostrada a mensagem "Módulo removido com sucesso!" e a tela é atualizada automaticamente. Em caso de falha, a mensagem de erro é exibida e o botão volta ao estado normal.

## Módulos Instalados

Esta seção lista os módulos que já estão instalados no sistema. A tabela contém as colunas:

- **Módulo**: nome do módulo instalado.
- **Versão**: versão instalada.
- **API**: o tipo de banco de dados utilizado pelo módulo, exibido como **SQL Server** ou **PostgreSQL**.
- **Ações**: botão **Remover** para os módulos que podem ser removidos, ou o rótulo **Padrão** (badge) para módulos que não podem ser removidos.

O botão **Remover** desta tabela abre a mesma janela de confirmação de remoção descrita na seção "Remover um Módulo".
