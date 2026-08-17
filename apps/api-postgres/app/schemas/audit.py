"""Schemas para auditoria de alterações e tempo de uso."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    """Schema de resposta para um log de auditoria."""

    id: int
    user_id: Optional[int] = None
    entidade: str
    entidade_id: Optional[int] = None
    acao: str
    campos_alterados: list
    ip: Optional[str] = None
    criado_em: datetime | None = None

    class Config:
        from_attributes = True


class SessaoResponse(BaseModel):
    """Schema de resposta para uma sessão de uso."""

    id: int
    user_id: int
    login_at: datetime | None = None
    logout_at: Optional[datetime] = None
    duracao_segundos: Optional[int] = None
    ip: Optional[str] = None
    logout_motivo: Optional[str] = None

    class Config:
        from_attributes = True