from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Aba(Base):
    """Representa uma seção/categoria no menu lateral (ex: Cadastro, Estoque)."""

    __tablename__ = "portal_abas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False)
    icone = Column(String(50), nullable=True)  # Classe FontAwesome
    ordem = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
    parent_id = Column(Integer, ForeignKey("portal_abas.id"), nullable=True)

    parent = relationship("Aba", remote_side=[id], back_populates="children")
    children = relationship("Aba", back_populates="parent", cascade="all, delete-orphan")
    modulos = relationship("Modulo", back_populates="aba", cascade="all, delete-orphan")


class Modulo(Base):
    """Representa uma página/funcionalidade standalone (ex: Gerenciamento de Usuários)."""

    __tablename__ = "portal_modulos"

    id = Column(Integer, primary_key=True, index=True)
    aba_id = Column(Integer, ForeignKey("portal_abas.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    slug = Column(
        String(100), unique=True, nullable=False
    )  # Identificador único para a URL
    url = Column(
        String(255), nullable=False
    )  # Caminho do arquivo HTML (ex: /modules/users/index.html)
    icone = Column(String(50), nullable=True)
    role_minima = Column(String(20), default="operador")
    ativo = Column(Boolean, default=True)

    aba = relationship("Aba", back_populates="modulos")
    usuarios_permitidos = relationship(
        "Usuario",
        secondary="usuario_modulos",
        back_populates="modulos_permitidos",
        lazy="select",
        primaryjoin="and_(Modulo.id == UsuarioModulo.modulo_id)",
        secondaryjoin="UsuarioModulo.usuario_id == Usuario.id",
    )
