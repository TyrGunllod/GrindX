Atue como um Desenvolvedor Full Stack Sênior. Preciso que você crie o código de um Módulo Central de Mensagens e Notificações Internas Assíncronas para uma aplicação ERP existente.

### 1. Contexto Técnico da Aplicação
- **Frontend:** HTML5, CSS3 e JavaScript Vanilla (sem frameworks como React ou Vue).
- **Arquitetura de Tela:** Estrutura Shell (Janela Pai) contendo um Mascote fixo na tela e um elemento `<iframe id="conteudo-principal">` onde os módulos (Estoque, Vendas, Financeiro) são carregados.
- **Comunicação:** API REST tradicional (CRUD assíncrono). Não utilize WebSockets nem tempo real.
- **Banco de Dados:** PostgreSQL.
- **Linguagem Backend:** Padrão GrindX

### 2. O que deve ser implementado

#### A. Banco de Dados (PostgreSQL - Script SQL)
- Script DDL para criação da tabela `mensagens`:
  - `id` BIGSERIAL PRIMARY KEY
  - `remetente_id` BIGINT NULL (FK para a tabela de usuários; NULL indica mensagem gerada pelo sistema)
  - `destinatario_id` BIGINT NOT NULL (FK para a tabela de usuários)
  - `titulo` VARCHAR(150) NOT NULL
  - `texto` TEXT NOT NULL
  - `categoria` VARCHAR(50) NOT NULL DEFAULT 'DIRETA' -- Ex: 'SISTEMA', 'DIRETA', 'AVISO'
  - `url_acao` VARCHAR(255) NULL -- Ex: "modulos/estoque/produto.html?id=88"
  - `lida_em` TIMESTAMP WITH TIME ZONE NULL
  - `criado_em` TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
- Criação de índices otimizados no PostgreSQL para consultas frequentes por `destinatario_id` e mensagens não lidas (`lida_em IS NULL`).

#### B. API REST Backend
- `GET /api/mensagens`: Retorna as mensagens recebidas pelo usuário logado (com suporte a filtro de não lidas).
- `GET /api/mensagens/nao-lidas/count`: Retorna apenas o número total de mensagens não lidas para o mascote.
- `POST /api/mensagens`: Endpoint para criar e enviar uma mensagem (usado pelo sistema ou por usuários).
- `PATCH /api/mensagens/:id/lida`: Atualiza o campo `lida_em` com a data/hora atual (`NOW()`).

#### C. Frontend na Janela Pai (Shell / Notificação pelo Mascote)
- **HTML/CSS:** 
  - Elemento do Mascote fixo na Janela Pai.
  - Balão de fala (speech bubble) ou badge de alerta acoplado ao mascote indicando a quantidade de mensagens não lidas (ex: "Você tem 3 novos recados!").
  - Pagina de recados que se abre ao clicar no balão de fala. Tambem disponível o acesso via mesmo dropdown do meu perfil, colocando abaixo do meu perfil o botão "Mensagens"
- **JS (Painel Pai):**
  1. Função para carregar a quantidade de mensagens não lidas ao abrir a página e em intervalo regular (polling a cada 10 minutos).
  2. Atualizar a interface do mascote dinamizando a visibilidade do balão de fala e a classe CSS de alerta (ex: fazer o mascote acenar ou destacar o balão quando houver mensagens pendentes).
  3. Função para carregar e renderizar a lista de mensagens dentro do painel ao clicar no mascote.
  4. Ao clicar em uma mensagem dentro do painel:
     - Enviar requisição `PATCH` para marcar como lida e recalcular o estado do mascote.
     - Alterar o atributo `src` do `<iframe id="conteudo-principal">` utilizando a `url_acao` da mensagem.

#### D. Comunicação entre Módulo (Iframe) e Janela Pai
- Forneça uma função utilitária Vanilla JS executável DENTRO do iframe que envie um aviso para a janela pai (`window.parent`) disparar a verificação de novas mensagens no mascote sempre que um evento de negócio importante acontecer.

Não executar, criar spec, plan e task.
Dúvidas, não decidir, trazer opçoes para decidir com o desenvolvedor.