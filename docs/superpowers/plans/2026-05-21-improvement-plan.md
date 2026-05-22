# Plano de Melhorias — GrindX
> Gerado em: 2026-05-21 | Baseado na revisão técnica do monorepo

---

## Visão Geral

Este plano organiza as melhorias em **4 etapas progressivas**, da mais urgente à mais estratégica.
Cada etapa é independente e pode ser entregue sem bloquear a próxima.

| Etapa | Foco | Esforço Estimado |
|-------|------|-----------------|
| 1 | Correções críticas & acesso pela rede | ~2–4 horas |
| 2 | Robustez & segurança | ~1–2 dias |
| 3 | Observabilidade & qualidade | ~2–3 dias |
| 4 | Escalabilidade & produção | ~1 semana |

---

## Etapa 1 — Correções Críticas & Acesso pela Rede Local

> **Prioridade máxima.** Impacto imediato, baixo risco de regressão.

### 1.1 — Acesso ao Sistema por Outro Computador na Rede

**Problema:** Atualmente todos os serviços escutam apenas em `127.0.0.1` (localhost),
tornando impossível acessar o sistema de outro dispositivo na mesma rede Wi-Fi/LAN.

**Solução: 3 mudanças simples.**

#### A) Expor as APIs na rede (Makefile)

```makefile
# ANTES
dev-postgres:
    cd packages/api-postgres && ... uvicorn app.main:app --reload --port 8002

# DEPOIS — adicionar --host 0.0.0.0
dev-postgres:
    cd packages/api-postgres && ... uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

dev-sqlserver:
    cd packages/api-sqlserver && ... uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

#### B) Expor o frontend na rede

```makefile
# ANTES
# (comando manual) python -m http.server 5500 --directory packages/frontend-webapp

# DEPOIS — adicionar target no Makefile com bind 0.0.0.0
dev-frontend:
    @echo "Iniciando Frontend na porta 5500 (acessivel na rede)..."
    python -m http.server 5500 --directory packages/frontend-webapp --bind 0.0.0.0
```

#### C) Atualizar o CORS para aceitar o IP da máquina host

No arquivo `packages/api-postgres/.env` e `packages/api-sqlserver/.env`,
adicionar o IP local da máquina que roda o servidor (ex: `192.168.1.100`):

```env
# .env (api-postgres e api-sqlserver)
CORS_ORIGINS=["http://localhost:5500","http://127.0.0.1:5500","http://192.168.1.100:5500"]
```

> **Como descobrir o IP:** no Windows, abrir o PowerShell e rodar `ipconfig`.
> Procurar por "Endereço IPv4" na sua interface de rede (Wi-Fi ou Ethernet).
> O IP muda se o roteador reiniciar — considere IP fixo na rede ou usar `*` em dev.

#### D) Corrigir o `main.py` para realmente usar o CORS do .env

```python
# ANTES — origens hardcoded, ignora o .env
allow_origins=[
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    ...
]

# DEPOIS — usa settings.allowed_origins_list que lê do .env
allow_origins=settings.allowed_origins_list,
```

#### E) Abrir as portas no Firewall do Windows

Rodar no **PowerShell como Administrador**:

```powershell
# Liberar porta do frontend
New-NetFirewallRule -DisplayName "GrindX Frontend" -Direction Inbound -Protocol TCP -LocalPort 5500 -Action Allow

# Liberar porta da API Postgres
New-NetFirewallRule -DisplayName "GrindX API Postgres" -Direction Inbound -Protocol TCP -LocalPort 8002 -Action Allow

# Liberar porta da API SQL Server (se necessário)
New-NetFirewallRule -DisplayName "GrindX API SQLServer" -Direction Inbound -Protocol TCP -LocalPort 8001 -Action Allow
```

#### F) Atualizar a URL da API no frontend

O `apiService.js` (ou equivalente) provavelmente tem a URL base da API hardcoded
como `localhost`. Ela precisa apontar para o IP do servidor quando acessada de outro computador.

**Solução recomendada — URL relativa ao host:**

```javascript
// Em shared/apiService.js — detectar automaticamente o host atual
const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8002'
  : `http://${window.location.hostname}:8002`;
