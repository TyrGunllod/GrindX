# Manual do Módulo Auditoria

## Sobre o Módulo

O módulo **Auditoria** do GrindX é uma tela de **consulta** (somente leitura). Aqui você acompanha dois tipos de informação sobre o que acontece no sistema:

1. **Registro de Alterações** — um histórico de tudo que foi criado, alterado ou excluído no banco de dados, incluindo quem fez, o que mudou e de onde.
2. **Tempo de Uso** — o registro de quando cada usuário entrou (login) e saiu (logout) do sistema, por quanto tempo ficou e o motivo do término da sessão.

Você não consegue editar, excluir ou cadastrar nada nesta tela. Ela serve apenas para **consultar e fiscalizar**.

### Como acessar

1. Faça login no GrindX.
2. No menu lateral (ou menu principal), clique em **Auditoria**.
3. A tela abre já carregando as duas tabelas automaticamente. Não precisa clicar em nada para carregar.

> **Permissão:** para ver esta tela você só precisa estar logado no sistema. Se você ainda não fez login, o sistema te redireciona para a tela de login.

### O que você vê no topo da tela

- **Título "Auditoria"** — o nome do módulo.
- **Versão do sistema** — um selo pequeno ao lado do título que mostra a versão atual do GrindX. Serve para você saber qual versão do sistema você está usando.
- **Subtítulo** — "Registro de alterações no banco e tempo de uso dos usuários." Explica resumidamente o que o módulo faz.

---

## Registro de Alterações

Esta é a primeira tabela da tela. Ela mostra o **histórico de mudanças feitas nos dados** do sistema: quem criou, alterou ou excluiu um registro, quando e quais campos foram mexidos.

No topo do cartão você vê o ícone de **prancheta com lista** (📋) e o texto **"Registro de Alterações"**, além de um selo cinza que mostra o **total de registros encontrados**, por exemplo `1.250 registro(s)`. Esse número se refere ao total geral (e não só aos registros da página atual).

### Colunas da tabela

Cada linha representa **uma ação feita por um usuário** em um registro. As colunas são:

| Coluna | O que mostra |
|--------|--------------|
| **Data** | A data e a hora em que a ação aconteceu, no formato brasileiro (ex.: `23/08/2026 14:32`). |
| **Usuário** | Quem fez a ação. Mostra o nome de login (username) do usuário. Se o nome não estiver disponível, aparece o número identificador do usuário (ex.: `#42`). Se não houver informação, aparece `—`. *(Coluna oculta em telas pequenas, como celular.)* |
| **Entidade** | Qual tipo de registro foi mexido (ex.: Produto, Cliente, Pedido). Se for possível identificar o registro específico, aparece o nome da entidade seguido do seu número, ex.: `Produto #7`. |
| **Ação** | O tipo de ação feita, mostrada como um **selo colorido**: |
| | - **Inserção** (selo **verde**) — um novo registro foi criado. |
| | - **Alteração** (selo **amarelo**) — um registro existente foi editado. |
| | - **Exclusão** (selo **vermelho**) — um registro foi apagado. |
| | - **Outros** (selo **cinza**) — ações de outros tipos, mostradas com o nome original. |
| **Campos Alterados** | Lista de **quais campos** (colunas do registro) foram modificados naquela ação, cada um dentro de um selinho pequeno. Ex.: `nome`, `preço`. Se não houver campos listados, aparece `—`. |
| **IP** | O endereço de IP (computador/rede) de onde o usuário fez a ação. Se não houver, aparece `—`. *(Coluna oculta em telas pequenas.)* |

> **Dica:** nas telas pequenas (celular), as colunas **Usuário** e **IP** ficam ocultas para caber melhor. As demais continuam visíveis.

### Paginação (navegar entre páginas)

Cada página mostra **até 20 registros**. No rodapé da tabela você encontra:

- **Botão "Anterior"** (com a setinha para a esquerda `‹`) — leva você para a **página anterior** de logs. Ele fica **desativado** (acinzentado) quando você já está na primeira página.
- **Texto "Página X de Y"** — mostra em qual página você está e quantas páginas existem no total (ex.: `Página 1 de 12`).
- **Botão "Próxima"** (com a setinha para a direita `›`) — leva você para a **próxima página** de logs. Ele fica **desativado** quando você já está na última página.

Não existe campo para escolher o número da página digitando; você navega clicando nos botões **Anterior** e **Próxima**.

### Mensagens possíveis na tabela

- **"Nenhum log registrado."** — não existe nenhuma alteração registrada no sistema até o momento.
- **"Erro ao carregar logs de auditoria."** — aconteceu um problema ao buscar os dados (por exemplo, sem conexão com a internet). Nesse caso, verifique sua conexão e tente acessar a tela novamente.

---

