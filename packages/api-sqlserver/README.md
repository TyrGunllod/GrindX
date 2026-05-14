# ERP — API SQL Server (Consulta)

Esta API é responsável por realizar consultas de leitura no banco de dados SQL Server legado (WAN). Por design, esta API não permite operações de escrita, servindo apenas para integração de dados de clientes e faturamento.

## 🚀 Funcionalidades

- **Consulta de Clientes:** Listagem paginada e busca por ID/CNPJ.
- **Filtros Avançados:** Filtros por razão social, cidade e UF.
- **Segurança:** 
  - Validação de tokens JWT emitidos pela `api-postgres`.
  - Controle de acesso (Read-only).
  - Middlewares de Rate Limiting e Security Headers.
- **Integração:** Conexão robusta via ODBC Driver com suporte a PyODBC.

## 🛠️ Tecnologias

- **FastAPI:** Framework web moderno.
- **SQLAlchemy 2.0:** ORM utilizando o novo padrão de consultas `select()`.
- **PyODBC:** Driver de conexão com o Microsoft SQL Server.
- **Structlog:** Logs estruturados para monitoramento.

## 📂 Estrutura do Pacote

```
api-sqlserver/
├── app/
│   ├── core/         # Configurações dinâmicas de conexão
│   ├── models/       # Modelos refletidos ou mapeados do SQL Server
│   ├── repositories/ # Camada de acesso a dados (Somente Leitura)
│   ├── routers/      # Endpoints de consulta
│   └── services/     # Lógica de integração
├── tests/            # Testes de integração e conexão
└── test_connection.py # Script utilitário para validar driver/rede
```

## ⚙️ Configuração Local

1.  **Ambiente Virtual:**
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  **Drivers:**
    Certifique-se de ter o `Microsoft ODBC Driver 17 for SQL Server` instalado no sistema.

3.  **Variáveis de Ambiente:**
    Ajuste as variáveis `DB_SERVER`, `DB_DATABASE`, `DB_USERNAME` e `DB_PASSWORD` no `.env`.

4.  **Execução:**
    ```powershell
    uvicorn app.main:app --reload --port 8001
    ```

## 📝 Notas de Versão (Revisão Recente)

- **SQLAlchemy 2.0 Style:** Repositórios atualizados para usar `select()` e `scalars()`.
- **Filtros Dinâmicos:** Refatoração da lógica de filtragem para ser mais limpa e eficiente.
- **Configuração de Conexão:** Melhoria na montagem da `DATABASE_URL` para suportar caracteres especiais em senhas.
