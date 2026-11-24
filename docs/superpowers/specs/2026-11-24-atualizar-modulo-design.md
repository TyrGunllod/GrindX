# Design — Atualizar módulo sem desinstalar (issue #7)

**Data:** 2026-11-24
**Status:** Aguardando aprovação
**Escopo:** `apps/api-postgres/scripts/import_module.py`, `apps/api-postgres/app/routers/import_router.py`, `apps/frontend-webapp/modules/importer/`, `docs/IMPORTACAO.md`

---

## 1. Contexto e problema

Issue #7: hoje, para atualizar um módulo já instalado, é preciso removê-lo e importar de novo.

O `DELETE /v1/import/{module}` apaga arquivos backend/frontend, as migrations do módulo, o registro em `portal.modulos` (nome, aba, URL, ícone, ordem, role mínima) e as permissões em `usuario_modulo`. O reinstalar não recria esses vínculos — a associação com a aba é manual em Portal → Estrutura.

O reimport por cima **já existe**: `POST /v1/import/{module}` com `force=True` troca backend/frontend, mantém `portal.modulos` intocado e, quando o banco está na cadeia do módulo, mantém as migrations aplicadas e acrescenta apenas as novas. O que falta é expor isso com um botão "Atualizar" e garantir que os registros em `main.py`, `dependencies.py` e `alembic/env.py` não fiquem órfãos quando a nova versão remove ou renomeia classes.

---

## 2. Objetivo, não-objetivo e anti-objetivo

**Objetivo:** atualizar um módulo instalado pelo Importador preservando aba, ordem, role mínima, permissões de usuário, dados e migrations já aplicadas.

**Não-objetivos:** atualização em lote, comparação de versões semver, endpoint dedicado de update, hot reload da API.

**Anti-objetivos:** escrever em `portal.modulos`/`usuario_modulo` durante a atualização; apagar migrations do módulo; recriar tabelas.

---

## 3. Abordagens consideradas

| # | Abordagem | Trade-off | Decisão |
|---|---|---|---|
| A | Reusar `import_module(force=True)` + limpeza/regeneração de registros + botão "Atualizar" | Diff pequeno, reaproveita fluxo e testes existentes | **Escolhida** |
| B | Endpoint dedicado `POST /v1/import/{slug}/update` | Mais explícito, duplica a orquestração do import | Descartada |
| C | Só adicionar o botão na UI | Menor diff, mantém API quebrada no restart quando classes somem | Descartada |

---

## 4. O que será feito

### 4.1 Backend — `scripts/import_module.py`

1. Extrair de `remove_module()` a limpeza de registros para `_clean_registrations(module_name, steps)`: `_clean_main_py` (main.py da API), factories/imports em `auth/dependencies.py`, imports em `alembic/env.py` e `_clean_requirements_txt`. `remove_module()` passa a chamar essa função — sem duplicação.
2. Em `import_module()`, detectar atualização antes do `copy_backend` (diretório do backend já existe) e, quando for atualização, rodar `_clean_registrations` entre `copy_backend` e `merge_requirements`. Depois o fluxo normal (`register_router`, `register_dependency`, `register_alembic_import`) regenera tudo a partir dos arquivos novos.
3. Retornar `updated: True` no resultado e acrescentar step: `"Atualização concluída — reinicie a API para carregar o novo código"`.

Ordem final: backup → copy_backend → (update: clean registrations) → merge_requirements → copy_frontend → copy_migration → register_* → migrations.

### 4.2 Backend — `app/routers/import_router.py`

Sem rota nova. A mensagem de sucesso passa a ser "Módulo atualizado com sucesso." quando `updated` vier no resultado; o resto do fluxo (zip removido, migrations em background) fica igual.

### 4.3 Frontend — `modules/importer/`

- Tabela de zips disponíveis: quando `ja_importado`, o botão vira **"Atualizar"** (`data-action="update"`) no lugar de "Remover". Remover continua disponível na tabela de instalados.
- Modal de atualização: "Atualizar para a versão X? A aba, a ordem, as permissões e os dados serão preservados."
- `confirmarImport()` passa a usar `this.currentAction` em vez de comparar o título do modal.

### 4.4 Docs

`docs/IMPORTACAO.md`: seção "Atualizar módulo" — o que é preservado, necessidade de reiniciar a API e o que acontece com migrations novas.

---

## 5. Testes

- `import_module`: primeira importação não chama a limpeza; segunda (diretório existente) chama `_clean_main_py`/dependencies/env/requirements antes de registrar.
- Nova versão que remove um service: `dependencies.py` final não contém import nem factory da classe removida.
- `import_router`: resposta com `updated=True` usa a mensagem "Módulo atualizado com sucesso.".
- Nenhum teste toca em `portal.modulos`/`usuario_modulo` — a preservação é por ausência de escrita.

---

## 6. Limites conhecidos

- A API em produção roda sem `--reload`: o código novo só entra no ar após restart (avisado no step).
- Um zip com `module_name` diferente do slug da URL continua sobrescrevendo o módulo do slug — comportamento atual, fora do escopo.
- Migrations novas são copiadas a partir da revisão atual do banco (`copy_migration` já faz isso); não há validação de downgrade.
