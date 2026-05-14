"""Utilitários de segurança compartilhados entre as APIs."""

from shared.security.jwt import (
    criar_jwt,
    gerar_hash_senha,
    verificar_jwt,
    verificar_senha,
)
from shared.security.permissions import (
    Role,
    get_user_roles_hierarchy,
    require_role,
    require_role_or_higher,
)

__all__ = [
    # JWT
    "criar_jwt",
    "gerar_hash_senha",
    "verificar_jwt",
    "verificar_senha",
    # Permissions
    "Role",
    "require_role",
    "require_role_or_higher",
    "get_user_roles_hierarchy",
]
