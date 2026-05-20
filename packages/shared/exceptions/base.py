"""
Exceções de domínio compartilhadas entre as APIs.

Hierarquia:
    AppException (base)
    ├── NotFoundError
    ├── ConflictError
    ├── BusinessValidationError
    ├── UnauthorizedError
    ├── ForbiddenError
    └── DatabaseError

    Domínio:
    ├── ProdutoNaoEncontradoError
    ├── PrecoInvalidoError
    ├── ClienteNaoEncontradoError
    ├── CnpjDuplicadoError
    ├── CredenciaisInvalidasError
    └── TokenExpiradoError
"""


class AppException(Exception):
    """Exceção base para todas as exceções de domínio do ERP."""

    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 500,
        details: dict | None = None,
    ) -> None:
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


# =========================================================
# Exceções Genéricas
# =========================================================


class NotFoundError(AppException):
    """Recurso não encontrado."""

    def __init__(
        self, resource: str, identifier: str | int, details: dict | None = None
    ) -> None:
        super().__init__(
            error_code=f"{resource.upper()}_NAO_ENCONTRADO",
            message=f"{resource} com identificador '{identifier}' não foi encontrado.",
            status_code=404,
            details=details,
        )


class ConflictError(AppException):
    """Conflito — recurso já existe ou violação de unicidade."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(
            error_code="CONFLITO",
            message=message,
            status_code=409,
            details=details,
        )


class BusinessValidationError(AppException):
    """Erro de validação de regra de negócio."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(
            error_code="VALIDACAO_NEGOCIO",
            message=message,
            status_code=422,
            details=details,
        )


class DatabaseError(AppException):
    """Erro de comunicação com o banco de dados."""

    def __init__(
        self, message: str = "Erro de comunicação com o banco de dados."
    ) -> None:
        super().__init__(
            error_code="ERRO_BANCO_DADOS",
            message=message,
            status_code=503,
        )


# =========================================================
# Exceções de Autenticação
# =========================================================


class UnauthorizedError(AppException):
    """Credenciais ausentes ou inválidas."""

    def __init__(self, message: str = "Credenciais inválidas.") -> None:
        super().__init__(
            error_code="NAO_AUTORIZADO",
            message=message,
            status_code=401,
        )


class ForbiddenError(AppException):
    """Permissão insuficiente para acessar o recurso."""

    def __init__(self, message: str = "Permissão insuficiente.") -> None:
        super().__init__(
            error_code="ACESSO_NEGADO",
            message=message,
            status_code=403,
        )


class CredenciaisInvalidasError(UnauthorizedError):
    """Username ou senha incorretos."""

    def __init__(self) -> None:
        super().__init__(message="Usuário ou senha incorretos.")


class TokenExpiradoError(UnauthorizedError):
    """Token JWT expirado."""

    def __init__(self) -> None:
        super().__init__(message="Token expirado. Faça login novamente.")


class TokenInvalidoError(UnauthorizedError):
    """Token JWT inválido ou malformado."""

    def __init__(self) -> None:
        super().__init__(message="Token inválido ou malformado.")


# =========================================================
# Exceções de Domínio — Produto
# =========================================================


class ProdutoNaoEncontradoError(NotFoundError):
    """Produto não encontrado pelo ID."""

    def __init__(self, produto_id: int) -> None:
        super().__init__(resource="Produto", identifier=produto_id)


class PrecoInvalidoError(BusinessValidationError):
    """Preço do produto inválido."""

    def __init__(self, message: str = "Preço deve ser maior que zero.") -> None:
        super().__init__(message=message)


# =========================================================
# Exceções de Domínio — Cliente
# =========================================================


class ClienteNaoEncontradoError(NotFoundError):
    """Cliente não encontrado pelo ID."""

    def __init__(self, cliente_id: int) -> None:
        super().__init__(resource="Cliente", identifier=cliente_id)


class CnpjNaoEncontradoError(NotFoundError):
    """Cliente não encontrado pelo CNPJ."""

    def __init__(self, cnpj: str) -> None:
        super().__init__(resource="Cliente", identifier=cnpj)
