# Requirements: GrindX — Technical Concerns Remediation

**Defined:** 2026-06-02
**Core Value:** Eliminar todos os problemas técnicos identificados para que o GrindX seja seguro, performante e maintível — zero pendências no CONCERNS.md.

## v1 Requirements

Requisitos para a remediação completa. Cada um mapeia para fases do roadmap.

### Segurança

- [ ] **SEC-01**: SECRET_KEY com validação de entropia Shannon (mínimo 3.5 bits/caractere) além de comprimento mínimo de 32 caracteres
- [ ] **SEC-02**: Senhas temporárias com expiração de 15 minutos e geração via `secrets` module (não `token_hex`)
- [ ] **SEC-03**: Rate limiting baseado em usuário autenticado (SlowAPI com chaves duplas: IP para não-autenticados, user_id para autenticados)
- [ ] **SEC-04**: Validação de uploads com magic bytes (biblioteca `filetype`) para logos e fontes, não apenas extensão/content-type
- [ ] **SEC-05**: CORS configurado com validação estrita em produção (nunca `*` em prod, lista de origens explícita)

### Infraestrutura

- [ ] **INFRA-01**: pytest-cov configurado com threshold mínimo de 70% (`--cov-fail-under=70`) e relatório no CI
- [ ] **INFRA-02**: Migrações Alembic duplicadas consolidadas (resolver conflitos de prefixo `001_*`)
- [ ] **INFRA-03**: Validação de schema translate map em testes (verificar que `_SCHEMA_TRANSLATE` cobre todos os schemas PostgreSQL usados)

### Performance

- [ ] **PERF-01**: Camada de cache in-memory com `cachetools` para queries frequentes (temas ativos, configurações de empresa)
- [ ] **PERF-02**: Estratégia de indexação no banco de dados (índices compostos para queries comuns, índices funcionais para busca case-insensitive)
- [ ] **PERF-03**: Health checks profundos que verificam conectividade com PostgreSQL e SQL Server (com graceful degradation)

## v2 Requirements

Requisitos deferidos para futuro release. Rastreados mas não no roadmap atual.

### Segurança Avançada

- **SEC-06**: Invalidação de JWT após mudança de senha (token_version no modelo Usuario ou Redis blacklist)
- **SEC-07**: Proteção contra path traversal em endpoints de upload (validação de caminhos)
- **SEC-08**: Headers de segurança avançados (CSP, HSTS, X-Frame-Options)

### Observabilidade

- **OBS-01**: Logging estruturado JSON com correlação de request IDs
- **OBS-02**: Métricas de performance de queries (slow query logging)
- **OBS-03**: Audit logging para operações sensíveis

### Qualidade

- **QUA-01**: Type checking com mypy (strict mode gradual)
- **QUA-02**: Mutation testing com mutmut para validar qualidade de testes
- **QUA-03**: Contract testing para APIs

## Out of Scope

| Feature | Reason |
|---------|--------|
| Migração para async SQLAlchemy | Refactoring grande, não crítico agora |
| Migração de frontend para framework | Vanilla JS funciona, não é prioridade |
| Migração para Redis cache | Adiciona complexidade de infraestrutura |
| Microservice decomposition | Monorepo funciona para escala atual |
| Custom auth framework | JWT + RBAC atual é suficiente |

## Traceability

Quais fases cobrem quais requisitos. Atualizado durante criação do roadmap.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SEC-01 | Phase 1: Security Hardening | Pending |
| SEC-02 | Phase 1: Security Hardening | Pending |
| SEC-03 | Phase 1: Security Hardening | Pending |
| SEC-04 | Phase 1: Security Hardening | Pending |
| SEC-05 | Phase 1: Security Hardening | Pending |
| INFRA-01 | Phase 2: Infrastructure & Quality | Pending |
| INFRA-02 | Phase 2: Infrastructure & Quality | Pending |
| INFRA-03 | Phase 2: Infrastructure & Quality | Pending |
| PERF-01 | Phase 3: Performance & Resilience | Pending |
| PERF-02 | Phase 3: Performance & Resilience | Pending |
| PERF-03 | Phase 3: Performance & Resilience | Pending |

**Coverage:**
- v1 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0 ✓

---
*Requirements defined: 2026-06-02*
*Last updated: 2026-06-02 after roadmap creation*
