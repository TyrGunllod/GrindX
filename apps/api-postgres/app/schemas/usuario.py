from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UsuarioBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    nome_completo: str = Field(..., min_length=2, max_length=100)
    role: str = Field(default="leitura")
    ativo: bool = True


class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6)


class UsuarioUpdate(BaseModel):
    nome_completo: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    ativo: Optional[bool] = None
    password: Optional[str] = None
    theme_preference: Optional[str] = None
    layout_preference: Optional[str] = None
    codigo: Optional[str] = None
    cbo: Optional[str] = None
    departamento: Optional[str] = None
    cargo: Optional[str] = None
    classificacao: Optional[str] = None
    cpf: Optional[str] = None
    endereco: Optional[str] = None
    numero: Optional[str] = None
    cep: Optional[str] = None
    telefone: Optional[str] = None
    celular: Optional[str] = None


class UsuarioResponse(UsuarioBase):
    id: int
    theme_preference: Optional[str] = None
    layout_preference: Optional[str] = None
    codigo: Optional[str] = None
    cbo: Optional[str] = None
    departamento: Optional[str] = None
    cargo: Optional[str] = None
    classificacao: Optional[str] = None
    cpf: Optional[str] = None
    endereco: Optional[str] = None
    numero: Optional[str] = None
    cep: Optional[str] = None
    telefone: Optional[str] = None
    celular: Optional[str] = None
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True


class UsuarioModulosUpdate(BaseModel):
    modulo_ids: list[int]


class UsuarioModulosResponse(BaseModel):
    usuario_id: int
    modulos: list[int]


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)


class ForgotPasswordRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
