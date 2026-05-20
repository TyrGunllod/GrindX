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


def require_role(
    *roles_permitidas: str | Role, get_user: Callable | None = None
) -> Callable:
    """Cria uma dependency que verifica se o usuário possui uma das roles permitidas.

    Se get_user for fornecido, a função retornada será uma dependência FastAPI completa.
    Caso contrário, ela espera receber o current_user como argumento (útil para composição).

    Args:
        roles_permitidas: Uma ou mais roles que têm acesso ao recurso.
        get_user: Função de dependência que retorna o TokenPayload (ex: get_current_user).

    Returns:
        Dependency function que valida a role do usuário.
    """
    # Normaliza as roles para strings
    roles_normalizadas = set()
    for role in roles_permitidas:
        if isinstance(role, Role):
            roles_normalizadas.add(role.value)
        else:
            roles_normalizadas.add(str(role))

    # Define a função de verificação
    def _verificar_role(
        current_user: TokenPayload = Depends(get_user) if get_user else None,
    ) -> TokenPayload:
        """Valida se o usuário tem acesso baseado em sua role."""
        # Se current_user não foi injetado (get_user=None), assumimos que virá por argumento
        if current_user is None:
            raise RuntimeError(
                "require_role deve ser chamado com get_user ou o current_user deve ser passado manualmente."
            )

        user_role = current_user.role

        # Verifica se o role do usuário está na lista de permitidos
        if user_role not in roles_normalizadas:
            raise ForbiddenError(
                message=f"Acesso restrito aos perfis: {', '.join(sorted(roles_normalizadas))}."
            )

        return current_user

    return _verificar_role


def require_role_or_higher(
    role_minimo: str | Role, get_user: Callable | None = None
) -> Callable:
    """Cria uma dependency que verifica se o usuário tem a role ou superior (hierarquia)."""
    # Normaliza a role mínima
    role_str = role_minimo.value if isinstance(role_minimo, Role) else str(role_minimo)

    def _verificar_role_hierarquica(
        current_user: TokenPayload = Depends(get_user) if get_user else None,
    ) -> TokenPayload:
        """Valida se o usuário tem a role mínima ou superior."""
        if current_user is None:
            raise RuntimeError(
                "require_role_or_higher deve ser chamado com get_user ou o current_user deve ser passado manualmente."
            )

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
