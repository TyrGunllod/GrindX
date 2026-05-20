"""
Guia de RBAC (Role-Based Access Control) para o ERP.

Define como usar o sistema de permissões nas rotas.
"""

# ============================================================================
# 1. DEFINIÇÃO DE ROLES
# ============================================================================

# Hierarquia: admin > operador > leitura
#
# ADMIN:
#   - Acesso completo a todas as operações
#   - Pode criar, atualizar, deletar e listar recursos
#   - Acesso a relatórios e configurações
#
# OPERADOR:
#   - Acesso a operações CRUD normais
#   - Pode criar, atualizar e listar
#   - NÃO pode deletar
#
# LEITURA:
#   - Acesso somente leitura (GET)
#   - NÃO pode criar, atualizar ou deletar

# ============================================================================
# 2. USANDO @require_role NAS ROTAS
# ============================================================================

from fastapi import APIRouter, Depends

from shared.security.permissions import Role, require_role, require_role_or_higher

router = APIRouter()

# Exemplo 1: Rota somente para admin
@router.delete(
    "/recurso/{id}",
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def deletar_recurso(id: int, current_user = Depends(get_current_user)):  # noqa: F821  # noqa: F821
    """Somente admin pode deletar."""
    pass

# Exemplo 2: Rota para admin e operador
@router.post(
    "/recurso",
    dependencies=[Depends(require_role(Role.ADMIN, Role.OPERADOR))],
)
def criar_recurso(dados: dict, current_user = Depends(get_current_user)):  # noqa: F821  # noqa: F821
    """Admin e operador podem criar."""
    pass

# Exemplo 3: Rota para todos
@router.get(
    "/recurso",
    dependencies=[Depends(require_role(Role.ADMIN, Role.OPERADOR, Role.LEITURA))],
)
def listar_recursos(current_user = Depends(get_current_user)):  # noqa: F821  # noqa: F821
    """Todos podem ler."""
    pass

# ============================================================================
# 3. USANDO @require_role_or_higher (Hierarquia)
# ============================================================================

# Use quando quer permitir a role e todas as superiores

# Exemplo: Requer operador ou superior (admin)
@router.post(
    "/relatorio",
    dependencies=[Depends(require_role_or_higher(Role.OPERADOR))],
)
def gerar_relatorio(current_user = Depends(get_current_user)):  # noqa: F821  # noqa: F821
    """Admin e operador podem gerar relatório.
    Leitura não consegue (é inferior a operador).
    """
    pass

# ============================================================================
# 4. MATRIX DE PERMISSÕES
# ============================================================================

# CATEGORIA: PRODUTOS
# Endpoint           | Admin | Operador | Leitura
# ------------------|-------|----------|--------
# GET /produtos       |  ✓    |    ✓     |   ✓
# POST /produtos      |  ✓    |    ✓     |   ✗
# DELETE /produtos/{id}| ✓    |    ✗     |   ✗

# CATEGORIA: USUÁRIOS
# Endpoint           | Admin | Operador | Leitura
# ------------------|-------|----------|--------
# GET /usuarios       |  ✓    |    ✗     |   ✗
# POST /usuarios      |  ✓    |    ✗     |   ✗
# DELETE /usuarios/{id}| ✓    |    ✗     |   ✗

# CATEGORIA: PORTAL (ESTRUTURA)
# Endpoint           | Admin | Operador | Leitura
# ------------------|-------|----------|--------
# GET /portal/menu    |  ✓    |    ✓     |   ✓
# POST /portal/abas   |  ✓    |    ✗     |   ✗
# PUT /portal/modulos |  ✓    |    ✗     |   ✗

# ============================================================================
# 5. ACESSAR ROLE DO USUÁRIO NA ROTA
# ============================================================================

from shared.schemas.auth import TokenPayload  # noqa: E402  # noqa: E402


@router.get("/perfil")
def meu_perfil(current_user: TokenPayload = Depends(get_current_user)):  # noqa: F821  # noqa: F821
    """Acessa a role do usuário autenticado."""
    return {
        "user_id": current_user.sub,
        "role": current_user.role,  # "admin", "operador" ou "leitura"
    }

# ============================================================================
# 6. VERIFICAR HIERARQUIA PROGRAMATICAMENTE
# ============================================================================

from shared.security.permissions import get_user_roles_hierarchy  # noqa: E402,I001


def exemplo_hierarquia():
    # Retorna lista de roles que o usuário pode acessar
    roles_do_admin = get_user_roles_hierarchy("admin")  # noqa: F841  # noqa: F841
    # Resultado: ["admin", "operador", "leitura"]

    roles_do_operador = get_user_roles_hierarchy("operador")  # noqa: F841  # noqa: F841
    # Resultado: ["operador", "leitura"]

    roles_da_leitura = get_user_roles_hierarchy("leitura")  # noqa: F841  # noqa: F841
    # Resultado: ["leitura"]

# ============================================================================
# 7. MENSAGENS DE ERRO
# ============================================================================

# Quando usuário não tem permissão, retorna 403 Forbidden:
# {
#   "error": "ACESSO_NEGADO",
#   "message": "Acesso restrito aos perfis: admin.",
#   "status_code": 403
# }

# ============================================================================
# 8. TESTANDO RBAC
# ============================================================================

# Testes unitários em shared/tests/test_permissions.py
# Testes de integração em tests/integration/test_rbac_produtos.py

# Executar testes:
# pytest shared/tests/test_permissions.py -v
# pytest tests/integration/test_rbac_produtos.py -v

# ============================================================================
# 9. BOAS PRÁTICAS
# ============================================================================

# ✓ FAZER:
#   - Usar require_role para proteger operações sensíveis
#   - Documentar a role requerida na description da rota
#   - Incluir 403 nos responses da documentação
#   - Testar cada combinação de role × endpoint

# ✗ NÃO FAZER:
#   - Validar role manualmente dentro da função (use @require_role)
#   - Misturar lógica de autenticação com negócio
#   - Esquecer de proteger novas rotas sensíveis
#   - Usar role.value em vez de Role enum

# ============================================================================
# 10. FLUXO DE REQUISIÇÃO COM RBAC
# ============================================================================

# Requisição HTTP com Bearer Token
# ↓
# HTTPBearer extrai o token do header Authorization
# ↓
# get_current_user() decodifica o JWT e valida
# ↓
# require_role() verifica se a role está na lista permitida
# ↓
# Se OK: continua para a função da rota
# Se NÃO: retorna 403 Forbidden (ForbiddenError)
