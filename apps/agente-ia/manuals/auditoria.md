# Manual do Módulo Auditoria

O módulo **Auditoria** permite acompanhar, em modo somente leitura, tudo o que acontece no sistema: as alterações feitas nos registros e o tempo de uso de cada usuário.

## Acesso ao Módulo

Para acessar, é necessário estar autenticado no sistema. Se o usuário não tiver uma sessão ativa, ele é redirecionado para a tela de login.

Ao abrir o módulo, o topo da página exibe o título **Auditoria**, a versão do sistema e a descrição: *"Registro de alterações no banco e tempo de uso dos usuários."*

Logo abaixo, são apresentadas duas seções:

1. **Registro de Alterações** — mostra as mudanças feitas nos dados do sistema.
2. **Tempo de Uso** — mostra as sessões de login e logout dos usuários.

## Registro de Alterações

Esta seção lista as alterações realizadas nos registros do sistema. No cabeçalho, à direita, aparece o total de registros encontrados (por exemplo, "120 registro(s)").

Cada linha da tabela exibe:

- **Data** — data e hora em que a alteração foi feita.
- **Usuário** — nome de usuário responsável pela alteração. Se o usuário não for identificado, aparece "—".
- **Entidade** — o tipo de registro alterado (por exemplo, "Cliente"), acompanhado do número de identificação quando existir (por exemplo, "Cliente #42").
- **Ação** — o tipo de operação realizada, exibido como um selo colorido:
  - **Inserção** (verde) — um novo registro foi criado.
  - **Alteração** (amarelo) — um registro existente foi modificado.
  - **Exclusão** (vermelho) — um registro foi removido.
- **Campos Alterados** — os nomes dos campos que foram modificados, exibidos como etiquetas. Se nenhum campo foi alterado, aparece "—".
- **IP** — o endereço de rede de onde a alteração foi feita.

### Paginação

No rodapé da seção, há controles para navegar entre as páginas de resultados:

- **Anterior** — volta para a página anterior.
- **Próxima** — avança para a próxima página.

Entre os botões, é exibido o texto **"Página X de Y"** indicando a posição atual. O botão **Anterior** fica desabilitado na primeira página e o botão **Próxima** fica desabilitado na última.

## Tempo de Uso

Esta seção mostra quanto tempo cada usuário permaneceu conectado. No cabeçalho, à direita, aparece o total de sessões (por exemplo, "35 sessão(ões)").

Cada linha da tabela exibe:

- **Login** — data e hora em que o usuário entrou no sistema.
- **Logout** — data e hora em que o usuário saiu. Se a sessão ainda estiver ativa, aparece o selo **"Em uso"** (verde) no lugar da data.
- **Duração** — tempo total da sessão, exibido de forma resumida:
  - Horas e minutos quando a sessão durou mais de uma hora (ex.: "2h 15min").
  - Minutos e segundos quando durou menos de uma hora (ex.: "12min 30s").
  - Apenas segundos para sessões muito curtas (ex.: "45s").
- **Usuário** — nome de usuário da sessão.
- **IP** — endereço de rede de onde o usuário se conectou.
- **Motivo** — o motivo do encerramento da sessão:
  - **Logout** — o usuário saiu manualmente.
  - **Inatividade** — a sessão foi encerrada por falta de atividade.
  - **Sessão expirada** — a sessão expirou automaticamente.

### Paginação

Da mesma forma que na seção de alterações, o rodapé oferece os botões **Anterior** e **Próxima**, com o texto **"Página X de Y"** entre eles, para navegar pelos registros de sessões.
