"""
Schemas Pydantic para a entidade Cliente.

Somente schemas de resposta (read-only) — sem Create/Update.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClienteResponse(BaseModel):
    """Schema de resposta com dados do cliente."""

    id: int = Field(..., description="ID do cliente")
    razao_social: str = Field(..., description="Razão social da empresa")
    nome_fantasia: str | None = Field(None, description="Nome fantasia")
    cnpj: str = Field(..., description="CNPJ formatado (XX.XXX.XXX/XXXX-XX)")
    email: str | None = Field(None, description="E-mail de contato")
    telefone: str | None = Field(None, description="Telefone de contato")
    endereco: str | None = Field(None, description="Endereço completo")
    cidade: str | None = Field(None, description="Cidade")
    uf: str | None = Field(None, description="Unidade federativa")
    ativo: bool = Field(..., description="Se o cliente está ativo")
    criado_em: datetime | None = Field(None, description="Data de criação")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "razao_social": "Empresa Exemplo Ltda",
                    "nome_fantasia": "Exemplo",
                    "cnpj": "12.345.678/0001-90",
                    "email": "contato@exemplo.com.br",
                    "telefone": "(11) 99999-0000",
                    "endereco": "Rua Exemplo, 123",
                    "cidade": "São Paulo",
                    "uf": "SP",
                    "ativo": True,
                    "criado_em": "2025-01-01T00:00:00Z",
                }
            ]
        },
    )


class ClienteFiltros(BaseModel):
    """Schema para filtros de busca de clientes."""

    razao_social: str | None = Field(None, description="Filtro por razão social (parcial)")
    cnpj: str | None = Field(None, description="Filtro por CNPJ exato")
    cidade: str | None = Field(None, description="Filtro por cidade")
    uf: str | None = Field(None, description="Filtro por UF")
    apenas_ativos: bool = Field(True, description="Filtrar somente ativos")
