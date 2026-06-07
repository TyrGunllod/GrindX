"""
Schemas base reutilizáveis em todas as APIs.

Define contratos padrão para respostas, erros e paginação.
"""

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    """Schema padrão para respostas de erro."""

    error: str = Field(
        ...,
        description="Código do erro em UPPER_SNAKE_CASE",
        json_schema_extra={"examples": ["RECURSO_NAO_ENCONTRADO"]},
    )
    message: str = Field(
        ...,
        description="Mensagem legível descrevendo o erro",
        json_schema_extra={"examples": ["O recurso solicitado não foi encontrado."]},
    )
    status_code: int = Field(
        ...,
        description="Código HTTP do erro",
        json_schema_extra={"examples": [404]},
    )
    details: dict[str, Any] | None = Field(
        default=None,
        description="Detalhes adicionais do erro, quando aplicável",
    )


class HealthCheckResponse(BaseModel):
    """Schema para resposta do health check."""

    status: str = Field(
        ...,
        description="Status do serviço",
        json_schema_extra={"examples": ["healthy"]},
    )
    service: str = Field(
        ...,
        description="Nome do serviço",
        json_schema_extra={"examples": ["api-postgres"]},
    )
    version: str = Field(
        ...,
        description="Versão do serviço",
        json_schema_extra={"examples": ["0.1.0"]},
    )
    database: dict[str, Any] = Field(
        ...,
        description="Status detalhado da conexão com o banco de dados",
        json_schema_extra={"examples": [{"postgres": "connected"}]},
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp da verificação",
    )
    details: dict[str, Any] | None = Field(
        default=None,
        description="Detalhes adicionais quando status é degraded",
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Schema genérico para respostas paginadas."""

    items: list[T] = Field(..., description="Lista de itens da página atual")
    total: int = Field(..., description="Total de itens disponíveis", ge=0)
    page: int = Field(..., description="Página atual", ge=1)
    page_size: int = Field(..., description="Itens por página", ge=1, le=100)
    total_pages: int = Field(..., description="Total de páginas disponíveis", ge=0)

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "items": [],
                    "total": 50,
                    "page": 1,
                    "page_size": 20,
                    "total_pages": 3,
                }
            ]
        }
    )


class MessageResponse(BaseModel):
    """Schema para respostas simples com mensagem."""

    message: str = Field(
        ...,
        description="Mensagem da operação",
        json_schema_extra={"examples": ["Operação realizada com sucesso."]},
    )
