"""Exceções compartilhadas entre as APIs."""

from shared.exceptions.codes import ErrorCode
from shared.exceptions.base import (
    AppException,
    NotFoundError,
    ConflictError,
    BusinessValidationError,
    DatabaseError,
    UnauthorizedError,
    ForbiddenError,
    CredenciaisInvalidasError,
    TokenExpiradoError,
    TokenInvalidoError,
)
