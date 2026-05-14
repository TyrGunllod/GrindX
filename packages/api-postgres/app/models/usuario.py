"""
Modelo SQLAlchemy para a entidade Usuario.

Tabela: usuarios (PostgreSQL)
Centraliza a autenticação para ambas as APIs.
"""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Usuario(Base):
    """Mapeamento da tabela 'usuarios' no PostgreSQL."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True, comment="Login do usuário"
    )
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, comment="E-mail do usuário"
    )
    nome_completo: Mapped[str] = mapped_column(
        String(150), nullable=False, comment="Nome completo do usuário"
    )
    senha_hash: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Hash bcrypt da senha"
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="leitura",
        comment="Perfil de acesso: admin, operador, leitura",
    )
    ativo: Mapped[bool] = mapped_column(
        default=True, nullable=False, comment="Se o usuário está ativo"
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, username='{self.username}', role='{self.role}')>"
