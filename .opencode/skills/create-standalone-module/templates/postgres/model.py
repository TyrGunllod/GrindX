from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.{module_name}.base import {entity_name}Base


class {entity_name}({entity_name}Base):
    __tablename__ = "{table_name}"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, comment="Nome"
    )
    ativo: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="Se está ativo"
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<{entity_name}(id={self.id}, nome='{self.nome}')>"


# === Optional extras (uncomment as needed) ===

# from sqlalchemy import ForeignKey, UniqueConstraint

# FK example:
# user_id: Mapped[int] = mapped_column(
#     ForeignKey("iam.usuarios.id"), nullable=False
# )

# UniqueConstraint example:
# __table_args__ = (
#     UniqueConstraint("user_id", "projeto_id", name="uq_{module_name}_user_projeto"),
# )