```

Assim, quando outro computador abre `http://192.168.1.100:5500`, o frontend
automaticamente aponta para `http://192.168.1.100:8002` — sem configuração extra.

---

### 1.2 — Corrigir Validação de SECRET_KEY

**Problema:** Uma chave fraca como `"secret"` passa sem nenhum aviso.

```python
# packages/api-postgres/app/core/config.py e api-sqlserver equivalente
from pydantic import field_validator

class Settings(BaseSettings):
    SECRET_KEY: str

    @field_validator("SECRET_KEY")
    @classmethod
    def validar_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError(
                "SECRET_KEY deve ter pelo menos 32 caracteres. "
                "Gere uma com: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        return v
```

---

### 1.3 — Guard no seed.py

**Problema:** `seed.py` pode ser rodado acidentalmente em produção.

```python
# packages/api-postgres/seed.py — adicionar no topo
from app.core.config import settings

if not settings.DEBUG:
    print("ERRO: seed.py só pode rodar com DEBUG=true. Abortando.")
    raise SystemExit(1)
```

---

## Etapa 2 — Robustez & Segurança

> Melhorias que aumentam a confiabilidade e fecham brechas antes de um deploy real.

### 2.1 — Eliminar Injeção Dupla de `get_current_user`

Nos routers de produto (e possivelmente usuário), o token JWT é decodificado duas vezes
por requisição — uma via `require_role` e outra via parâmetro explícito.

```python
# ANTES — duplicado
@router.get(
    "/produtos",
    dependencies=[Depends(require_role(Role.ADMIN, Role.OPERADOR, Role.LEITURA))],
)
def listar_produtos(
    ...
    current_user: TokenPayload = Depends(get_current_user),  # segunda vez desnecessária
):

# DEPOIS — remover o parâmetro current_user se não for usado no corpo
# OU: remover o dependencies=[...] e deixar só o parâmetro com verificação inline
@router.get("/produtos")
def listar_produtos(
    ...
    current_user: TokenPayload = Depends(require_role(Role.ADMIN, Role.OPERADOR, Role.LEITURA)),
):
```

### 2.2 — Rate Limiter Thread-Safe

O `RateLimitMiddleware` usa `defaultdict` sem lock — inseguro com múltiplos workers assíncronos.

```python
# Adicionar asyncio.Lock por IP (solução leve, sem Redis)
import asyncio
from collections import defaultdict

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, ...):
        ...
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def dispatch(self, request, call_next):
        ...
        async with self._lock:
            self._clean_old_requests(client_ip, now)
            if len(self._requests[client_ip]) >= self.max_requests:
                ...  # retornar 429
            self._requests[client_ip].append(now)
```

> Para produção com múltiplos workers, substituir por `fastapi-limiter` com Redis.

### 2.3 — Adicionar Content-Security-Policy

O `SecurityHeadersMiddleware` não tem CSP, o que deixa o frontend exposto a XSS via inline scripts.

```python
response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline'; "  # remover unsafe-inline após migrar scripts inline
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: blob:; "
    "connect-src 'self' http://localhost:8002 http://localhost:8001;"
)
```

### 2.4 — Separar `.env` de dev e produção

Criar `.env.dev` e `.env.prod` explícitos, com `.env.prod` nunca versionado:

```
packages/api-postgres/
├── .env.example     # template público (já existe)
├── .env.dev         # valores locais de desenvolvimento
└── .env.prod        # NUNCA commitar — produção real
```

Adicionar ao `.gitignore`:
```
.env.prod
*.prod.env
```

---

## Etapa 3 — Observabilidade & Qualidade

> Melhorias que facilitam debugging, monitoramento e manutenção contínua.

### 3.1 — Health Check Mais Rico

O `/health` atual provavelmente só retorna `{"status": "ok"}`.
Adicionar verificação real do banco:

```python
@router.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "version": settings.APP_VERSION,
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat(),
    }
```

### 3.2 — Logs de Auditoria em Ações Críticas

Registrar quem fez o quê em operações sensíveis (criar/desativar usuário, login, etc.):

```python
# Em AuthService.autenticar()
logger.info(
    "login_attempt",
    username=username,
    success=True,
    ip=request.client.host,  # passar request como parâmetro
    timestamp=datetime.utcnow().isoformat(),
)
```

