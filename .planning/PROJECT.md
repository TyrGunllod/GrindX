# GrindX — Technical Concerns Remediation

## What This Is

Plano completo para eliminar todas as preocupações técnicas identificadas no CONCERNS.md do projeto GrindX. O projeto é um ERP monorepo com dual FastAPI backends (PostgreSQL + SQL Server), frontend vanilla JS e pacote shared Python. O objetivo é transformar o código de "funciona mas tem dívidas" em "seguro, testado e maintível".

## Core Value

Eliminar todos os problemas técnicos identificados para que o GrindX seja seguro, performante e maintível — zero pendências no CONCERNS.md.

## Requirements

### Validated

- ✓ API Postgres funcional (porta 8002) — existing
- ✓ API SQL Server funcional (porta 8001) — existing
- ✓ Frontend portal com módulos — existing
- ✓ Pacote shared com JWT, RBAC, exceções — existing
- ✓ CI/CD com GitHub Actions — existing
- ✓ Codebase map completo (.planning/codebase/) — existing

### Active

**Segurança (HIGH):**
- [ ] SECRET_KEY com validação de entropia além de comprimento mínimo
- [ ] Senhas temporárias com expiração e força adequada
- [ ] Rate limiting por usuário (não apenas por IP)
- [ ] CORS configurado corretamente para produção
- [ ] Proteção CSRF implementada
- [ ] Validação completa de uploads (magic bytes, não apenas extensão/content-type)

**Dívida Técnica (HIGH/MEDIUM):**
- [ ] pytest-cov configurado com cobertura mínima
- [ ] Migrações duplicadas resolvidas (001_create_tables vs 001_initial_schema)
- [ ] Re-exports de modelos eliminados ou documentados
- [ ] PYTHONPATH resolvido via instalação do pacote shared

**Performance (MEDIUM):**
- [ ] Camada de cache (Redis ou in-memory) para queries frequentes
- [ ] Database indexing strategy definida e implementada
- [ ] Frontend com lazy loading para módulos

**Áreas Frágeis (MEDIUM):**
- [ ] Health check profundo (verifica conectividade com DB)
- [ ] Error codes centralizados em registry
- [ ] Versionamento de API documentado

**Missing Features (LOW):**
- [ ] API versioning strategy
- [ ] OpenAPI spec exportada
- [ ] Client SDK generation (opcional)

### Out of Scope

- Migração para async SQLAlchemy — refactoring grande, não crítico agora
- Migração de frontend para framework — vanilla JS funciona, não é prioridade
- Real-time/WebSocket — não faz parte das preocupações atuais

## Context

- **Ambiente**: Windows (PowerShell), Python 3.12+, Podman containers
- **Banco**: PostgreSQL (produção), SQLite (testes), SQL Server (read-only)
- **CI**: GitHub Actions com SQLite in-memory
- **Testes**: pytest com markers (unit, integration, slow)
- **Linting**: Ruff (select E, F, I; ignore E501)
- **Codebase map**: 7 documentos em `.planning/codebase/` detalhando stack, arquitetura, estrutura, convenções, testes, integrações e preocupações

## Constraints

- **Compatibilidade**: Correções não podem quebrar funcionalidade existente
- **Testes**: Cada correção deve ter teste associado
- **Phases**: Segurança primeiro, depois dívida técnica, performance e áreas frágeis
- **Zero pendências**: "Feito" = CONCERNS.md vazio ou todos os itens marcados como resolvidos

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Fases priorizando segurança | Vulnerabilidades de segurança têm impacto imediato | — Pending |
| Testes obrigatórios para cada correção | Garante que correções não introduzem regressões | — Pending |
| Todos os problemas (não apenas HIGH) | Dívida técnica acumulada precisa ser resolvida | — Pending |

## Evolution

Este documento evolui conforme as fases são completadas.

**After each phase transition:**
1. Preocupações resolvidas? → Marcar como concluída no CONCERNS.md
2. Novas preocupações surgidas? → Adicionar ao CONCERNS.md
3. Decisões técnicas? → Adicionar ao Key Decisions

**After milestone completion:**
1. Revisão completa de todas as seções
2. Verificar se Core Value foi alcançada
3. CONCERNS.md deve estar vazio ou todos os itens resolvidos

---
*Last updated: 2026-06-02 after initialization*
