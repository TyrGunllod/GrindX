"""
Testes unitários para o sistema de permissões RBAC.

Testa require_role, require_role_or_higher e a hierarquia de permissões.
Usa mocks para não depender de HTTP real.
"""

import pytest
from shared.exceptions.base import ForbiddenError
from shared.schemas.auth import TokenPayload
from shared.security.permissions import (
    Role,
    get_user_roles_hierarchy,
    require_role,
    require_role_or_higher,
)


class TestRoleEnum:
    """Testes da enumeração Role."""

    def test_role_valores(self):
        """Testa que os valores de Role são corretos."""
        assert Role.ADMIN.value == "admin"
        assert Role.OPERADOR.value == "operador"
        assert Role.LEITURA.value == "leitura"

    def test_role_string_conversion(self):
        """Testa conversão de Role para string."""
        assert str(Role.ADMIN) == "admin"
        assert str(Role.OPERADOR) == "operador"
        assert str(Role.LEITURA) == "leitura"


class TestRequireRole:
    """Testes do decorator require_role."""

    def test_require_role_admin_acessa_admin_permitido(self):
        """Testa que admin consegue acessar rota com require_role(admin)."""
        dependency = require_role(Role.ADMIN)
        current_user = TokenPayload(sub="1", role="admin")

        resultado = dependency(current_user)

        assert resultado.role == "admin"

    def test_require_role_operador_acessa_operador_permitido(self):
        """Testa que operador consegue acessar rota com require_role(operador)."""
        dependency = require_role(Role.OPERADOR)
        current_user = TokenPayload(sub="1", role="operador")

        resultado = dependency(current_user)

        assert resultado.role == "operador"

    def test_require_role_leitura_acessa_leitura_permitido(self):
        """Testa que leitura consegue acessar rota com require_role(leitura)."""
        dependency = require_role(Role.LEITURA)
        current_user = TokenPayload(sub="1", role="leitura")

        resultado = dependency(current_user)

        assert resultado.role == "leitura"

    def test_require_role_leitura_nao_acessa_admin(self):
        """Testa que leitura NÃO consegue acessar rota com require_role(admin)."""
        dependency = require_role(Role.ADMIN)
        current_user = TokenPayload(sub="1", role="leitura")

        with pytest.raises(ForbiddenError) as exc_info:
            dependency(current_user)

        assert "admin" in str(exc_info.value.message).lower()

    def test_require_role_operador_nao_acessa_admin(self):
        """Testa que operador NÃO consegue acessar rota com require_role(admin)."""
        dependency = require_role(Role.ADMIN)
        current_user = TokenPayload(sub="1", role="operador")

        with pytest.raises(ForbiddenError):
            dependency(current_user)

    def test_require_role_multiplas_roles_permitidas(self):
        """Testa que múltiplas roles permitidas funcionam."""
        dependency = require_role(Role.ADMIN, Role.OPERADOR)

        # Admin deve passar
        current_admin = TokenPayload(sub="1", role="admin")
        assert dependency(current_admin).role == "admin"

        # Operador deve passar
        current_operador = TokenPayload(sub="2", role="operador")
        assert dependency(current_operador).role == "operador"

        # Leitura deve falhar
        current_leitura = TokenPayload(sub="3", role="leitura")
        with pytest.raises(ForbiddenError):
            dependency(current_leitura)

    def test_require_role_com_string_role(self):
        """Testa que require_role funciona com strings (não só enums)."""
        dependency = require_role("admin", "operador")
        current_user = TokenPayload(sub="1", role="admin")

        resultado = dependency(current_user)

        assert resultado.role == "admin"

    def test_require_role_com_string_do_user_role(self):
        """Testa que user_role como string funciona."""
        dependency = require_role(Role.ADMIN)
        current_user = TokenPayload(sub="1", role="admin")  # string

        resultado = dependency(current_user)

        assert resultado.role == "admin"

    def test_require_role_mensagem_erro_clara(self):
        """Testa que mensagem de erro lista as roles permitidas."""
        dependency = require_role(Role.ADMIN, Role.OPERADOR)
        current_user = TokenPayload(sub="1", role="leitura")

        with pytest.raises(ForbiddenError) as exc_info:
            dependency(current_user)

        message = str(exc_info.value.message).lower()
        assert "admin" in message
        assert "operador" in message


