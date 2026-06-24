"""
Testes unitários do pacote shared a partir da raiz do projeto.

Valida que os módulos compartilhados estão acessíveis e funcionais
quando importados do nível do monorepo.
"""

import sys
from pathlib import Path

_packages_dir = str(Path(__file__).resolve().parent.parent.parent / "packages")
if _packages_dir not in sys.path:
    sys.path.insert(0, _packages_dir)


class TestSharedSecurity:
    """Testes do módulo shared.security."""

    def test_import_jwt_functions(self):
        """Testa que funções JWT podem ser importadas."""
        from shared.security.jwt import (
            criar_jwt,
            gerar_hash_senha,
            verificar_jwt,
            verificar_senha,
        )

        assert callable(criar_jwt)
        assert callable(verificar_jwt)
        assert callable(gerar_hash_senha)
        assert callable(verificar_senha)

    def test_import_permissions(self):
        """Testa que funções de permissão podem ser importadas."""
        from shared.security.permissions import (
            Role,
            require_role,
            require_role_or_higher,
        )

        assert callable(require_role)
        assert callable(require_role_or_higher)
        assert Role is not None


class TestSharedSchemas:
    """Testes do módulo shared.schemas."""

    def test_import_token_payload(self):
        """Testa que TokenPayload pode ser importado."""
        from shared.schemas.auth import TokenPayload

        payload = TokenPayload(sub="1", role="admin")
        assert payload.sub == "1"
        assert payload.role == "admin"

    def test_import_error_response(self):
        """Testa que ErrorResponse pode ser importado."""
        from shared.schemas.base import ErrorResponse

        error = ErrorResponse(error="TESTE", message="Erro de teste", status_code=500)
        assert error.error == "TESTE"
        assert error.message == "Erro de teste"
        assert error.status_code == 500

    def test_import_health_check_response(self):
        """Testa que HealthCheckResponse pode ser importado."""
        from shared.schemas.base import HealthCheckResponse

        health = HealthCheckResponse(
            status="healthy",
            service="test",
            version="1.0.0",
            database={"postgres": "connected"},
        )
        assert health.status == "healthy"

    def test_import_message_response(self):
        """Testa que MessageResponse pode ser importado."""
        from shared.schemas.base import MessageResponse

        msg = MessageResponse(message="Operação realizada com sucesso.")
        assert msg.message == "Operação realizada com sucesso."


class TestSharedExceptions:
    """Testes do módulo shared.exceptions."""

    def test_import_base_exceptions(self):
        """Testa que exceções base podem ser importadas."""
        from shared.exceptions.base import (
            AppException,
            BusinessValidationError,
            ConflictError,
            ForbiddenError,
            NotFoundError,
            UnauthorizedError,
        )

        assert issubclass(AppException, Exception)
        assert issubclass(NotFoundError, AppException)
        assert issubclass(ConflictError, AppException)
        assert issubclass(BusinessValidationError, AppException)
        assert issubclass(UnauthorizedError, AppException)
        assert issubclass(ForbiddenError, AppException)

    def test_not_found_error(self):
        """Testa que NotFoundError funciona corretamente."""
        from shared.exceptions.base import NotFoundError

        exc = NotFoundError(resource="Produto", identifier=123)
        assert exc.status_code == 404
        assert "PRODUTO" in exc.error_code
        assert "123" in exc.message

    def test_forbidden_error(self):
        """Testa que ForbiddenError funciona corretamente."""
        from shared.exceptions.base import ForbiddenError

        exc = ForbiddenError("Acesso negado ao recurso.")
        assert exc.status_code == 403
        assert "Acesso negado" in exc.message

    def test_token_errors(self):
        """Testa que exceções de token funcionam corretamente."""
        from shared.exceptions.base import TokenExpiradoError, TokenInvalidoError

        exc_expirado = TokenExpiradoError()
        assert exc_expirado.status_code == 401
        assert "expirado" in exc_expirado.message.lower()

        exc_invalido = TokenInvalidoError()
        assert exc_invalido.status_code == 401
        assert "inválido" in exc_invalido.message.lower()

    def test_domain_exceptions(self):
        """Testa exceções de domínio específicas."""
        from shared.exceptions.base import (
            ClienteNaoEncontradoError,
            PrecoInvalidoError,
            ProdutoNaoEncontradoError,
        )

        exc_produto = ProdutoNaoEncontradoError(produto_id=42)
        assert exc_produto.status_code == 404
        assert "PRODUTO" in exc_produto.error_code

        exc_preco = PrecoInvalidoError()
        assert exc_preco.status_code == 422

        exc_cliente = ClienteNaoEncontradoError(cliente_id=99)
        assert exc_cliente.status_code == 404
        assert "CLIENTE" in exc_cliente.error_code
