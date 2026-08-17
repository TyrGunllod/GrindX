"""Router de auditoria e sessões (somente leitura, acesso admin)."""

import structlog
from fastapi import APIRouter, Depends, Query
from shared.schemas.base import PaginatedResponse
from sqlalchemy.orm import Session

from app.audit.models import AuditLog, Sessao
from app.auth.dependencies import require_role
from app.database import get_db
from app.schemas.audit import AuditLogResponse, SessaoResponse

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/v1/audit", tags=["Auditoria"])


@router.get(
    "/logs",
    response_model=PaginatedResponse[AuditLogResponse],
    summary="Listar logs de auditoria",
    description="Lista os logs de alterações no banco. Acesso: admin.",
)
def listar_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: None = Depends(require_role("admin")),
):
    """Lista os logs de auditoria (mais recentes primeiro)."""
    total = db.query(AuditLog).count()
    items = (
        db.query(AuditLog)
        .order_by(AuditLog.criado_em.desc(), AuditLog.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get(
    "/sessoes",
    response_model=PaginatedResponse[SessaoResponse],
    summary="Listar sessões de uso",
    description="Lista os logins/logouts dos usuários. Acesso: admin.",
)
def listar_sessoes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: None = Depends(require_role("admin")),
):
    """Lista as sessões de uso (mais recentes primeiro)."""
    total = db.query(Sessao).count()
    items = (
        db.query(Sessao)
        .order_by(Sessao.login_at.desc(), Sessao.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )
