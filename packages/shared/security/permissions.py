"""
Sistema de permissões baseado em roles (RBAC).

Define os papéis disponíveis, hierarquia de permissões e dependencies
para verificação de permissão nas rotas protegidas.

Hierarquia de permissões:
    admin ≥ operador ≥ leitura

Exemplos de uso:
    @router.post("/produtos", dependencies=[Depends(require_role(Role.OPERADOR))])
    def criar_produto(...):
        ...

    @router.put(
        "/produtos/{id}",
        dependencies=[Depends(require_role(Role.ADMIN, Role.OPERADOR))]
    )
    def atualizar_produto(...):
        ...
"""

from enum import StrEnum
from functools import wraps
from typing import Callable

from fastapi import Depends

from shared.exceptions.base import ForbiddenError
from shared.schemas.auth import TokenPayload


class Role(StrEnum):
    """Papéis disponíveis no sistema com hierarquia."""

    ADMIN = "admin"
    OPERADOR = "operador"
    LEITURA = "leitura"


# Hierarquia de permissões: indivíduos com role anterior herdam permissões posteriores
_ROLE_HIERARCHY = {
    Role.ADMIN: [Role.ADMIN, Role.OPERADOR, Role.LEITURA],
    Role.OPERADOR: [Role.OPERADOR, Role.LEITURA],
    Role.LEITURA: [Role.LEITURA],
}


def require_role(*roles_permitidas: str | Role) -> Callable:
    """Cria uma dependency que verifica se o usuário possui uma das roles permitidas.

    Suporta tanto strings quanto enums de Role.
    Respeita a hierarquia: admin > operador > leitura.

    Uso em rotas:
        @router.post(
            "/produtos",
            dependencies=[Depends(require_role(Role.OPERADOR))]
        )
        def criar_produto(...):
            ...

        @router.delete(
            "/produtos/{id}",
            dependencies=[Depends(require_role(Role.ADMIN))]
        )
        def deletar_produto(...):
            ...

    Args:
        roles_permitidas: Uma ou mais roles que têm acesso ao recurso.
                         Pode ser string ou Role enum.

    Returns:
        Dependency function que valida a role do usuário.

    Raises:
        ForbiddenError: Se o usuário não possuir a role necessária.
    """
    # Normaliza as roles para strings
    roles_normalizadas = set()
    for role in roles_permitidas:
        if isinstance(role, Role):
            roles_normalizadas.add(role.value)
        else:
            roles_normalizadas.add(str(role))

    def _verificar_role(current_user: TokenPayload) -> TokenPayload:
        """Valida se o usuário tem acesso baseado em sua role."""
        user_role = current_user.role

        # Verifica se o role do usuário está na lista de permitidos
        if user_role not in roles_normalizadas:
            raise ForbiddenError(
                message=f"Acesso restrito aos perfis: {', '.join(sorted(roles_normalizadas))}."
            )

        return current_user

    return _verificar_role


def require_role_or_higher(role_minimo: str | Role) -> Callable:
    """Cria uma dependency que verifica se o usuário tem a role ou superior (hierarquia).

    Usa a hierarquia: admin > operador > leitura

    Uso em rotas:
        @router.get(
            "/relatorios",
            dependencies=[Depends(require_role_or_higher(Role.OPERADOR))]
        )
        def gerar_relatorio(...):
            # Permite admin e operador, nega leitura
            ...

    Args:
        role_minimo: Role mínima requerida. Roles superiores também têm acesso.

    Returns:
        Dependency function que valida a role do usuário.

    Raises:
        ForbiddenError: Se o usuário não tiver a role mínima ou superior.
    """
    # Normaliza a role mínima
    role_str = role_minimo.value if isinstance(role_minimo, Role) else str(role_minimo)

    def _verificar_role_hierarquica(current_user: TokenPayload) -> TokenPayload:
        """Valida se o usuário tem a role mínima ou superior."""
        user_role = current_user.role

        # Obtém as roles permitidas para este user
        roles_permitidas = _ROLE_HIERARCHY.get(user_role, [])

        # Verifica se a role mínima está nas roles permitidas do user
        if role_str not in roles_permitidas:
            raise ForbiddenError(
                message=f"Acesso restrito ao perfil '{role_str}' ou superior."
            )

        return current_user

    return _verificar_role_hierarquica


def get_user_roles_hierarchy(user_role: str | Role) -> list[str]:
    """Retorna a lista de roles que um usuário pode acessar (hierarquia).

    Útil para filtrar dados ou verificar permissões de forma mais flexível.

    Args:
        user_role: Role do usuário.

    Returns:
        Lista de roles que o usuário pode acessar.
    """
    role_str = user_role.value if isinstance(user_role, Role) else str(user_role)
    return _ROLE_HIERARCHY.get(role_str, [])
