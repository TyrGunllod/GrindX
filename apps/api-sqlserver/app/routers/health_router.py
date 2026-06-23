"""
Router de health check para a api-sqlserver.
"""

from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends
from shared.schemas.base import HealthCheckResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.core.config import settings
from app.database import get_db

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["Health"])


def check_database_health(db: Session) -> dict:
    """Verifica conectividade com o SQL Server.

    Returns:
        dict com 'status' ('connected' ou 'disconnected') e 'error'.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "connected"}
    except Exception as exc:
        logger.error("Falha na verificação do SQL Server", error=str(exc))
        return {"status": "disconnected", "error": str(exc)}


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="Verifica a saúde do serviço e a conectividade com o SQL Server.",
)
def health_check(db: Session = Depends(get_db)):
    db_result = check_database_health(db)

    if db_result["status"] == "connected":
        logger.info("Health check: healthy")
        return HealthCheckResponse(
            status="healthy",
            service=settings.APP_NAME,
            version=settings.APP_VERSION,
            database={"sqlserver": "connected"},
            timestamp=datetime.now(timezone.utc),
        )

    logger.warning("Health check: degraded", error=db_result.get("error"))
    return JSONResponse(
        status_code=503,
        content=HealthCheckResponse(
            status="degraded",
            service=settings.APP_NAME,
            version=settings.APP_VERSION,
            database={"sqlserver": db_result["status"]},
            timestamp=datetime.now(timezone.utc),
            details={"error": db_result.get("error")},
        ).model_dump(mode="json"),
    )
