"""
Modelo SQLAlchemy para a entidade Cliente.

Tabela: clientes (SQL Server — somente leitura)
Mapeamento de tabela existente no SQL Server na nuvem.
"""

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Cliente(Base):
    """Mapeamento read-only da tabela 'clientes' no SQL Server."""

    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    razao_social: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="Razão social da empresa"
    )
    nome_fantasia: Mapped[str | None] = mapped_column(
        String(200), nullable=True, comment="Nome fantasia"
    )
    cnpj: Mapped[str] = mapped_column(
        String(18), nullable=False, unique=True, index=True, comment="CNPJ formatado"
    )
    email: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="E-mail de contato"
    )
    telefone: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="Telefone de contato"
    )
    endereco: Mapped[str | None] = mapped_column(
        String(300), nullable=True, comment="Endereço completo"
    )
    cidade: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Cidade"
    )
    uf: Mapped[str | None] = mapped_column(String(2), nullable=True, comment="UF")
    ativo: Mapped[bool] = mapped_column(
        default=True, nullable=False, comment="Se o cliente está ativo"
    )
    criado_em: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="Data de criação"
    )

    def __repr__(self) -> str:
        return f"<Cliente(id={self.id}, razao_social='{self.razao_social}', cnpj='{self.cnpj}')>"
