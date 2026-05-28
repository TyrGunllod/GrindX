"""
Router de health check para a api-sqlserver.
"""

from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends
from shared.schemas.base import HealthCheckResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import get_db

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="Verifica a saúde do serviço e a conectividade com o SQL Server.",
)
def health_check(db: Session = Depends(get_db)) -> HealthCheckResponse:
    """Retorna o status de saúde do serviço."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("Falha na conexão com o SQL Server", error=str(exc))
        db_status = "disconnected"

    return HealthCheckResponse(
        status="healthy" if db_status == "connected" else "degraded",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        database=db_status,
        timestamp=datetime.now(timezone.utc),
    )
