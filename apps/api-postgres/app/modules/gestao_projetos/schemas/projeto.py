from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjetoCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200, description="Nome")
    descricao: str | None = Field(default=None, description="Descricao")
    status: str = Field(default="planning", pattern=r"^(planning|active|completed|on-hold)$")
    data_inicio: date = Field(..., description="Data de inicio")
    data_fim: date = Field(..., description="Data de termino")
    cor: str = Field(default="#3b82f6", min_length=7, max_length=7, description="Cor hexadecimal")
    gerente_id: int | None = Field(default=None, description="ID do gerente")


class ProjetoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=200)
    descricao: str | None = Field(default=None)
    status: str | None = Field(default=None, pattern=r"^(planning|active|completed|on-hold)$")
    data_inicio: date | None = Field(default=None)
    data_fim: date | None = Field(default=None)
    cor: str | None = Field(default=None, min_length=7, max_length=7)
    gerente_id: int | None = Field(default=None)


class ProjetoResponse(BaseModel):
    id: int
    nome: str
    descricao: str | None
    status: str
    data_inicio: date
    data_fim: date
    cor: str
    gerente_id: int | None
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)
