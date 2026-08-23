"""Router de health check da API do Agente."""

from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import get_db
from app.schemas import HealthResponse

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:  # noqa: BLE001
        logger.error("Falha na verificação do banco", error=str(exc))
        db_status = "disconnected"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        database={"postgres": db_status},
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
