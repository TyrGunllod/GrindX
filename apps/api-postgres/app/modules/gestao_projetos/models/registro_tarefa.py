from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.gestao_projetos.base import GestaoProjetosBase


class RegistroTarefa(GestaoProjetosBase):
    __tablename__ = "registros_tarefas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tarefa_id: Mapped[int] = mapped_column(
        ForeignKey("org.tarefas.id", ondelete="CASCADE"),
        nullable=False, index=True, comment="FK para tarefas",
    )
    tipo: Mapped[str] = mapped_column(String(20), default="log", nullable=False, comment="log | decisao")
    conteudo: Mapped[str] = mapped_column(Text, nullable=False, comment="Conteudo do registro")
    autor_id: Mapped[int | None] = mapped_column(
        ForeignKey("org.recursos.id", ondelete="SET NULL"),
        nullable=True, index=True, comment="FK para recursos (autor)",
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="Se esta ativo")
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<RegistroTarefa(id={self.id}, tarefa_id={self.tarefa_id}, tipo='{self.tipo}')>"