# Especificação Técnica — Resolução de Pendências REVISAO-GRINDX

**Data:** 09/06/2026
**Versão alvo:** v1.18.0 → v1.19.0
**Base:** REVISAO-GRINDX.md (docs/Revisions/)
**Cobertura:** 9 itens prioritários (3 bugs, 3 docs, 5 melhorias)

---

## 1. Introdução

A revisão técnica da v1.18.0 identificou 9 pendências classificadas por prioridade. Este spec detalha cada item com a abordagem de correção, arquivos envolvidos, critérios de aceitação e riscos.

A execução segue ordem de prioridade: bugs primeiro (impacto funcional), depois documentação (alinhamento equipe), por fim melhorias (qualidade de longo prazo).

---

## 2. Bugs

### 2.1 B-01 — slowapi duplicado no requirements.txt

**Descrição:** A dependência `slowapi>=0.1.9` aparece duas vezes no `apps/api-postgres/requirements.txt` (linhas 21 e 31). Não causa falha funcional, mas polui o arquivo e gera ruído em auditorias.

**Arquivo:** `apps/api-postgres/requirements.txt`

**Correção:** Remover a linha 31 (segunda ocorrência).

**Critério de aceitação:** `rg "slowapi" apps/api-postgres/requirements.txt` retorna exatamente 1 linha.

---

### 2.2 B-02 — APP_VERSION desatualizado no config.py

**Descrição:** Ambas as APIs declaram `APP_VERSION = "1.15.0"` nos respectivos `config.py`. O CHANGELOG registra v1.18.0. O semantic-release usa esta constante como `version_variable`, então toda resposta da API e health check retornam versão errada.

**Arquivos:**
- `apps/api-postgres/app/core/config.py`
- `apps/api-sqlserver/app/core/config.py`

**Correção:** Atualizar `APP_VERSION` de `"1.15.0"` para `"1.18.0"` em ambos os arquivos.

**Pós-correção:** Verificar se `git tag` lista `v1.16.0`, `v1.17.0`, `v1.18.0`. Se não existirem, recriar tags apontando para commits correspondentes no CHANGELOG.

**Critério de aceitação:** Health check de ambas as APIs retorna `"version": "1.18.0"`.

---

### 2.3 B-03 — Contradição SEC-07 entre CONCERNS.md e STATE.md

**Descrição:** `CONCERNS.md` marca SEC-07 como resolvido (path traversal protection implementado na Phase 4). `STATE.md` lista SEC-07 como "Deferred to v2". O código está correto (proteção implementada). Apenas conflito documental.

**Arquivos:**
- `.planning/CONCERNS.md`
- `.planning/STATE.md`

**Correção:** Remover SEC-07 da tabela "Deferred Items" em STATE.md. Se houver ressalva de escopo parcial, adicionar nota explicativa em vez de manter como pendente.

**Critério de aceitação:** STATE.md não contém mais SEC-07 na lista de itens adiados.

---

## 3. Documentação Desatualizada

### 3.1 MAPA-ARQUIVOS.md

**Problemas:**
- Não reflete a migração `packages/` → `apps/`
- Lista módulos frontend `home`, `users`, `structure` — faltam `admin-skins`, `importer`
- Não menciona `assets/` (favicon.ico, favicon.svg, favicon.png)
- Não menciona `shared/fonts/` (DM Sans, Barlow Condensed)
- Não menciona `skins/` (grindx-default.json, royal-purple.json)

**Arquivo:** `docs/MAPA-ARQUIVOS.md`

**Correção:** Reescrever a seção de estrutura de diretórios refletindo o estado atual do código, incluindo todos os novos módulos, assets, fontes e skins.

---

### 3.2 SETUP.md

**Problemas:**
- Paths de instalação referenciam `packages/api-postgres/`, `packages/api-sqlserver/`, `packages/frontend-webapp/`
- O correto é `apps/api-postgres/`, `apps/api-sqlserver/`, `apps/frontend-webapp/`

**Arquivo:** `docs/SETUP.md`

**Correção:** Atualizar todos os paths de instalação e configuração para o layout `apps/`.

---

### 3.3 API.md

