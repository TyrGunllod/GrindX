# Design — Atualizar módulo sem desinstalar (issue #7)

**Data:** 2026-11-24
**Status:** Aguardando aprovação
**Escopo:** `apps/api-postgres/scripts/import_module.py`, `apps/api-postgres/app/routers/import_router.py`, `apps/api-postgres/app/core/config.py`, `compose.yaml`, `apps/frontend-webapp/modules/importer/`, `docs/IMPORTACAO.md`

---

## 1. Contexto e problema

Issue #7: hoje, para atualizar um módulo já instalado, é preciso removê-lo e importar de novo.

O `DELETE /v1/import/{module}` apaga arquivos backend/frontend, as migrations do módulo, o registro em `portal.modulos` (nome, aba, URL, ícone, ordem, role mínima) e as permissões em `usuario_modulo`. O reinstalar não recria esses vínculos — a associação com a aba é manual em Portal → Estrutura.

O reimport por cima **já existe**: `POST /v1/import/{module}` com `force=True` troca backend/frontend, mantém `portal.modulos` intocado e, quando o banco está na cadeia do módulo, mantém as migrations aplicadas e acrescenta apenas as novas. Faltam quatro coisas:

1. Expor a atualização com um botão "Atualizar".
2. Não deixar registros órfãos em `main.py`, `dependencies.py` e `alembic/env.py` quando a nova versão remove ou renomeia classes.
3. O código novo entrar no ar. Em produção o container roda `uvicorn` sem `--reload` (`apps/api-postgres/Dockerfile:30`), então o processo continua com o módulo antigo em memória.
4. Falha de migration não ser silenciosa. Hoje o fluxo da API sempre responde antes das migrations (`import_router.py:323` + thread que só loga) e o caminho CLI engole a exceção devolvendo `success: True` (`import_module.py:1037-1045`). Pior: `copy_migration()` apaga migrations não aplicadas (`stale.unlink()`, linhas 549-551) e, em revisão órfã, faz `stamp_revision` no head do módulo sem aplicar nada (linhas 563-575) — o banco passa a dizer que está atualizado sem estar.

---

## 2. Objetivo, não-objetivo e anti-objetivo

**Objetivos:** atualizar um módulo instalado pelo Importador preservando aba, ordem, role mínima, permissões de usuário, dados e migrations já aplicadas; falha de migration bloqueia a atualização com a mensagem do alembic; histórico de migrations nunca é apagado nem carimbado sem aplicação; em produção a API reinicia sozinha após a atualização.

**Não-objetivos:** atualização em lote, comparação de versões semver, endpoint dedicado de update, backup de schema com `pg_dump`, downgrade automático.

**Anti-objetivos:** escrever em `portal.modulos`/`usuario_modulo` durante a atualização; apagar migrations do módulo; recriar tabelas.

---

## 3. Abordagens consideradas

| # | Abordagem | Trade-off | Decisão |
|---|---|---|---|
| A | Reusar `import_module(force=True)` + limpeza/regeneração de registros + botão "Atualizar" | Diff pequeno, reaproveita fluxo e testes existentes | **Escolhida** |
| B | Endpoint dedicado `POST /v1/import/{slug}/update` | Mais explícito, duplica a orquestração do import | Descartada |
| C | Só adicionar o botão na UI | Menor diff, mantém API quebrada no restart quando classes somem | Descartada |

Para o restart: `--reload` no Dockerfile foi descartado (reinicia no meio da cópia de arquivos e aborta o import in-process). Escolhido auto-restart por `SIGTERM` atrás de flag explícita, usando o `restart: unless-stopped` que já existe (`compose.yaml:64`).

Para migrations: downgrade automático é desnecessário — `alembic/env.py:75` executa a cadeia em uma transação e no Postgres DDL é transacional, então a falha desfaz o que aquela execução aplicou. O que falta é parar de silenciar a falha e parar de forjar/apagar histórico.

---

## 4. O que será feito

### 4.1 Backend — `scripts/import_module.py`

