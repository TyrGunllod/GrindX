"""
Modelo SQLAlchemy para a entidade Produto.

Tabela: produtos (PostgreSQL)
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Produto(Base):
    """Mapeamento da tabela 'produtos' no PostgreSQL."""

    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, comment="Nome do produto"
    )
    descricao: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="Descrição detalhada do produto"
    )
    preco: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, comment="Preço unitário"
    )
    ativo: Mapped[bool] = mapped_column(
        default=True, nullable=False, comment="Se o produto está ativo no sistema"
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Data de criação do registro",
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Data da última atualização",
    )

    def __repr__(self) -> str:
        return f"<Produto(id={self.id}, nome='{self.nome}', preco={self.preco})>"
