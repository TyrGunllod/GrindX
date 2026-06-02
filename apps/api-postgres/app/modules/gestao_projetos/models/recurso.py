from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.gestao_projetos.base import GestaoProjetosBase


class Recurso(GestaoProjetosBase):
    __tablename__ = "recursos"

    __table_args__ = (
        UniqueConstraint("user_id", "projeto_id", name="uq_recurso_user_projeto"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("iam.usuarios.id"), nullable=False, comment="FK para usuario do IAM",
    )
    projeto_id: Mapped[int] = mapped_column(nullable=False, comment="ID do projeto")
    cargo_contexto: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Cargo/funcao no contexto do projeto")
    cor: Mapped[str] = mapped_column(String(7), default="#3b82f6", nullable=False, comment="Cor de identificacao visual")
    alocado: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="Se esta ativamente alocado")
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Recurso(id={self.id}, user_id={self.user_id}, projeto_id={self.projeto_id})>"