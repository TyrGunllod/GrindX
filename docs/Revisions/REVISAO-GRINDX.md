# Revisão Técnica — GrindX v1.18.0

**Data:** 09/06/2026  
**Versão analisada:** CHANGELOG v1.18.0 (código extraído do ZIP)  
**Cobertura:** 333 arquivos, 28 arquivos de teste, histórico de 18 releases

---

## Resumo executivo

O projeto está significativamente mais maduro do que os docs em contexto descrevem. O que antes era um MVP 97% completo evoluiu para um sistema com segurança hardened, cache, health checks profundos, sistema de temas/skins, módulo de importação dinâmica e arquitetura multi-schema no PostgreSQL. O CHANGELOG registra 18 versões entre 21/05 e 09/06/2026 — desenvolvimento intenso e bem documentado.

**3 bugs concretos encontrados. Documentação criticamente defasada. 4 itens v2 bem delimitados.**

---

## 1. Bugs concretos

### 🔴 B-01 — `slowapi` duplicado no requirements.txt

```
# requirements.txt — api-postgres
linha 21: slowapi>=0.1.9
linha 31: slowapi>=0.1.9   ← duplicata
```

`pip install` aceita silenciosamente, mas polui o arquivo e pode causar confusão em auditorias de dependências.

**Correção:** remover a linha 31.

---

### 🔴 B-02 — APP_VERSION desatualizado no `config.py`

O `config.py` de ambas as APIs registra:

```python
APP_VERSION = "1.15.0"
```

O CHANGELOG e o `release.yml` estão na v1.18.0. O `semantic-release` usa essa constante como `version_variable`, então as 3 últimas releases foram publicadas com a versão errada no cabeçalho das respostas da API e no health check.

**Causa provável:** o semantic-release não executou com sucesso após a v1.15.0 (pode ser falta do token `GH_TOKEN` na esteira, ou as releases foram feitas manualmente via `git tag`).

**Verificar:** `git log --oneline --tags` para confirmar se as tags v1.16.0–v1.18.0 existem no repositório.

---

### 🟡 B-03 — Contradição entre CONCERNS.md e STATE.md sobre SEC-07

`CONCERNS.md` marca:
> ✓ RESOLVED: Path traversal protection added in Phase 4

`STATE.md` lista:
> Security — Path traversal protection (SEC-07) — Deferred to v2

O código está correto: `theme_router.py` implementa `os.path.realpath()` para templates e os uploads de logo/fonte usam `uuid.uuid4()` como filename (imune a traversal por natureza). O conflito é apenas documental, mas gera confusão em auditorias futuras.

**Correção:** remover SEC-07 da tabela "Deferred Items" no STATE.md, ou adicionar uma nota explicando o escopo parcial.

---

## 2. Documentação criticamente defasada

Os arquivos de docs em contexto (API.md, SETUP.md, MAPA-ARQUIVOS.md) descrevem o estado do projeto em ~maio/2026 e estão desalinhados com o código atual em vários pontos estruturais.

### Estrutura de diretórios

| Docs dizem | Código real |
|-----------|------------|
| `packages/api-postgres/` | `apps/api-postgres/` |
| `packages/api-sqlserver/` | `apps/api-sqlserver/` |
| `packages/frontend-webapp/` | `apps/frontend-webapp/` |

A migração `packages/ → apps/` foi feita na v1.16.0 e todos os Makefiles, pyproject.toml e CI já refletem isso, mas os docs de instalação (SETUP.md) ainda referenciam os caminhos antigos.

### Routers / Endpoints

| Docs API.md | Código real |
|------------|-------------|
| `GET /v1/produtos/` | **removido** na v1.16.0 |
| `POST /v1/produtos/` | **removido** |
| `PUT/DELETE /v1/produtos/{id}` | **removido** |
| — | `GET/POST /v1/themes/` ← novo |
| — | `POST /v1/import/scan` ← novo |
| — | `POST /v1/import/{slug}` ← novo |