### 3.3 — Testes de Contrato entre APIs

Adicionar testes que verificam que a `api-sqlserver` consegue validar tokens
emitidos pela `api-postgres` — garantindo que `SECRET_KEY` está sincronizada entre elas:

```python
# tests/test_cross_api_jwt.py
def test_token_da_postgres_e_valido_na_sqlserver():
    token = emitir_token_postgres()
    response = client_sqlserver.get("/v1/cliente", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200  # não 401
```

### 3.4 — Makefile: Target `dev-all`

Facilitar subir tudo de uma vez com um único comando:

```makefile
dev-all:
    @echo "Subindo todos os servicos GrindX..."
    start "API Postgres"  cmd /k "cd packages/api-postgres && set PYTHONPATH=..&& .venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002"
    start "API SQLServer" cmd /k "cd packages/api-sqlserver && set PYTHONPATH=..&& .venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001"
    start "Frontend"      cmd /k "python -m http.server 5500 --directory packages/frontend-webapp --bind 0.0.0.0"
    @echo Acesse: http://localhost:5500
```

---

## Etapa 4 — Escalabilidade & Produção

> Para quando o sistema precisar rodar em produção de verdade.

### 4.1 — Rate Limiter Distribuído com Redis

Substituir o `RateLimitMiddleware` em memória por `fastapi-limiter`:

```python
# requirements.txt
fastapi-limiter>=0.1.6
redis[asyncio]>=5.0.0

# main.py (lifespan)
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter

async with lifespan(app):
    r = redis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)
    yield
    await FastAPILimiter.close()
```

### 4.2 — Nginx como Reverse Proxy

Em vez de expor as APIs diretamente, colocar Nginx na frente:

```nginx
# nginx.conf
server {
    listen 80;
    server_name 192.168.1.100;  # IP da máquina na rede

    location / {
        root /path/to/frontend-webapp;
        index index.html;
    }

    location /v1/ {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /sqlserver/ {
        proxy_pass http://127.0.0.1:8001;
    }
}
```

Benefícios: uma porta só (80/443), SSL centralizado, load balancing futuro.

### 4.3 — Containers com IP Fixo na Rede

No `podman-compose.yml`, configurar o container para ser acessível na rede local
via macvlan ou publicando a porta no host com bind explícito:

```yaml
ports:
  - "0.0.0.0:8002:8002"  # explícito — garante bind em todas as interfaces
  - "0.0.0.0:8001:8001"
```

### 4.4 — Variáveis de Ambiente para IP Dinâmico no Frontend

Em vez de hardcodar o IP no `apiService.js`, ler de uma configuração injetada no build:

```javascript
// shared/config.js (gerado no deploy)
window.GRINDX_CONFIG = {
  API_BASE_URL: "http://192.168.1.100:8002",  // injetado no deploy
};

// shared/apiService.js
const API_BASE = window.GRINDX_CONFIG?.API_BASE_URL ?? `http://${window.location.hostname}:8002`;
```

---

## Workflow por Etapa — Ruff + Conventional Commits

> **Regra geral:** antes de commitar qualquer etapa, rodar o ruff para garantir que
> o código está limpo. Cada etapa gera **um commit atômico** com mensagem padronizada.

### Passo a Passo (repetir em cada etapa)

```powershell
# 1. Verificar erros e problemas de estilo
cd D:\_Projects\GrindX
ruff check packages/

# 2. Ver e corrigir automaticamente o que for possível
ruff check packages/ --fix

# 3. Verificar formatação
ruff format --check packages/

# 4. Aplicar formatação automática
ruff format packages/

# 5. Rodar o ruff uma última vez para confirmar que está limpo
ruff check packages/
# Saída esperada: "All checks passed!"

# 6. Commitar a etapa
git add .
git commit -m "<tipo>(<escopo>): <descrição>"
```

> O `ruff check` e o `ruff format` são operações diferentes — sempre rodar os dois.

---

### Referência de Conventional Commits

```
<tipo>(<escopo opcional>): <descrição curta no imperativo>

[corpo opcional — o quê e por quê, não como]