class TestRequireRoleOrHigher:
    """Testes do decorator require_role_or_higher com hierarquia."""

    def test_admin_acessa_admin_ou_superior(self):
        """Testa que admin consegue acessar require_role_or_higher(admin)."""
        dependency = require_role_or_higher(Role.ADMIN)
        current_user = TokenPayload(sub="1", role="admin")

        resultado = dependency(current_user)

        assert resultado.role == "admin"

    def test_admin_acessa_operador_ou_superior(self):
        """Testa que admin consegue acessar require_role_or_higher(operador)."""
        dependency = require_role_or_higher(Role.OPERADOR)
        current_user = TokenPayload(sub="1", role="admin")

        resultado = dependency(current_user)

        assert resultado.role == "admin"

    def test_operador_acessa_operador_ou_superior(self):
        """Testa que operador consegue acessar require_role_or_higher(operador)."""
        dependency = require_role_or_higher(Role.OPERADOR)
        current_user = TokenPayload(sub="1", role="operador")

        resultado = dependency(current_user)

        assert resultado.role == "operador"

    def test_operador_acessa_leitura_ou_superior(self):
        """Testa que operador consegue acessar require_role_or_higher(leitura)."""
        dependency = require_role_or_higher(Role.LEITURA)
        current_user = TokenPayload(sub="1", role="operador")

        resultado = dependency(current_user)

        assert resultado.role == "operador"

    def test_leitura_nao_acessa_operador_ou_superior(self):
        """Testa que leitura NÃO consegue acessar require_role_or_higher(operador)."""
        dependency = require_role_or_higher(Role.OPERADOR)
        current_user = TokenPayload(sub="1", role="leitura")

        with pytest.raises(ForbiddenError):
            dependency(current_user)

    def test_leitura_nao_acessa_admin_ou_superior(self):
        """Testa que leitura NÃO consegue acessar require_role_or_higher(admin)."""
        dependency = require_role_or_higher(Role.ADMIN)
        current_user = TokenPayload(sub="1", role="leitura")

        with pytest.raises(ForbiddenError):
            dependency(current_user)

    def test_require_role_or_higher_com_string(self):
        """Testa que require_role_or_higher funciona com strings."""
        dependency = require_role_or_higher("operador")
        current_user = TokenPayload(sub="1", role="admin")

        resultado = dependency(current_user)

        assert resultado.role == "admin"


class TestGetUserRolesHierarchy:
    """Testes da função get_user_roles_hierarchy."""

    def test_admin_tem_todas_as_roles(self):
        """Testa que admin consegue acessar todas as roles."""
        roles = get_user_roles_hierarchy(Role.ADMIN)

        assert "admin" in roles
        assert "operador" in roles
        assert "leitura" in roles
        assert len(roles) == 3

    def test_operador_tem_operador_e_leitura(self):
        """Testa que operador consegue acessar operador e leitura."""
        roles = get_user_roles_hierarchy(Role.OPERADOR)

        assert "operador" in roles
        assert "leitura" in roles
        assert "admin" not in roles
        assert len(roles) == 2

    def test_leitura_tem_somente_leitura(self):
        """Testa que leitura consegue acessar somente leitura."""
        roles = get_user_roles_hierarchy(Role.LEITURA)

        assert "leitura" in roles
        assert "operador" not in roles
        assert "admin" not in roles
        assert len(roles) == 1

    def test_get_user_roles_com_string(self):
        """Testa que get_user_roles_hierarchy funciona com strings."""
        roles = get_user_roles_hierarchy("admin")

        assert "admin" in roles
        assert "operador" in roles
        assert "leitura" in roles

    def test_role_invalida_retorna_lista_vazia(self):
        """Testa que role inválida retorna lista vazia."""
        roles = get_user_roles_hierarchy("role_inexistente")

        assert roles == []


class TestHierarquiaPermissoes:
    """Testes da lógica de hierarquia de permissões."""

    def test_hierarquia_ordem_correta(self):
        """Testa que a hierarquia segue a ordem: admin > operador > leitura."""
        admin_roles = get_user_roles_hierarchy("admin")
        operador_roles = get_user_roles_hierarchy("operador")
        leitura_roles = get_user_roles_hierarchy("leitura")

        # Admin tem mais permissions que operador
        assert len(admin_roles) > len(operador_roles)

        # Operador tem mais permissions que leitura
        assert len(operador_roles) > len(leitura_roles)

        # Leitura tem pelo menos leitura
        assert len(leitura_roles) >= 1

    def test_admin_herda_todas_permissoes(self):
        """Testa que admin herda todas as permissões inferiores."""
        admin_roles = set(get_user_roles_hierarchy("admin"))
        operador_roles = set(get_user_roles_hierarchy("operador"))
        leitura_roles = set(get_user_roles_hierarchy("leitura"))

        # Admin contém todas as roles de operador
        assert operador_roles.issubset(admin_roles)

        # Operador contém todas as roles de leitura
        assert leitura_roles.issubset(operador_roles)

    def test_operador_herda_leitura(self):
        """Testa que operador herda permissions de leitura."""
        operador_roles = set(get_user_roles_hierarchy("operador"))
        leitura_roles = set(get_user_roles_hierarchy("leitura"))

        assert leitura_roles.issubset(operador_roles)