### Módulos frontend

| MAPA-ARQUIVOS.md | Real |
|------------------|------|
| `home`, `users`, `structure` | `home`, `users`, `structure`, **`admin-skins`**, **`importer`** |
| sem assets | `assets/favicon.ico`, `assets/favicon.svg`, `assets/favicon.png` |
| sem fontes | `shared/fonts/` — DM Sans + Barlow Condensed bundled |
| sem skins | `skins/grindx-default.json`, `skins/royal-purple.json` |

### Modelos de banco

| Docs DATABASE.md | Real |
|-----------------|------|
| `Usuario`, `Produto`, `Aba`, `Modulo` | `Usuario`, **`Empresa`**, **`CompanyTheme`**, **`ThemeHistory`**, `Aba`, `Modulo` |
| schema único | **multi-schema**: `iam`, `org`, `portal` (4 schemas + `public`) |

### Migrações

8 arquivos de migração existem, sendo 2 com nomenclatura fora do padrão sequencial:

```
001_initial_schema.py          ← padrão ✓
002_add_usuario_modulos.py     ← padrão ✓
003_add_empresa_and_theme.py   ← padrão ✓
004_add_theme_history.py       ← padrão ✓
005_add_aba_parent_id.py       ← padrão ✓
006_add_performance_indexes.py ← padrão ✓ (head)
02_add_org_schema_tables.py    ← ⚠ nomenclatura inconsistente
2026_06_02_add_temp_password_fields.py ← ⚠ nomenclatura inconsistente
```

O Alembic aceita todos desde que a cadeia de `down_revision` esteja correta, mas a inconsistência dificulta navegação. Vale renomear para `007_add_org_schema_tables.py` e `008_add_temp_password_fields.py` em uma próxima oportunidade (não é urgente).

---

## 3. Análise de segurança

### O que está bem implementado

**Validação de entropia da SECRET_KEY** — Shannon entropy com threshold 3.5 bits/char é uma abordagem incomum e correta. Rejeita chaves como "12345678901234567890123456789012" que passariam por simples validação de comprimento.

**Rate limiting dual-key (SlowAPI)** — separar rate limit por `user_id` quando autenticado evita que um único IP compartilhado (NAT corporativo, VPN) afete múltiplos usuários. Implementação limpa com `limits.storage.MemoryStorage`.

**Senhas temporárias com expiração** — uso de `secrets.token_urlsafe()` (CSPRNG) com campo `expires_at` no banco e lógica fail-closed (sem `expires_at` → rejeita). Correto.

**Magic bytes em uploads** — `filetype` library para validar tipo real do arquivo, não apenas extensão. Evita upload de executáveis renomeados como `.jpg`.

**CORS strict em produção** — o `allowed_origins_list` property lança `ValueError` se `CORS_ORIGINS` for `*` em ambiente de produção. Isso previne deploy acidental com CORS aberto.

**Path traversal em templates** — `os.path.realpath()` garante que o caminho resolvido está dentro do diretório esperado antes de abrir o arquivo. Correto.

### Limitações conhecidas e aceitas (v2)

| Item | Impacto | Mitigação atual |
|------|---------|----------------|
| JWT sem blacklist/revogação | Token válido até expirar mesmo após logout | TTL curto (30 min) limita janela de exposição |
| SQLAlchemy síncrono | Throughput limitado sob carga | Pool de conexões padrão do SQLAlchemy cobre maioria dos casos |
| Cache in-memory sem Redis | Não compartilhado entre workers | Aceitável para single-worker; documentado |
| Frontend sem bundle/minificação | Maior payload inicial | Vanilla JS é leve; sem framework pesado |

### Ponto de atenção: `config.js` hardcoded

```javascript
// apps/frontend-webapp/shared/config.js
window.GRINDX_CONFIG = {
  API_BASE_URL: "http://localhost:8002/v1",
};
```

