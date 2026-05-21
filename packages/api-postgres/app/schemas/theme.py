"""Schemas para o CRUD de temas/skins."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ThemeCreate(BaseModel):
    """Schema para criação de tema."""

    name: str = Field(..., min_length=1, max_length=100, description="Nome da skin")
    colors: Optional[dict] = Field(default=None, description="Overrides de cores")
    fonts: Optional[dict] = Field(default=None, description="Overrides de fontes")
    icon_library: str = Field(default="fontawesome", description="Biblioteca de ícones")
    tokens: Optional[dict] = Field(default=None, description="Tokens extras")
    logo_url: Optional[str] = Field(
        default=None, max_length=500, description="URL do logo"
    )
    logo_short_url: Optional[str] = Field(
        default=None, max_length=500, description="URL do logo curto"
    )
    company_name: Optional[str] = Field(
        default=None, max_length=100, description="Nome exibido no sistema"
    )
    copyright_text: Optional[str] = Field(
        default=None, max_length=200, description="Texto do rodapé"
    )


class ThemeUpdate(BaseModel):
    """Schema para atualização de tema (todos opcionais)."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    colors: Optional[dict] = None
    fonts: Optional[dict] = None
    icon_library: Optional[str] = None
    tokens: Optional[dict] = None
    logo_url: Optional[str] = Field(default=None, max_length=500)
    logo_short_url: Optional[str] = Field(default=None, max_length=500)
    company_name: Optional[str] = Field(default=None, max_length=100)
    copyright_text: Optional[str] = Field(default=None, max_length=200)


class ThemeResponse(BaseModel):
    """Schema de resposta para tema."""

    id: int
    company_id: int
    name: str
    is_active: bool
    colors: dict | None = None
    fonts: dict | None = None
    icon_library: str
    tokens: dict | None = None
    logo_url: str | None = None
    logo_short_url: str | None = None
    company_name: str | None = None
    copyright_text: str | None = None
    criado_em: datetime | None = None
    atualizado_em: datetime | None = None

    class Config:
        from_attributes = True
