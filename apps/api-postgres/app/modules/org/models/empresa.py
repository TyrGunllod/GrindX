from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.org.base import OrgBase

if TYPE_CHECKING:
    from app.modules.org.models.theme import CompanyTheme


class Empresa(OrgBase):
    __tablename__ = "empresas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Nome da empresa"
    )
    dominio: Mapped[str | None] = mapped_column(
        String(255), nullable=True, unique=True, comment="Domínio/subdomínio da empresa"
    )
    ativo: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="Se a empresa está ativa"
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    themes: Mapped[list["CompanyTheme"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Empresa(id={self.id}, nome='{self.nome}')>"
