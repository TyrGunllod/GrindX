from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.gestao_projetos.base import GestaoProjetosBase


class Projeto(GestaoProjetosBase):
    __tablename__ = "projetos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False, index=True, comment="Nome")
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Descricao")
    status: Mapped[str] = mapped_column(String(20), default="planning", nullable=False, comment="Status")
    data_inicio: Mapped[date] = mapped_column(Date, nullable=False, comment="Data de inicio")
    data_fim: Mapped[date] = mapped_column(Date, nullable=False, comment="Data de termino")
    cor: Mapped[str] = mapped_column(String(7), default="#3b82f6", nullable=False, comment="Cor hexadecimal")
    gerente_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("iam.usuarios.id"), nullable=True, comment="ID do gerente")
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="Se esta ativo")
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Projeto(id={self.id}, nome='{self.nome}')>"