[rodapé opcional — breaking changes, issues fechadas]
```

**Tipos permitidos:**

| Tipo | Quando usar |
|------|-------------|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug ou comportamento errado |
| `refactor` | Mudança de código sem alterar comportamento externo |
| `chore` | Configuração, tooling, Makefile, .gitignore |
| `docs` | Apenas documentação |
| `test` | Adição ou correção de testes |
| `perf` | Melhoria de performance |
| `ci` | Mudanças em workflows do CI/CD |

**Escopos sugeridos para o GrindX:**

| Escopo | O que cobre |
|--------|-------------|
| `api-postgres` | Pacote da API principal |
| `api-sqlserver` | Pacote da API SQL Server |
| `frontend` | Frontend webapp |
| `shared` | Pacote compartilhado |
| `makefile` | Targets do Makefile |
| `infra` | Containers, compose, nginx |
| `config` | Variáveis de ambiente, settings |
| `auth` | Autenticação e tokens |
| `middleware` | Rate limit, headers, request ID |

---

### Commits por Etapa

#### Etapa 1 — Correções Críticas & Acesso pela Rede

```bash
# Após 1.1 (acesso pela rede)
git commit -m "feat(makefile): expor servicos na rede com --host 0.0.0.0

Adiciona --host 0.0.0.0 nos targets dev-postgres e dev-sqlserver.
Adiciona target dev-frontend com --bind 0.0.0.0.
Permite acesso ao sistema por outros dispositivos na rede local."

# Após corrigir o CORS no main.py (1.1-D)
git commit -m "fix(api-postgres): usar CORS_ORIGINS do .env em vez de lista hardcoded

allow_origins passava a usar settings.allowed_origins_list.
Configuracao de origens agora respeitada via variavel de ambiente."

# Após corrigir o apiService.js (1.1-F)
git commit -m "fix(frontend): detectar host dinamicamente no apiService

URL base da API agora usa window.location.hostname.
Elimina necessidade de ajuste manual ao acessar de outra maquina."

# Após 1.2 (validação SECRET_KEY)
git commit -m "fix(config): validar comprimento minimo da SECRET_KEY

Adiciona field_validator que rejeita chaves com menos de 32 caracteres.
Previne uso acidental de chaves fracas em qualquer ambiente."

# Após 1.3 (guard no seed.py)
git commit -m "fix(api-postgres): adicionar guard de ambiente no seed.py

seed.py agora aborta se DEBUG=false, prevenindo execucao acidental
em producao."
```

#### Etapa 2 — Robustez & Segurança

```bash
# Após 2.1
git commit -m "refactor(api-postgres): eliminar injecao dupla de get_current_user

Token JWT era decodificado duas vezes por requisicao nos routers
de produto. Centralizado em require_role via Depends."

# Após 2.2
git commit -m "fix(middleware): tornar RateLimitMiddleware thread-safe com asyncio.Lock

defaultdict compartilhado entre corrotinas sem sincronizacao.
Lock garante consistencia dos contadores por IP."

# Após 2.3
git commit -m "feat(middleware): adicionar Content-Security-Policy no SecurityHeadersMiddleware

CSP reduz superficie de ataque XSS no frontend.
Configurado com unsafe-inline temporario — remover apos migrar scripts."

# Após 2.4
git commit -m "chore(config): separar .env de dev e producao

Cria .env.dev para desenvolvimento local.
Adiciona .env.prod ao .gitignore — nunca versionado."
```

#### Etapa 3 — Observabilidade & Qualidade

```bash
# Após 3.1
git commit -m "feat(api-postgres): enriquecer health check com verificacao do banco

/health agora executa SELECT 1 e retorna status do banco,
versao e timestamp. Retorna 'degraded' se banco inacessivel."

# Após 3.2
git commit -m "feat(auth): adicionar logs de auditoria em acoes criticas

Login, registro e desativacao de usuario agora registram
usuario, IP e timestamp via structlog."

# Após 3.3
git commit -m "test: adicionar testes de contrato entre api-postgres e api-sqlserver

Garante que tokens emitidos pela api-postgres sao validos
na api-sqlserver — valida sincronizacao da SECRET_KEY."

# Após 3.4
git commit -m "chore(makefile): adicionar target dev-all para subir todos os servicos