Esse arquivo precisa ser editado manualmente por ambiente. O `release.yml` não faz substituição automática. Em deploy, é fácil esquecer. Considerar injeção via Nginx (`sub_filter`) ou variável de build.

---

## 4. Qualidade de código

### Pontos positivos

- Docstrings em PT-BR com formato Google-style são consistentes nos arquivos principais
- Type hints em todas as assinaturas de função
- Separação clara de responsabilidades: router → service → repository
- Cache thread-safe com locks explícitos (`threading.Lock`) — evita race condition no TTLCache
- Health check distingue `healthy` / `degraded` / `disconnected` e retorna 503 adequado quando degradado
- `shared/` como pacote instalável via `pip install -e packages/shared` (pyproject.toml presente)
- Semantic versioning automatizado com CHANGELOG gerado

### Pontos a melhorar

**Dependências de dev misturadas com prod no requirements.txt:**

```
# requirements.txt mistura tudo:
pytest>=8.0.0
pytest-asyncio>=0.23.5
httpx>=0.27.0
pytest-cov>=6.0.0
ruff>=0.3.0
```

Isso vai para a imagem de container em produção. Criar `requirements-dev.txt` separado e usar `pip install -r requirements.txt` no Containerfile sem as deps de teste.

**`import_router.py` executa subprocessos:**

O endpoint de importação de módulos usa `subprocess.run()` para executar scripts Python. Isso é poderoso mas requer atenção: garantir que apenas admins possam acionar (já implementado com `require_role`), e que o `IMPORT_DIR` seja configurado para um diretório controlado, não arbitrário.

**Dois CI diferentes (GitHub Actions + Jenkinsfile) sem paridade:**

O `release.yml` roda com `--cov-fail-under=70`. O `Jenkinsfile` não inclui coverage threshold. Em pipelines paralelos isso significa que o Jenkins pode passar em builds que o GitHub Actions rejeitaria.

---

## 5. Itens pendentes prioritários

| # | Item | Prioridade | Arquivo |
|---|------|-----------|---------|
| 1 | Remover `slowapi` duplicado | Alta | `apps/api-postgres/requirements.txt` |
| 2 | Corrigir `APP_VERSION = "1.15.0"` → `"1.18.0"` | Alta | `apps/api-postgres/app/core/config.py` e `api-sqlserver` |
| 3 | Atualizar MAPA-ARQUIVOS.md / SETUP.md / API.md | Alta | `docs/` |
| 4 | Separar requirements dev/prod | Média | `apps/api-postgres/requirements.txt` |
| 5 | Adicionar coverage ao Jenkinsfile | Média | `Jenkinsfile` |
| 6 | Atualizar config.js para injeção por ambiente | Média | `apps/frontend-webapp/shared/config.js` |
| 7 | Renomear migrações inconsistentes | Baixa | `alembic/versions/` |
| 8 | Corrigir contradição SEC-07 no STATE.md | Baixa | `.planning/STATE.md` |

---

## 6. O que está pronto e funcionando bem

- Autenticação JWT com par access/refresh + recuperação de senha com expiração
- RBAC com matriz admin/operador
- Sistema de temas/skins por empresa com upload de logo e fontes
- Menu dinâmico hierárquico (abas aninhadas com `parent_id`)
- Importação de módulos dinâmicos via ZIP com validação de manifest
- Health check profundo com verificação de schema PostgreSQL
- Cache in-memory com TTL para temas, usuários e portal
- 5 índices B-tree via migração Alembic
- Middlewares: rate limit dual-key, request ID, security headers, CORS
- Suite de testes com SQLite in-memory (sem dependência de banco real no CI)
- Cobertura mínima de 70% enforced no GitHub Actions
- Semantic release com CHANGELOG automático
- Fonts e assets visuais bundled localmente (sem CDN externo)
- Containerização com Podman + Nginx configurado

---

*Revisão baseada na análise de 333 arquivos do ZIP GrindX.zip (commit de 09/06/2026).*
