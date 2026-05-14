"""
Handlers globais de exceção registrados no FastAPI.

Converte exceções de domínio em respostas HTTP padronizadas.
Em produção, oculta stack traces de erros internos.
"""

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from shared.exceptions.base import AppException

logger = structlog.get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Registra todos os handlers de exceção no app FastAPI."""

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        """Handler para exceções de domínio do ERP."""
        logger.warning(
            exc.message,
            error_code=exc.error_code,
            status_code=exc.status_code,
            path=str(request.url),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "status_code": exc.status_code,
                **({"details": exc.details} if exc.details else {}),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handler para erros de validação do Pydantic/FastAPI."""
        logger.warning(
            "Erro de validação na requisição",
            path=str(request.url),
            errors=exc.errors(),
        )
        return JSONResponse(
            status_code=422,
            content={
                "error": "ERRO_VALIDACAO",
                "message": "Os dados enviados contêm erros de validação.",
                "status_code": 422,
                "details": {"errors": exc.errors()},
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handler para exceções não tratadas. Oculta detalhes em produção."""
        logger.error(
            "Erro interno não tratado",
            path=str(request.url),
            error_type=type(exc).__name__,
            error_detail=str(exc),
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "ERRO_INTERNO",
                "message": "Ocorreu um erro interno no servidor.",
                "status_code": 500,
            },
        )
