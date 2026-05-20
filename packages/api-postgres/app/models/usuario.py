"""
Modelo SQLAlchemy para a entidade Usuario.

Tabela: usuarios (PostgreSQL)
Centraliza a autenticação para ambas as APIs.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.portal import Modulo


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
    empresa_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("empresas.id", ondelete="SET NULL"), nullable=True, comment="Empresa do usuário"
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

    modulos_permitidos: Mapped[list["Modulo"]] = relationship(
        "Modulo",
        secondary="usuario_modulos",
        back_populates="usuarios_permitidos",
        lazy="select",
        primaryjoin="and_(Usuario.id == UsuarioModulo.usuario_id)",
        secondaryjoin="UsuarioModulo.modulo_id == Modulo.id"
    )

    def __repr__(self) -> str:
        return (
            f"<Usuario(id={self.id}, username='{self.username}', role='{self.role}')>"
        )


class UsuarioModulo(Base):
    """Tabela de associação entre usuários e módulos do portal.

    Controla quais módulos cada usuário (não-admin) tem permissão de acessar.
    Admins ignoram esta tabela e veem tudo.
    """

    __tablename__ = "usuario_modulos"

    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True
    )
    modulo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("portal_modulos.id", ondelete="CASCADE"), primary_key=True
    )
    concedido_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    concedido_por_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )

    def __repr__(self) -> str:
        return f"<UsuarioModulo(usuario_id={self.usuario_id}, modulo_id={self.modulo_id})>"
