from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class {entity_name}Create(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100, description="Nome")


class {entity_name}Update(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=100)


class {entity_name}Response(BaseModel):
    id: int
    nome: str
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)


# === Optional validators (uncomment as needed) ===

# from pydantic import field_validator

# @field_validator("email")
# @classmethod
# def validate_email(cls, v: str) -> str:
#     if "@" not in v:
#         raise ValueError("Email inválido")
#     return v