**Problemas:**
- Documenta endpoints que não existem mais: `GET /v1/produtos/`, `POST /v1/produtos/`, `PUT/DELETE /v1/produtos/{id}`
- Não documenta novos endpoints: `GET/POST /v1/themes/`, `POST /v1/import/scan`, `POST /v1/import/{slug}`

**Arquivo:** `docs/API.md`

**Correção:** Remover documentação de endpoints removidos. Adicionar documentação dos novos endpoints (themes, import). Garantir que schemas de request/response estejam atualizados.

---

## 4. Melhorias

### 4.1 M-01 — Separar requirements dev/prod

**Descrição:** O `requirements.txt` atual mistura dependências de produção (FastAPI, SQLAlchemy, etc.) com dependências de desenvolvimento (pytest, pytest-asyncio, httpx, pytest-cov, ruff). Isso faz com que a imagem de container inclua ferramentas de teste desnecessárias.

**Arquivos:**
- `apps/api-postgres/requirements.txt` — remover deps dev
- `apps/api-postgres/requirements-dev.txt` — criar (herda de requirements.txt + dev deps)
- `Containerfile` (se existir) — ajustar para usar apenas `requirements.txt`

**Abordagem:**
1. Manter `requirements.txt` apenas com deps de produção
2. Criar `requirements-dev.txt` com:
   ```
   -r requirements.txt
   pytest>=8.0.0
   pytest-asyncio>=0.23.5
   httpx>=0.27.0
   pytest-cov>=6.0.0
   ruff>=0.3.0
   ```

**Critério de aceitação:** `pip install -r requirements.txt` não instala pytest nem ruff. `pip install -r requirements-dev.txt` instala tudo.

---

### 4.2 M-02 — Adicionar coverage threshold ao Jenkinsfile

**Descrição:** O `release.yml` (GitHub Actions) impõe `--cov-fail-under=70`. O `Jenkinsfile` não tem este threshold, criando disparidade entre pipelines.

**Arquivo:** `Jenkinsfile`

**Correção:** Adicionar `--cov-fail-under=70` ao comando pytest no Jenkinsfile.

**Critério de aceitação:** Jenkins falha se cobertura < 70%.

---

### 4.3 M-03 — Config.js injetável por ambiente

**Descrição:** `apps/frontend-webapp/shared/config.js` tem `API_BASE_URL` hardcoded como `http://localhost:8002/v1`. Em deploy, precisa ser editado manualmente. Risco de esquecimento.

**Arquivo:** `apps/frontend-webapp/shared/config.js`

**Correção:** Fazer o config.js ler de uma variável de ambiente ou injetar via servidor web (Nginx sub_filter). Alternativa: criar `config.template.js` com placeholder e script de substituição no CI.

**Abordagem recomendada:**
- Modificar `config.js` para checar `window.__GRINDX_API_URL` (injetado via Nginx ou script de bootstrap)
- Manter fallback para `http://localhost:8002/v1` em dev
- Documentar no SETUP.md como configurar em produção

---

### 4.4 M-04 — Renomear migrações inconsistentes

**Descrição:** Duas migrações Alembic têm nomenclatura fora do padrão sequencial:
- `02_add_org_schema_tables.py` (deveria ser `007_...`)
- `2026_06_02_add_temp_password_fields.py` (deveria ser `008_...`)

**Arquivos:** `apps/api-postgres/alembic/versions/`

**Correção:** Renomear arquivos mantendo o `down_revision` intacto para não quebrar a cadeia. Requer atualizar o `revision` (identity string) dentro do arquivo da migração.

**Risco:** Se o Alembic já registrou estas revisões no banco, renomear o identity string pode causar conflito. Estratégia segura: apenas registrar no spec como "baixa prioridade, fazer apenas se banco de dev for recriado".

**Abordagem alternativa (recomendada):** Não renomear identities — apenas renomear os arquivos para facilitar navegação. O Alembic usa o `revision` interno, não o nome do arquivo. Portanto, renomear só o arquivo é seguro e suficiente para organização visual.

---

### 4.5 M-05 — Sincronização automática da versão na tela de login

