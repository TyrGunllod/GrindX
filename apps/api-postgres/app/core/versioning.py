"""
Estratégia de versionamento de API do GrindX.

Todas as rotas usam o prefixo /v1/ padronizado.
Para adicionar uma nova versão:
1. Criar um novo conjunto de rotas com prefixo /v2/
2. Manter as rotas /v1/ funcionando por pelo menos 6 meses
3. Adicionar header de depreciação nas rotas /v1/
4. Documentar mudanças no CHANGELOG.md
"""

API_VERSION = "v1"
API_PREFIX = f"/{API_VERSION}"

# Endpoints públicos (sem autenticação)
PUBLIC_ENDPOINTS = [
    "/health",
    f"{API_PREFIX}/docs",
    f"{API_PREFIX}/redoc",
    f"{API_PREFIX}/openapi.json",
]

# Rotas que requerem autenticação
PROTECTED_ROUTES = [
    f"{API_PREFIX}/usuarios",
    f"{API_PREFIX}/themes",
    f"{API_PREFIX}/portal",
    f"{API_PREFIX}/import",
]
