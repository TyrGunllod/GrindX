# AGENTS.md — Regras para Agentes de IA

## ⚠️ Regras Críticas — leia antes de qualquer tarefa

Estas regras causam falha de CI, bug sutil ou retrabalho quando ignoradas. Revise esta lista antes de considerar qualquer tarefa concluída.

**Sempre:**
- [ ] Antes de `git push`: executar testes → formatar código → lint, nesta ordem (ver Pre-push)
- [ ] Manter `database.sql`, os modelos e a migration em sincronia (o teste de contrato compara as colunas)
- [ ] Modal fecha só no **Cancelar** ou **depois de salvar com sucesso** — sem X no cabeçalho, sem `Escape`, sem fechar no clique do overlay (`test_modal_contrato.py`)
- [ ] Usar tokens/constantes do design system — nunca valores fixos (cores, fontes, espaçamentos)
- [ ] Usar constantes/enums de erro — nunca strings literais de erro
- [ ] Atualizar documentação (README, docs/) ao alterar código relevante

**Nunca sem confirmação explícita do usuário:**
- [ ] `CORS_ORIGINS=*` em qualquer ambiente que não seja dev local
- [ ] Editar uma migration já mergeada na branch principal — sempre criar uma nova
- [ ] Remover ou pular um teste que está falhando
- [ ] Fazer rewrite amplo do repositório — preferir diffs pequenos e focados
- [ ] Adicionar endpoints de escrita em APIs somente leitura

---

## Estrutura do Projeto

Descreva aqui a estrutura de diretórios do projeto, serviços, portas e responsabilidades de cada componente.

---

## Comandos do Desenvolvedor

Documente os comandos principais: inicialização, execução de serviços, testes, lint, build, deploy.

---

## Pre-push (obrigatório antes de todo git push)

> **ATENÇÃO:** Estas etapas são MANDATÓRIAS antes de todo `git push`.
> Pular esta verificação causa falha no CI. Execute nesta ordem:

- [ ] Testes: comando para rodar a suite completa
- [ ] Formatação: comando para formatar o código
- [ ] Lint: comando para verificar — sem erros
- [ ] Scripts: `python -m py_compile scripts/version.py export.py` (se ambos existirem)

---

## Testing

- Descreva o framework de testes, marcadores (unit, integration, slow), e estratégias (ex: banco em memória para integração)
- Cobertura mínima obrigatória no CI (ex: 70%)
- Comandos e variáveis de ambiente necessárias para rodar os testes

---

## Commit & Release

- Formato: [conventional commits](https://www.conventionalcommits.org/)
- Padrão de idioma para título e descrição dos commits
- CI pipeline: push → lint + testes + release (se aplicável)
- **Versionamento**: `python scripts/version.py` (ou `make version`) gera a próxima versão semver a partir de conventional commits:
  - `BREAKING CHANGE` / `feat!: ...` → MAJOR; `feat:` → MINOR; demais → PATCH
  - Atualiza `module.json` + todos as `frontend/*/version.js`
  - Cria a tag `vX.Y.Z`; use `--dry-run` (simula) e `--no-tag` (não cria tag)
  - Commits de release (`docs: registrar changelog`) são ignorados pelo script
- **Fluxo de release em duas etapas** (a tag deve ficar no commit que contém o CHANGELOG):
  1. `python scripts/version.py --no-tag` — atualiza `module.json` + `frontend/*/version.js` + `CHANGELOG.md`
  2. Commitar esses artefatos e então criar a tag `git tag vX.Y.Z`
  - ⚠️ O padrão `make version` cria a tag no commit atual, ANTES do commit dos artefatos — `git checkout vX.Y.Z` não conteria o changelog

---

## Banco de dados — Standalone vs GrindX

- **Standalone**: o repositório não tem `alembic.ini`, então a migration não roda aqui. O preparo do banco é o `database.sql` da raiz — idempotente (`CREATE SCHEMA/TABLE/INDEX IF NOT EXISTS`), sem `DROP`, aplicado por `make db-init` (`scripts/db_init.py`, que usa o driver Python e dispensa o `psql`).
- **GrindX**: a fonte da verdade é a migration (`migration/{revision}_{table}_...py`), aplicada pelo `make export`. **Nunca** rode o `database.sql` lá.
- `database.sql` é PostgreSQL (`SERIAL`, `TIMESTAMPTZ`, `NUMERIC`); os testes de integração usam SQLite in-memory com `create_all`.
- O `package()` do `export.py` inclui `database.sql` no zip.

---

## Arquitetura — Pontos não óbvios

- Restrições de acesso (ex: APIs somente leitura)
- Estrutura de módulos/pacotes
- Design system e convenções de estilo (ex: CSS tokens)
- Ordem de carregamento de scripts
- Containerização: ferramenta, configurações especiais, sistema de arquivos
- Variáveis de ambiente críticas e seus valores padrão
- URLs e configurações de rede (CORS, CSP, proxy)

---

## Códigos de Erro

Registro centralizado de códigos de erro. Use constantes em vez de strings literais. Documente o caminho do módulo de erros e como importar/usar.

---

## Segurança

- **Standalone não autentica.** `app/core/auth.py` devolve sempre a identidade de desenvolvimento (`USUARIO_DEV = 1`); `X-Usuario-Id` só serve para simular outro usuário. Autenticação de verdade é exclusivamente o JWT do GrindX — por isso o standalone jamais deve ser publicado em ambiente exposto, e o frontend nunca guarda segredo.

- Validação de secrets (entropia mínima, requisitos)
- CORS: modo strict em produção (nunca `*`)
- Rate limiting: estratégia e chaves utilizadas
- Nunca commitar secrets ou chaves no repositório

---

## Performance

- Estratégia de cache (TTL, escopo)
- Índices de banco de dados relevantes
- Otimizações específicas do projeto

---

## Docs Sync

Sempre atualizar a documentação relevante ao alterar código. Liste os arquivos de documentação que devem ser mantidos sincronizados (ex: `README.md`, `docs/API.md`, `docs/SETUP.md`, este `AGENTS.md`).