**Descrição:** A tela de login exibe a versão lendo `apps/frontend-webapp/version.json`. O `pyproject.toml` já define `build_command = "python scripts/update_frontend_version.py"` que deveria gerar este arquivo automaticamente após cada bump de versão, mas:
- `version.json` está em `v1.17.0` enquanto `APP_VERSION` está em `1.15.0` — prova de que a sincronização não está ocorrendo
- O script lê `APP_VERSION` do `config.py` da api-postgres e escreve em `version.json`
- A tela de login faz `fetch('version.json')` e exibe o resultado no `<span id="versionDisplay">`

**Causa raiz:** O `semantic-release` não executou com sucesso nas últimas releases (provável falta de `GH_TOKEN` no CI ou releases manuais via `git tag`), então o `build_command` nunca foi disparado.

**Arquivos:**
- `pyproject.toml` — `build_command` já configurado (linha 9)
- `scripts/update_frontend_version.py` — script de sincronização
- `apps/frontend-webapp/version.json` — arquivo gerado
- `.github/workflows/release.yml` — CI release

**Correções:**

1. **Verificar `build_command`:** Confirmar que `python scripts/update_frontend_version.py` executa com CWD = raiz do repositório. O python-semantic-release executa `build_command` do diretório do `pyproject.toml` (raiz), então o script deve funcionar. Validar manualmente:
   ```bash
   python scripts/update_frontend_version.py
   cat apps/frontend-webapp/version.json  # deve refletir APP_VERSION
   ```

2. **Adicionar step explícito no CI:** Mesmo com `build_command`, adicionar um passo explícito no `release.yml` após o `semantic-release version` para garantir que `version.json` foi gerado e incluso no commit:
   ```yaml
   - name: Gerar version.json
     run: python scripts/update_frontend_version.py
   
   - name: Commit version.json
     run: |
       git add apps/frontend-webapp/version.json
       git commit -m "chore(release): update version.json" || true
   ```

3. **Corrigir version.json atual:** Após corrigir B-02 (APP_VERSION), executar o script manualmente para sync:
   ```bash
   python scripts/update_frontend_version.py
   ```

**Critério de aceitação:** `apps/frontend-webapp/version.json` contém a mesma versão de `APP_VERSION` no `config.py`. Após um `semantic-release version`, o `version.json` é atualizado automaticamente e incluído no commit de release.

---

## 5. Ordens de Execução e Dependências

```
Fase 1 — Bugs (sem dependências externas)
  ├── 1.1 B-01: slowapi duplicado
  ├── 1.2 B-02: APP_VERSION
  └── 1.3 B-03: SEC-07 docs

Fase 2 — Documentação (pode rodar em paralelo)
  ├── 2.1 MAPA-ARQUIVOS.md
  ├── 2.2 SETUP.md
  └── 2.3 API.md

Fase 3 — Melhorias (independentes entre si)
  ├── 3.1 M-01: requirements-dev
  ├── 3.2 M-02: Jenkins coverage
  ├── 3.3 M-03: config.js injetável
  ├── 3.4 M-04: migrações renomeadas
  └── 3.5 M-05: version.json automático (executar após B-02)
```

Cada fase não depende da anterior. A ordem segue risco × impacto: bugs primeiro porque afetam a execução atual, docs depois porque afetam a equipe, melhorias por último porque têm menor urgência.

---

## 6. Riscos

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| B-02: tags git ausentes | Versão continua errada no header | Verificar tags antes de corrigir; criar se necessário |
| M-04: renomear migrações quebra banco existente | Falha em `alembic upgrade` | Renomear apenas arquivo, não `revision` interna |
| M-03: config.js quebra frontend em produção | API calls falham | Manter fallback localhost; testar em dev primeiro |
| M-01: requirements-dev não testado | CI quebra | Validar com `pip install -r` em pipeline de teste |
| M-05: build_command falha em CWD errado | version.json não gerado | Validar manualmente + step explícito no CI |

---

## 7. Critérios de Aceitação Globais

1. `ruff check .` passa sem erros
2. `pytest tests/` passa com cobertura >= 70%
3. Health check de ambas as APIs retorna versão correta
4. SETUP.md descreve instalação com paths `apps/`
5. Nenhum endpoint removido aparece em API.md
6. `requirements.txt` não contém pytest nem ruff
7. `version.json` reflete o mesmo valor de `APP_VERSION` do `config.py`
8. Tela de login exibe a versão correta do release atual
