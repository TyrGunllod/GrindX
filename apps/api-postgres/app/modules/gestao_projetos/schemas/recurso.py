from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RecursoCreate(BaseModel):
    user_id: int = Field(..., description="ID do usuario IAM")
    projeto_id: int = Field(..., description="ID do projeto")
    cargo_contexto: str | None = Field(default=None, max_length=100, description="Cargo/funcao")
    cor: str = Field(default="#3b82f6", pattern=r"^#[0-9a-fA-F]{6}$", description="Cor hexadecimal")


class RecursoUpdate(BaseModel):
    cargo_contexto: str | None = Field(default=None, max_length=100)
    cor: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")
    alocado: bool | None = Field(default=None)


class RecursoResponse(BaseModel):
    id: int
    user_id: int
    projeto_id: int
    cargo_contexto: str | None
    cor: str
    alocado: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)
