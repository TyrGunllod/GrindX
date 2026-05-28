"""
Testes de integração que validam a estrutura de testes dos pacotes.

Garante que os testes de cada pacote estão acessíveis e configurados
corretamente para execução a partir da raiz do monorepo.
"""

import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parent.parent.parent
_packages_dir = str(_root / "packages")
_apps_dir = str(_root / "apps")
if _packages_dir not in sys.path:
    sys.path.insert(0, _packages_dir)
if _apps_dir not in sys.path:
    sys.path.insert(0, _apps_dir)


class TestEstruturaTestes:
    """Valida a estrutura de testes do monorepo."""

    def test_api_postgres_tests_exist(self):
        """Testa que os testes da api-postgres existem."""
        tests_dir = Path(_apps_dir) / "api-postgres" / "tests"
        assert tests_dir.exists()
        assert (tests_dir / "unit").exists()
        assert (tests_dir / "integration").exists()
        assert (tests_dir / "conftest.py").exists()

    def test_api_sqlserver_tests_exist(self):
        """Testa que os testes da api-sqlserver existem."""
        tests_dir = Path(_apps_dir) / "api-sqlserver" / "tests"
        assert tests_dir.exists()
        assert (tests_dir / "unit").exists()
        assert (tests_dir / "integration").exists()
        assert (tests_dir / "conftest.py").exists()

    def test_shared_tests_exist(self):
        """Testa que os testes do shared existem."""
        tests_dir = Path(_packages_dir) / "shared" / "tests"
        assert tests_dir.exists()
        assert (tests_dir / "test_permissions.py").exists()

    def test_root_tests_exist(self):
        """Testa que os testes da raiz existem."""
        root_tests = Path(__file__).resolve().parent.parent
        assert root_tests.exists()
        assert (root_tests / "unit").exists()
        assert (root_tests / "integration").exists()
        assert (root_tests / "conftest.py").exists()


class TestImportsPacotes:
    """Valida que os módulos compartilhados podem ser importados corretamente."""

    def test_import_shared_security(self):
        """Testa que o módulo shared.security pode ser importado."""
        from shared.security.jwt import criar_jwt, verificar_jwt

        assert callable(criar_jwt)
        assert callable(verificar_jwt)

    def test_import_shared_permissions(self):
        """Testa que o módulo shared.permissions pode ser importado."""
        from shared.security.permissions import Role, require_role

        assert Role.ADMIN.value == "admin"
        assert callable(require_role)

    def test_import_shared_schemas(self):
        """Testa que o módulo shared.schemas pode ser importado."""
        from shared.schemas.auth import TokenPayload
        from shared.schemas.base import ErrorResponse, PaginatedResponse

        payload = TokenPayload(sub="1", role="admin")
        assert payload is not None

        error = ErrorResponse(error="TESTE", message="Teste", status_code=500)
        assert error is not None

    def test_import_shared_exceptions(self):
        """Testa que o módulo shared.exceptions pode ser importado."""
        from shared.exceptions.base import (
            AppException,
            NotFoundError,
            ForbiddenError,
            TokenExpiradoError,
        )

        assert AppException is not None
        assert NotFoundError is not None
        assert ForbiddenError is not None
        assert TokenExpiradoError is not None

    def test_jwt_create_and_verify(self):
        """Testa funcionalidade completa de JWT."""
        from datetime import timedelta

        from shared.security.jwt import criar_jwt, verificar_jwt

        secret = "test-secret-for-root-tests"
        token = criar_jwt(
            payload={"sub": "1", "role": "admin"},
            secret_key=secret,
            expira_em=timedelta(minutes=30),
        )

        result = verificar_jwt(token, secret)
        assert result.sub == "1"
        assert result.role == "admin"

    def test_password_hashing(self):
        """Testa funcionalidade de hashing de senha."""
        from shared.security.jwt import gerar_hash_senha, verificar_senha

        senha = "senha_secreta_123"
        hash_senha = gerar_hash_senha(senha)

        assert verificar_senha(senha, hash_senha)
        assert not verificar_senha("senha_errada", hash_senha)
