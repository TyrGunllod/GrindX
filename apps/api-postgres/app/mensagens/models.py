"""Modelos do módulo central de mensagens."""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.org.base import OrgBase


class Mensagem(OrgBase):
    __tablename__ = "mensagens"

    __table_args__ = (
        CheckConstraint(
            "categoria IN ('SISTEMA', 'DIRETA', 'AVISO')",
            name="ck_mensagens_categoria",
        ),
        Index("ix_mensagens_destinatario_id", "destinatario_id", "criado_em"),
        Index("ix_mensagens_resposta_a", "resposta_a_id"),
        {"schema": "org"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resposta_a_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("org.mensagens.id", ondelete="CASCADE"),
        nullable=True,
        comment="Mensagem raiz da thread (NULL para mensagens raiz)",
    )
    remetente_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("iam.usuarios.id", ondelete="SET NULL"),
        nullable=True,
        comment="NULL indica mensagem gerada pelo sistema",
    )
    destinatario_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("iam.usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    categoria: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="DIRETA"
    )
    url_acao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lida_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    arquivada_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<Mensagem(id={self.id}, titulo='{self.titulo}', "
            f"categoria='{self.categoria}')>"
        )


class AnexoMensagem(OrgBase):
    __tablename__ = "anexos_mensagem"

    __table_args__ = (
        Index("ix_anexos_mensagem_mensagem_id", "mensagem_id"),
        {"schema": "org"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    mensagem_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("org.mensagens.id", ondelete="CASCADE"),
        nullable=False,
    )
    nome_arquivo_original: Mapped[str] = mapped_column(String(255), nullable=False)
    caminho: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    tamanho_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<AnexoMensagem(id={self.id}, "
            f"nome='{self.nome_arquivo_original}', size={self.tamanho_bytes})>"
        )
