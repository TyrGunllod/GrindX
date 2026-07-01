from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.iam.base import IamBase
from app.modules.portal.models.portal import Modulo


class Usuario(IamBase):
    __tablename__ = "usuarios"

    __table_args__ = (
        Index("ix_usuarios_role", "role"),
        Index("ix_usuarios_ativo", "ativo"),
        Index("ix_usuarios_empresa_id", "empresa_id"),
        {"schema": "iam"},
    )

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
    temp_password_hash: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Hash bcrypt da senha temporária"
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Expiração da senha temporária"
    )
    theme_preference: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        comment="Preferência de tema: light, dark ou null (sistema)",
    )
    layout_preference: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Preferência de layout: sidebar, topbar ou null (padrão)",
    )
    codigo: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Código do funcionário"
    )
    cbo: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="C.B.O")
    departamento: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Departamento"
    )
    cargo: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Cargo"
    )
    classificacao: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Classificação: Junior, Pleno, Senior, I, II, III, IV, V",
    )
    cpf: Mapped[str | None] = mapped_column(String(14), nullable=True, comment="CPF")
    endereco: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Endereço"
    )
    numero: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="Número do endereço"
    )
    cep: Mapped[str | None] = mapped_column(String(10), nullable=True, comment="CEP")
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
        Integer,
        ForeignKey("org.empresas.id", ondelete="SET NULL"),
        nullable=True,
        comment="Empresa do usuário",
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
        return (
            f"<Usuario(id={self.id}, username='{self.username}', role='{self.role}')>"
        )


class UsuarioModulo(IamBase):
    __tablename__ = "usuario_modulos"

    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("iam.usuarios.id", ondelete="CASCADE"), primary_key=True
    )
    modulo_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("portal.portal_modulos.id", ondelete="CASCADE"),
        primary_key=True,
    )
    concedido_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    concedido_por_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("iam.usuarios.id", ondelete="SET NULL"), nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"<UsuarioModulo(usuario_id={self.usuario_id}, modulo_id={self.modulo_id})>"
        )


# Relationships must be defined after all model classes exist
# to avoid circular import between iam and portal modules
Usuario.modulos_permitidos = relationship(
    Modulo,
    secondary=UsuarioModulo.__table__,
    back_populates="usuarios_permitidos",
    lazy="select",
    primaryjoin=Usuario.id == UsuarioModulo.__table__.c.usuario_id,
    secondaryjoin=UsuarioModulo.__table__.c.modulo_id == Modulo.id,
)

Modulo.usuarios_permitidos = relationship(
    Usuario,
    secondary=UsuarioModulo.__table__,
    back_populates="modulos_permitidos",
    lazy="select",
    primaryjoin=Modulo.id == UsuarioModulo.__table__.c.modulo_id,
    secondaryjoin=UsuarioModulo.__table__.c.usuario_id == Usuario.id,
)
