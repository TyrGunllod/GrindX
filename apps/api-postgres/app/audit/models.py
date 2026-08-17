from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.org.base import OrgBase


class AuditLog(OrgBase):
    __tablename__ = "audit_logs"

    __table_args__ = (
        Index("ix_audit_logs_entidade_id", "entidade", "entidade_id"),
        {"schema": "org"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("iam.usuarios.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    entidade: Mapped[str] = mapped_column(String(100), nullable=False)
    entidade_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    acao: Mapped[str] = mapped_column(String(20), nullable=False)
    campos_alterados: Mapped[list] = mapped_column(JSON, nullable=False)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, entidade='{self.entidade}', acao='{self.acao}')>"


class Sessao(OrgBase):
    __tablename__ = "sessoes"

    __table_args__ = ({"schema": "org"},)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("iam.usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    login_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    logout_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duracao_segundos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    logout_motivo: Mapped[str | None] = mapped_column(String(20), nullable=True)

    def __repr__(self) -> str:
        return f"<Sessao(id={self.id}, user_id={self.user_id}, login_at='{self.login_at}')>"