1. Validar, logo após `validate_manifest()` e antes do backup/cópia, que `manifest["module_name"]` é igual ao `module_name` recebido (slug da URL). Hoje o *fuzzy match* do `import_router` pode selecionar um zip de outro módulo; como `copy_backend` usa o slug e `copy_migration`/`register_*` usam o manifest, a divergência altera a cadeia de migrations de outro módulo e ainda responde sucesso. Divergência vira `ValueError`, que o `except` existente já devolve como `success: false`.
2. Extrair de `remove_module()` a limpeza de registros para `_clean_registrations(module_name, steps)`: `_clean_main_py` (main.py da API), factories/imports em `auth/dependencies.py`, imports em `alembic/env.py` e `_clean_requirements_txt`. `remove_module()` passa a chamar essa função — sem duplicação.
3. Em `import_module()`, detectar atualização antes do `copy_backend` (diretório do backend já existe) e, quando for atualização, rodar `_clean_registrations` entre `copy_backend` e `merge_requirements`. Depois o fluxo normal (`register_router`, `register_dependency`, `register_alembic_import`) regenera tudo a partir dos arquivos novos.
4. Falha de migration deixa de ser engolida: o `except` de `run_migrations()` relança e o `except` externo devolve `success: false` com o stderr do alembic. O rollback de arquivos existente continua valendo.
5. Depois de `run_migrations()`, ler `_get_db_current_revision()` e acrescentar step `"Schema na revisão <rev>"`.
6. In `copy_migration()`: não apagar migration não aplicada (`stale.unlink()` removido, vira warning no log) e, em revisão órfã, recusar com `RuntimeError` informando a revisão do banco e o head do módulo em vez de `_stamp_revision`.
7. Retornar `updated: True` no resultado e acrescentar step `"Atualização concluída — reinicie a API para carregar o novo código"` (ou `"Atualização concluída — a API vai reiniciar"` quando o restart automático estiver ligado).

Ordem final: validar slug → backup → copy_backend → (update: clean registrations) → merge_requirements → copy_frontend → copy_migration → register_* → migrations → revisão atual.

### 4.2 Backend — `app/routers/import_router.py`

- Antes de chamar o import, detectar atualização (`app/modules/{module_name}` já existe).
- **Atualização:** `skip_migrations=False` (migrations rodam inline, antes da resposta) e sem thread de background. Falha de migration chega ao Importador como `success: false`.
- **Instalação nova:** mantém `skip_migrations=True` + `_run_migrations_background`.
- Mensagem de sucesso: `"Módulo atualizado com sucesso."` quando `updated`, senão `"Módulo importado com sucesso."`.
- Auto-restart: `settings.import_auto_restart` (novo bool, default `False`, em `app/core/config.py`) + `BackgroundTasks`. Quando a flag está ligada e o resultado é `updated: true`, agenda `_restart_api()` — espera 2s e envia `SIGTERM` no próprio processo; o `restart: unless-stopped` do container levanta de novo.
- `compose.yaml`: `IMPORT_AUTO_RESTART=true` no serviço `api-postgres`. Default `False` protege o dev (`--reload` não pode ser morto).

### 4.3 Frontend — `modules/importer/`

- Tabela de zips disponíveis: quando `ja_importado`, o botão vira **"Atualizar"** (`data-action="update"`) no lugar de "Remover". Remover continua disponível na tabela de instalados.
- Modal de atualização: "Atualizar para a versão X? A aba, a ordem, as permissões e os dados serão preservados."
- `confirmarImport()` passa a usar `this.currentAction` em vez de comparar o título do modal.

### 4.4 Docs

`docs/IMPORTACAO.md`: seção "Atualizar módulo" — o que é preservado, migrations novas/falhas, restart automático em produção e necessidade de restart manual fora do container.

---

## 5. Testes

- `import_module`: primeira importação não chama a limpeza; segunda (diretório existente) chama `_clean_main_py`/dependencies/env/requirements antes de registrar.
- Nova versão que remove um service: `dependencies.py` final não contém import nem factory da classe removida.
- Zip com `module_name` divergente do slug: `import_module` falha antes do backup, sem copiar nem registrar nada.
- `run_migrations()` levantando: `import_module` devolve `success: False` com o erro.
- `copy_migration`: revisão órfã levanta erro; migration não aplicada não é apagada.
- `import_router`: atualização passa `skip_migrations=False` e não agenda background; instalação nova mantém o background.
- `import_router`: resposta com `updated=True` usa a mensagem "Módulo atualizado com sucesso.".
- `_restart_api` só é agendado com a flag ligada + `updated`.
- Nenhum teste toca em `portal.modulos`/`usuario_modulo` — a preservação é por ausência de escrita.

---

## 6. Limites conhecidos

- Sem backup de schema antes da atualização (`pg_dump`): uma migration destrutiva (drop/rename) continua sem rede de segurança.
- Sem downgrade automático: a transação do alembic desfaz a execução que falhou, mas nada desfaz uma migration que aplicou com sucesso.
- O restart automático derruba requisições em voo no momento em que ocorre.
- SQL Server não tem esta cadeia de migrations nem `dependencies.py`; a limpeza se resume ao `main.py` e o restart automático vale igual.
