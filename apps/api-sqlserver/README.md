<!-- title: API SQL Server — GrindX | updated: 2026-05-20 -->

# GrindX — API SQL Server (Consulta)

API de leitura para integração com banco de dados SQL Server legado (WAN). Por design, não permite operações de escrita — serve apenas para consulta de dados de clientes e faturamento.

---

## Funcionalidades

- **Consulta de Clientes:** Listagem paginada e busca por ID/CNPJ
- **Filtros Avançados:** Filtros por razão social, cidade e UF
- **Segurança:**
  - Validação de tokens JWT emitidos pela `api-postgres`
  - Controle de acesso (Read-only)
  - Middlewares de Rate Limiting e Security Headers
- **Integração:** Conexão via ODBC Driver com suporte a PyODBC

---

## Tecnologias

| Tecnologia | Uso |
|------------|-----|
| FastAPI | Framework web |
| SQLAlchemy 2.0 | ORM com padrão `select()` |
| PyODBC | Driver de conexão com SQL Server |
| Structlog | Logs estruturados |

---

## Estrutura do Pacote

```
api-sqlserver/
├── app/
│   ├── auth/         # Validação JWT (sem emissão)
│   ├── core/         # Configurações dinâmicas de conexão
│   ├── middleware/   # Rate limit, request ID, security headers
│   ├── models/       # Modelos do SQL Server
│   ├── repositories/ # Camada de acesso a dados (Somente Leitura)
│   ├── routers/      # Endpoints de consulta
│   └── services/     # Lógica de integração
├── tests/            # Testes de integração e conexão
└── test_connection.py # Script utilitário para validar driver/rede
```

---

## Configuração Local

### 1. Ambiente Virtual

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Drivers

**Container:** já vem com `unixodbc` + `msodbcsql18` no `Containerfile`.

**Host Linux (sem container) — escolha UMA opção:**

**A) pyodbc + ODBC Driver (requer lib de sistema):**
```bash
# Se apt update falha com `microsoft-prod.gpg: No such file`, remova primeiro:
sudo rm -f /etc/apt/sources.list.d/mssql-release.list /usr/share/keyrings/microsoft-prod.gpg && sudo apt update

sudo apt install -y curl gnupg2 ca-certificates
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg
sudo chmod 644 /usr/share/keyrings/microsoft-prod.gpg
echo "deb [arch=amd64,arm64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt update
sudo ACCEPT_EULA=Y apt install -y unixodbc unixodbc-dev msodbcsql17  # ou msodbcsql18 se usar Driver 18

odbcinst -q -d -v  # deve listar o driver instalado
```
`.env` deve alinhar com o pacote: `DB_DRIVER=ODBC Driver 17 for SQL Server` (para `msodbcsql17`) ou `ODBC Driver 18 for SQL Server` (para `msodbcsql18`). Erro `Can't open lib 'ODBC Driver 17'` = mismatch.

Remover: `sudo apt remove -y msodbcsql18 && sudo apt autoremove -y`.

**B) pymssql (sem ODBC, sem repo Microsoft):**
```env
DB_DRIVER=pymssql
```
`app/core/config.py:125` usa `mssql+pymssql://` quando `DB_DRIVER` não contém `ODBC` — não precisa de `unixODBC`.

### 3. Variáveis de Ambiente

Ajuste as variáveis `DB_SERVER`, `DB_DATABASE`, `DB_USERNAME` e `DB_PASSWORD` no `.env`.

A `SECRET_KEY` deve ser **idêntica** à da `api-postgres` para validação cruzada de tokens JWT.

### 4. Execução

```powershell
uvicorn app.main:app --reload --port 8001
```

---

## Notas de Versão

- **SQLAlchemy 2.0 Style:** Repositórios atualizados para usar `select()` e `scalars()`
- **Filtros Dinâmicos:** Refatoração da lógica de filtragem para ser mais limpa e eficiente
- **Configuração de Conexão:** Melhoria na montagem da `DATABASE_URL` para suportar caracteres especiais em senhas
