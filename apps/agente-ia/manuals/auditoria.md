# Manual do Módulo Auditoria

O módulo **Auditoria** é uma área só de leitura: você não cadastra nem edita nada aqui. Ele serve para consultar dois tipos de informação:

1. **Registro de Alterações** — tudo que foi criado, alterado ou excluído no sistema.
2. **Tempo de Uso** — os horários em que cada usuário entrou e saiu do sistema.

É o lugar certo para descobrir "quem fez o quê" e "quem estava conectado quando".

---

## Tela Principal: Auditoria

Quando você abre o módulo, a tela já carrega sozinha os dois painéis com os dados. Não precisa clicar em nada para começar. No topo aparece o nome do módulo e a versão do sistema.

A tela mostra dois blocos lado a lado:

- **Registro de Alterações** (ícone de prancheta) — histórico de mudanças no sistema.
- **Tempo de Uso** (ícone de relógio) — histórico de entradas e saídas dos usuários.

Cada bloco tem um total no cabeçalho (ex.: "12 registro(s)" ou "5 sessão(ões)") informando quantos itens existem no total, e mostra **20 itens por página**.

> **Dica:** se não houver nada registrado, aparece a mensagem "Nenhum log registrado." ou "Nenhuma sessão registrada."

---

## Bloco Registro de Alterações

Mostra um histórico das mudanças feitas no sistema, com as colunas abaixo.

### Coluna Data
Quando a alteração aconteceu, com dia, hora e minuto (formato brasileiro). Se não houver data, aparece um travessão (—).

### Coluna Usuário
Nome de quem fez a alteração. Se o nome não estiver disponível, aparece o número de identificação do usuário. Se não houver usuário, aparece um travessão (—). Esta coluna fica oculta em telas menores (celular).

### Coluna Entidade
O que foi mexido (tipo de registro, como "produto", "cliente" etc.), acompanhado do número de identificação do registro quando existir (ex.: "produto #42").

### Coluna Ação
O tipo de mudança feita, mostrado como um selo colorido:

- **Inserção** (selo verde) — algo foi criado.
- **Alteração** (selo amarelo) — algo foi editado.
- **Exclusão** (selo vermelho) — algo foi apagado.

### Coluna Campos Alterados
Quais campos do registro foram modificados, mostrados como pequenos rótulos. Se não houver informação, aparece um travessão (—).

### Coluna IP
O endereço de internet (IP) de onde veio a alteração. Se não estiver disponível, aparece um travessão (—). Esta coluna fica oculta em telas menores (celular).

### Botão Anterior
Volta para a página anterior de registros. Ele fica desabilitado (acinzentado) quando você já está na primeira página. Use a seta para a esquerda (‹).

### Botão Próxima
Avança para a próxima página de registros. Ele fica desabilitado (acinzentado) quando você já está na última página. Use a seta para a direita (›).

> **Para navegar:** no rodapé do bloco aparece "Página X de Y". Clique em **Anterior** e **Próxima** para percorrer as páginas.

---

## Bloco Tempo de Uso

Mostra o histórico de conexões dos usuários, com as colunas abaixo.

### Coluna Login
Quando o usuário entrou no sistema, com dia, hora e minuto (formato brasileiro). Se não houver data, aparece um travessão (—).

### Coluna Logout
Quando o usuário saiu do sistema. Se o usuário ainda está conectado, aparece o selo verde **"Em uso"** no lugar da data.

### Coluna Duração
Quanto tempo o usuário ficou conectado, no formato "2h 5min", "3min 10s" ou "15s". Se não houver informação, aparece um travessão (—).

### Coluna Usuário
Nome de quem esteve conectado. Se o nome não estiver disponível, aparece o número de identificação do usuário. Esta coluna fica oculta em telas menores (celular).

### Coluna IP
O endereço de internet (IP) de onde o usuário se conectou. Se não estiver disponível, aparece um travessão (—). Esta coluna fica oculta em telas menores (celular).

### Coluna Motivo
Por que a sessão terminou:

- **Logout** — o usuário saiu clicando em "Sair".
- **Inatividade** — o usuário ficou parado por muito tempo.
- **Sessão expirada** — o tempo máximo de conexão chegou ao fim.

Se o usuário ainda está conectado, aparece um travessão (—).

### Botão Anterior
Volta para a página anterior de sessões. Ele fica desabilitado (acinzentado) quando você já está na primeira página. Use a seta para a esquerda (‹).

### Botão Próxima
Avança para a próxima página de sessões. Ele fica desabilitado (acinzentado) quando você já está na última página. Use a seta para a direita (›).

> **Para navegar:** no rodapé do bloco aparece "Página X de Y". Clique em **Anterior** e **Próxima** para percorrer as páginas.

---

## Perguntas frequentes

### Posso editar ou apagar um registro de auditoria?
Não. O módulo Auditoria é apenas de consulta. Os registros são gravados automaticamente pelo sistema e não podem ser alterados por ninguém.

### Por que algumas colunas não aparecem?
Em telas menores (como celulares), as colunas **Usuário** e **IP** são ocultadas para facilitar a leitura. Se você vir a tabela sem essas colunas, é por causa do tamanho da tela.

### Preciso preencher algum campo ou abrir algum formulário?
Não. Este módulo não tem formulários nem janelas de cadastro. Os dados aparecem automaticamente assim que a página abre.
