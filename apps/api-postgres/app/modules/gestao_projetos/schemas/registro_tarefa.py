from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RegistroCreate(BaseModel):
    tipo: str = Field(default="log", pattern=r"^(log|decisao)$")
    conteudo: str = Field(..., min_length=1, description="Conteudo do registro")
    autor_id: int | None = Field(default=None, description="ID do autor")


class RegistroUpdate(BaseModel):
    tipo: str | None = Field(default=None, pattern=r"^(log|decisao)$")
    conteudo: str | None = Field(default=None, min_length=1)


class RegistroResponse(BaseModel):
    id: int
    tarefa_id: int
    tipo: str
    conteudo: str
    autor_id: int | None
    ativo: bool
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)
