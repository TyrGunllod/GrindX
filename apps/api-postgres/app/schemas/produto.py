"""
Schemas Pydantic para a entidade Produto.

Define os contratos de entrada (Create, Update) e saída (Response)
com validações e exemplos para documentação Swagger.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProdutoCreate(BaseModel):
    """Schema para criação de um novo produto."""

    nome: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nome do produto",
        json_schema_extra={"examples": ["Caneta Esferográfica Azul"]},
    )
    descricao: str | None = Field(
        default=None,
        max_length=500,
        description="Descrição detalhada do produto",
        json_schema_extra={"examples": ["Caneta esferográfica ponta fina, tinta azul"]},
    )
    preco: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=2,
        description="Preço unitário (deve ser maior que zero)",
        json_schema_extra={"examples": [2.50]},
    )
    ativo: bool = Field(
        default=True,
        description="Se o produto está ativo no sistema",
    )

    @field_validator("nome")
    @classmethod
    def nome_nao_pode_ser_vazio(cls, valor: str) -> str:
        """Valida que o nome não é apenas espaços em branco."""
        if not valor.strip():
            raise ValueError("Nome do produto não pode ser vazio.")
        return valor.strip()


class ProdutoUpdate(BaseModel):
    """Schema para atualização parcial de um produto."""

    nome: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Novo nome do produto",
    )
    descricao: str | None = Field(
        default=None,
        max_length=500,
        description="Nova descrição do produto",
    )
    preco: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=10,
        decimal_places=2,
        description="Novo preço unitário",
    )
    ativo: bool | None = Field(
        default=None,
        description="Novo status de ativação",
    )

    @field_validator("nome")
    @classmethod
    def nome_nao_pode_ser_vazio(cls, valor: str | None) -> str | None:
        if valor is not None and not valor.strip():
            raise ValueError("Nome do produto não pode ser vazio.")
        return valor.strip() if valor else valor


class ProdutoResponse(BaseModel):
    """Schema de resposta com dados do produto."""

    id: int = Field(..., description="ID único do produto")
    nome: str = Field(..., description="Nome do produto")
    descricao: str | None = Field(None, description="Descrição do produto")
    preco: Decimal = Field(..., description="Preço unitário")
    ativo: bool = Field(..., description="Se o produto está ativo")
    criado_em: datetime = Field(..., description="Data de criação")
    atualizado_em: datetime = Field(..., description="Data da última atualização")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "nome": "Caneta Esferográfica Azul",
                    "descricao": "Caneta esferográfica ponta fina, tinta azul",
                    "preco": 2.50,
                    "ativo": True,
                    "criado_em": "2025-01-15T10:30:00Z",
                    "atualizado_em": "2025-01-15T10:30:00Z",
                }
            ]
        },
    )
