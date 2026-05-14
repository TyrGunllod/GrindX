"""
Schemas de autenticação compartilhados entre as APIs.

Define contratos para tokens JWT e dados de usuário.
"""

from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    """Schema para requisição de autenticação."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Nome de usuário",
        json_schema_extra={"examples": ["admin"]},
    )
    password: str = Field(
        ...,
        min_length=6,
        description="Senha do usuário",
        json_schema_extra={"examples": ["senha_segura_123"]},
    )


class TokenResponse(BaseModel):
    """Schema para resposta com tokens JWT."""

    access_token: str = Field(..., description="Token de acesso JWT")
    refresh_token: str = Field(..., description="Token de refresh JWT")
    token_type: str = Field(
        default="bearer",
        description="Tipo do token",
    )


class RefreshTokenRequest(BaseModel):
    """Schema para requisição de refresh do token."""

    refresh_token: str = Field(
        ...,
        description="Token de refresh válido",
    )


class TokenPayload(BaseModel):
    """Schema interno representando o payload decodificado do JWT."""

    sub: str = Field(..., description="ID do usuário (subject)")
    role: str = Field(..., description="Role do usuário")
    exp: int | None = Field(default=None, description="Timestamp de expiração")