## Tempo de Uso

Esta é a segunda tabela da tela. Ela mostra o **histórico de sessões dos usuários**: quando cada um entrou, quando saiu, quanto tempo ficou logado e o motivo pelo qual a sessão terminou.

No topo do cartão você vê o ícone de **relógio** (🕐) e o texto **"Tempo de Uso"**, além do selo com o **total de sessões encontradas**, por exemplo `480 sessão(ões)`.

### Colunas da tabela

Cada linha representa **uma sessão de login** de um usuário. As colunas são:

| Coluna | O que mostra |
|--------|--------------|
| **Login** | A data e a hora em que o usuário **entrou** no sistema (ex.: `23/08/2026 08:05`). |
| **Logout** | A data e a hora em que o usuário **saiu** do sistema. Se a sessão **ainda está aberta** (o usuário está logado agora), aparece o selo verde **"Em uso"** em vez de uma data. |
| **Duração** | Por quanto tempo a sessão durou. O formato se adapta: |
| | - Sessões longas: ex. `2h 15min`. |
| | - Sessões médias: ex. `45min 30s`. |
| | - Sessões curtas: ex. `30s`. |
| | - Se não houver informação, aparece `—`. |
| **Usuário** | Quem estava logado. Mostra o nome de login; se não estiver disponível, aparece o número identificador (ex.: `#42`). *(Coluna oculta em telas pequenas.)* |
| **IP** | O endereço de IP de onde a pessoa entrou no sistema. Se não houver, aparece `—`. *(Coluna oculta em telas pequenas.)* |
| **Motivo** | O motivo pelo qual a sessão terminou: |
| | - **Logout** — o usuário saiu clicando no botão de sair do sistema. |
| | - **Inatividade** — o usuário ficou um tempo sem mexer no sistema e foi desconectado automaticamente. |
| | - **Sessão expirada** — o tempo máximo de sessão acabou e o sistema encerrou. |
| | - Se não houver informação, aparece `—`. |

> **Dica:** use a coluna **Logout** para descobrir quem está **conectado agora** no sistema — as linhas com o selo verde "Em uso" indicam sessões abertas.

### Paginação (navegar entre páginas)

Igual à tabela anterior: cada página mostra **até 20 sessões**.

- **Botão "Anterior"** (setinha para a esquerda `‹`) — volta para a **página anterior**. Fica desativado na primeira página.
- **Texto "Página X de Y"** — sua posição atual na listagem.
- **Botão "Próxima"** (setinha para a direita `›`) — avança para a **próxima página**. Fica desativado na última página.

### Mensagens possíveis na tabela

- **"Nenhuma sessão registrada."** — não existe nenhuma sessão de uso registrada até o momento.
- **"Erro ao carregar sessões de uso."** — aconteceu um problema ao buscar os dados. Verifique sua conexão e tente novamente.

---

## Resumo rápido (até aqui, tudo que você clica)

| Elemento | O que faz |
|----------|-----------|
| Menu **Auditoria** | Abre este módulo. |
| **Anterior** (em "Registro de Alterações") | Volta uma página nos logs de alterações. |
| **Próxima** (em "Registro de Alterações") | Avança uma página nos logs de alterações. |
| **Anterior** (em "Tempo de Uso") | Volta uma página no histórico de sessões. |
| **Próxima** (em "Tempo de Uso") | Avança uma página no histórico de sessões. |

Não existem modais, formulários ou janelas de preenchimento neste módulo: ele é inteiramente de consulta. A navegação se resume a trocar de página nas duas tabelas.

---

## Perguntas frequentes

**1. Por que a coluna "Usuário" some quando acesso pelo celular?**
Porque o sistema esconde algumas colunas em telas pequenas para a tabela ficar legível. A mesma informação continua disponível ao acessar por um computador ou tablet.

**2. Um registro aparece na tabela mas não sei qual era o dado antigo.**
A tabela mostra **quais campos** foram alterados (na coluna "Campos Alterados"), mas não mostra o valor antigo. Para isso, é preciso verificar o cadastro atual do registro no módulo correspondente.

**3. Vejo "Em uso" na coluna Logout. O que significa?**
Significa que a sessão do usuário **está aberta agora** — ou seja, essa pessoa está logada no sistema neste momento.

**4. O que são "Inatividade" e "Sessão expirada" no motivo do logout?**
- **Inatividade:** o usuário ficou muito tempo sem mexer no sistema e foi desconectado automaticamente.
- **Sessão expirada:** o tempo máximo permitido para uma sessão foi atingido, então o sistema encerrou a sessão por segurança.

**5. Posso apagar algum registro desta tela?**
Não. O módulo Auditoria é de consulta. Apenas os registros do sistema geram automaticamente os logs; você não pode criar, editar ou excluir nada aqui.
