from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.gestao_projetos.base import GestaoProjetosBase


class Tarefa(GestaoProjetosBase):
    __tablename__ = "tarefas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False, index=True, comment="Titulo da tarefa")
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Descricao detalhada")
    status: Mapped[str] = mapped_column(String(20), default="todo", nullable=False, comment="todo | in-progress | done")
    prioridade: Mapped[str] = mapped_column(String(10), default="medium", nullable=False, comment="low | medium | high")
    data_inicio: Mapped[date] = mapped_column(Date, nullable=False, comment="Data de inicio")
    data_fim: Mapped[date] = mapped_column(Date, nullable=False, comment="Data de termino")
    progresso: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="Progresso 0-100")
    projeto_id: Mapped[int | None] = mapped_column(
        ForeignKey("org.projetos.id", ondelete="CASCADE"),
        nullable=True, index=True, comment="FK para projetos",
    )
    responsavel_id: Mapped[int | None] = mapped_column(
        ForeignKey("org.recursos.id", ondelete="SET NULL", use_alter=True),
        nullable=True, index=True, comment="FK para recursos (responsavel)",
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="Se esta ativo")
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Tarefa(id={self.id}, titulo='{self.titulo}', status='{self.status}')>"