from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    event,
    func,
    text,
)
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.modules.org.base import OrgBase

if TYPE_CHECKING:
    from app.modules.org.models.empresa import Empresa


@event.listens_for(Session, "before_flush")
def _deactivate_other_themes(session, flush_context, instances):
    for obj in list(session.new) + list(session.dirty):
        if isinstance(obj, CompanyTheme) and obj.is_active:
            query = session.query(CompanyTheme).filter(
                CompanyTheme.company_id == obj.company_id,
                CompanyTheme.is_active.is_(True),
            )
            if obj.id is not None:
                query = query.filter(CompanyTheme.id != obj.id)
            query.update({"is_active": False}, synchronize_session="fetch")


class CompanyTheme(OrgBase):
    __tablename__ = "company_themes"

    __table_args__ = (
        Index(
            "ix_company_themes_company_active",
            "company_id",
            "is_active",
        ),
        {"schema": "org"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("org.empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Nome da skin"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Skin ativa"
    )
    colors: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="Overrides de cores"
    )
    fonts: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="Overrides de fontes"
    )
    icon_library: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'fontawesome'"),
        comment="Biblioteca de ícones",
    )
    tokens: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="Tokens extras (radius, shadows)"
    )
    logo_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="URL do logo"
    )
    logo_short_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="URL do logo curto"
    )
    company_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Nome exibido no sistema"
    )
    copyright_text: Mapped[str | None] = mapped_column(
        String(200), nullable=True, comment="Texto do rodapé"
    )
    layout_mode: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'topbar'"),
        comment="Modo de layout: 'sidebar' ou 'topbar'",
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

    company: Mapped["Empresa"] = relationship(back_populates="themes")

    def __repr__(self) -> str:
        return f"<CompanyTheme(id={self.id}, company_id={self.company_id}, name='{self.name}')>"
