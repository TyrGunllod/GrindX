"""Exceções compartilhadas entre as APIs."""

from shared.exceptions.base import (
    AppException,
    BusinessValidationError,
    ConflictError,
    CredenciaisInvalidasError,
    DatabaseError,
    ForbiddenError,
    NotFoundError,
    TokenExpiradoError,
    TokenInvalidoError,
    UnauthorizedError,
)
from shared.exceptions.codes import ErrorCode

__all__ = [
    "AppException",
    "BusinessValidationError",
    "CredenciaisInvalidasError",
    "ConflictError",
    "DatabaseError",
    "ErrorCode",
    "ForbiddenError",
    "NotFoundError",
    "TokenExpiradoError",
    "TokenInvalidoError",
    "UnauthorizedError",
]
