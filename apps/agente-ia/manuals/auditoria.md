# Manual do Módulo Auditoria

O módulo **Auditoria** do GrindX permite visualizar o histórico de alterações feitas no sistema e o tempo de uso de cada usuário. É um módulo **somente de leitura** (consulta): aqui não se cria, edita nem exclui nada.

A tela é dividida em duas áreas (cards):

- **Registro de Alterações** — mostra tudo o que foi inserido, alterado ou excluído no banco de dados.
- **Tempo de Uso** — mostra as sessões de login e logout dos usuários, com a duração de cada uma.

## Registro de Alterações

Esta seção lista o histórico de mudanças realizadas no sistema, organizadas em uma tabela com as colunas descritas abaixo. Os registros aparecem em ordem, com os mais recentes primeiro.

### Colunas da tabela

- **Data** — data e hora em que a alteração foi registrada.
- **Usuário** — nome de usuário que fez a alteração. Quando o nome não está disponível, é mostrado o código do usuário precedido de `#`. Se não houver usuário associado, aparece `—`.
- **Entidade** — o que foi alterado (tipo de registro), seguido do número de identificação. Exemplo: `Cliente #123`.
- **Ação** — o tipo de mudança, exibido como uma etiqueta colorida:
  - **Inserção** (verde) — um novo registro foi criado.
  - **Alteração** (amarelo) — um registro existente foi modificado.
  - **Exclusão** (vermelho) — um registro foi removido.
- **Campos Alterados** — lista dos campos que foram modificados, exibidos como etiquetas separadas. Se não houver campos informados, aparece `—`.
- **IP** — endereço IP de onde a alteração foi feita. Se não houver informação, aparece `—`.

### Botões

- **Anterior** — volta para a página anterior de registros. Fica desativado quando já se está na primeira página.
- **Próxima** — avança para a página seguinte de registros. Fica desativado quando já se está na última página.

Entre os dois botões aparece a indicação **"Página X de Y"**, informando em qual página se está e o total de páginas disponíveis. No topo do card, ao lado do título, é exibido o **total de registros** (exemplo: `150 registro(s)`).

## Tempo de Uso

Esta seção mostra as sessões de uso dos usuários, ou seja, quando cada um entrou e saiu do sistema e quanto tempo ficou conectado.

### Colunas da tabela

- **Login** — data e hora em que o usuário entrou no sistema.
- **Logout** — data e hora em que o usuário saiu. Se a sessão ainda estiver ativa, aparece a etiqueta verde **"Em uso"** no lugar da data.
- **Duração** — tempo total da sessão, no formato:
  - `Xh Xmin` quando durou uma hora ou mais;
  - `Xmin Xs` quando durou menos de uma hora;
  - `Xs` quando durou menos de um minuto.
  - Se a duração não estiver disponível, aparece `—`.
- **Usuário** — nome de usuário. Quando o nome não está disponível, é mostrado o código do usuário precedido de `#`.
- **IP** — endereço IP usado na sessão. Se não houver informação, aparece `—`.
- **Motivo** — o motivo do encerramento da sessão:
  - **Logout** — o usuário saiu normalmente.
  - **Inatividade** — a sessão foi encerrada por inatividade.
  - **Sessão expirada** — a sessão venceu.
  - Se a sessão ainda estiver ativa (sem logout), aparece `—`.

### Botões

- **Anterior** — volta para a página anterior de sessões. Fica desativado quando já se está na primeira página.
- **Próxima** — avança para a página seguinte de sessões. Fica desativado quando já se está na última página.

Entre os dois botões aparece a indicação **"Página X de Y"**. No topo do card, ao lado do título, é exibido o **total de sessões** (exemplo: `300 sessão(ões)`).
