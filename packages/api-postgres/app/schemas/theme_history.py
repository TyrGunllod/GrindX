"""Schemas para histórico de temas/skins."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ThemeHistoryResponse(BaseModel):
    """Schema de resposta para histórico de tema."""

    id: int
    theme_id: int
    company_id: int
    action: str  # created, updated, deleted, activated, deactivated
    performed_by: Optional[int] = None
    theme_snapshot: Optional[dict] = None
    changes: Optional[dict] = None
    criado_em: datetime | None = None

    class Config:
        from_attributes = True