Abre terminais separados para cada servico com um unico comando.
Inclui frontend na porta 5500 acessivel na rede."
```

#### Etapa 4 — Escalabilidade & Produção

```bash
# Após 4.1
git commit -m "feat(middleware): substituir rate limiter em memoria por fastapi-limiter com Redis

Rate limiting agora e distribuido e funciona corretamente
com multiplos workers Uvicorn."

# Após 4.2
git commit -m "feat(infra): adicionar configuracao Nginx como reverse proxy

Centraliza acesso na porta 80, oculta portas internas das APIs
e prepara infraestrutura para SSL futuro."

# Após 4.3
git commit -m "fix(infra): bind explicito 0.0.0.0 nos containers do podman-compose

Garante que os containers publicam as portas em todas as interfaces
do host, necessario para acesso na rede local."

# Após 4.4
git commit -m "feat(frontend): injetar URL da API via GRINDX_CONFIG no deploy

Elimina hardcode de IP no apiService.js.
Config e gerada no deploy e lida em runtime pelo frontend."
```

---

## Checklist Resumido

### Etapa 1 — Fazer Agora
- [ ] Adicionar `--host 0.0.0.0` nos comandos Uvicorn do Makefile
- [ ] Adicionar target `dev-frontend` com `--bind 0.0.0.0` no Makefile
- [ ] Atualizar `CORS_ORIGINS` no `.env` com o IP da máquina
- [ ] Corrigir `main.py` para usar `settings.allowed_origins_list` no CORS
- [ ] Abrir portas 5500, 8001, 8002 no Firewall do Windows
- [ ] Corrigir `apiService.js` para URL dinâmica baseada no `window.location.hostname`
- [ ] Adicionar `@field_validator` para `SECRET_KEY` mínima de 32 chars
- [ ] Adicionar guard de `DEBUG` no `seed.py`
- [ ] `ruff check packages/ --fix && ruff format packages/`
- [ ] `ruff check packages/` — confirmar "All checks passed!"
- [ ] Commitar cada mudança com conventional commit (ver seção acima)

### Etapa 2 — Esta Semana
- [ ] Eliminar injeção dupla de `get_current_user` nos routers
- [ ] Adicionar `asyncio.Lock` no `RateLimitMiddleware`
- [ ] Adicionar header `Content-Security-Policy`
- [ ] Criar `.env.dev` / `.env.prod` e atualizar `.gitignore`
- [ ] `ruff check packages/ --fix && ruff format packages/`
- [ ] `ruff check packages/` — confirmar "All checks passed!"
- [ ] Commitar cada mudança com conventional commit (ver seção acima)

### Etapa 3 — Próximas 2 Semanas
- [ ] Health check com verificação real do banco
- [ ] Logs de auditoria em ações críticas
- [ ] Testes de contrato entre as duas APIs
- [ ] Target `dev-all` no Makefile
- [ ] `ruff check packages/ --fix && ruff format packages/`
- [ ] `ruff check packages/` — confirmar "All checks passed!"
- [ ] Commitar cada mudança com conventional commit (ver seção acima)

### Etapa 4 — Antes de Produção
- [ ] Rate limiter com Redis
- [ ] Nginx como reverse proxy
- [ ] Containers com bind explícito `0.0.0.0`
- [ ] `GRINDX_CONFIG` injetado no deploy do frontend
- [ ] `ruff check packages/ --fix && ruff format packages/`
- [ ] `ruff check packages/` — confirmar "All checks passed!"
- [ ] Commitar cada mudança com conventional commit (ver seção acima)

---

## Como Testar o Acesso pela Rede

Após aplicar a Etapa 1:

1. **No computador servidor:** descobrir o IP com `ipconfig` (ex: `192.168.1.100`)
2. **Subir os serviços:** `make dev-postgres`, `make dev-sqlserver`, `make dev-frontend`
3. **No outro computador da rede:** abrir o navegador em `http://192.168.1.100:5500`
4. **Testar a API diretamente:** `http://192.168.1.100:8002/health`

Se não conectar, verificar:
- Firewall do Windows bloqueando (checar Etapa 1-E)
- Ambos os computadores na mesma rede Wi-Fi/LAN
- IP do servidor não mudou (se mudou, atualizar o `.env` e reiniciar)

---

*Plano gerado automaticamente a partir da revisão técnica do GrindX — maio de 2026.*
