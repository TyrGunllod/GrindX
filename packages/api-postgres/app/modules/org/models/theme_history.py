from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.org.base import OrgBase


class ThemeHistory(OrgBase):
    __tablename__ = "theme_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    theme_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("org.company_themes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    action: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    performed_by: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="ID do usuário que executou a ação"
    )
    theme_snapshot: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="Snapshot completo do tema após a ação"
    )
    changes: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="Diff das alterações (apenas para updates)"
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ThemeHistory(id={self.id}, theme_id={self.theme_id}, action='{self.action}', criado_em='{self.criado_em}')>"
