from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TarefaCreate(BaseModel):
    titulo: str = Field(..., min_length=2, max_length=255, description="Titulo")
    descricao: str | None = Field(default=None, description="Descricao")
    status: str = Field(default="todo", pattern=r"^(todo|in-progress|done)$")
    prioridade: str = Field(default="medium", pattern=r"^(low|medium|high)$")
    data_inicio: date = Field(..., description="Data de inicio")
    data_fim: date = Field(..., description="Data de termino")
    progresso: int = Field(default=0, ge=0, le=100, description="Progresso 0-100")
    projeto_id: int | None = Field(default=None, description="ID do projeto")
    responsavel_id: int | None = Field(default=None, description="ID do responsavel")

    @field_validator("data_fim")
    @classmethod
    def validate_data_fim(cls, v: date, info) -> date:
        if "data_inicio" in info.data and v < info.data["data_inicio"]:
            raise ValueError("data_fim deve ser >= data_inicio")
        return v


class TarefaUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=2, max_length=255)
    descricao: str | None = Field(default=None)
    status: str | None = Field(default=None, pattern=r"^(todo|in-progress|done)$")
    prioridade: str | None = Field(default=None, pattern=r"^(low|medium|high)$")
    data_inicio: date | None = Field(default=None)
    data_fim: date | None = Field(default=None)
    progresso: int | None = Field(default=None, ge=0, le=100)
    projeto_id: int | None = Field(default=None)
    responsavel_id: int | None = Field(default=None)


class TarefaResponse(BaseModel):
    id: int
    titulo: str
    descricao: str | None
    status: str
    prioridade: str
    data_inicio: date
    data_fim: date
    progresso: int
    projeto_id: int | None
    responsavel_id: int | None
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)
