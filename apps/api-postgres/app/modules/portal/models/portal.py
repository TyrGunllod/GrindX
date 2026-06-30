from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.modules.portal.base import PortalBase


class Aba(PortalBase):
    __tablename__ = "portal_abas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False)
    icone = Column(String(50), nullable=True)
    ordem = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
    parent_id = Column(Integer, ForeignKey("portal.portal_abas.id"), nullable=True)

    parent = relationship("Aba", remote_side=[id], back_populates="children")
    children = relationship("Aba", back_populates="parent", cascade="all")
    modulos = relationship("Modulo", back_populates="aba", cascade="all, delete-orphan", order_by="Modulo.ordem")


class Modulo(PortalBase):
    __tablename__ = "portal_modulos"

    __table_args__ = (
        Index("ix_portal_modulos_aba_id", "aba_id"),
        {"schema": "portal"},
    )

    id = Column(Integer, primary_key=True, index=True)
    aba_id = Column(Integer, ForeignKey("portal.portal_abas.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    url = Column(String(255), nullable=False)
    icone = Column(String(50), nullable=True)
    role_minima = Column(String(20), default="operador")
    ordem = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)

    aba = relationship("Aba", back_populates="modulos")
