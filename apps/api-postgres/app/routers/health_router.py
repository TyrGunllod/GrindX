"""
Router de health check.

Endpoint público (sem autenticação) para monitoramento
e verificação de saúde do serviço e conexão com o banco.
"""

from datetime import datetime, timezone
from typing import Any

import structlog
from fastapi import APIRouter, Depends
from shared.schemas.base import HealthCheckResponse
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.core.config import settings
from app.database import get_db

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["Health"])

# Tabelas críticas que devem existir para o funcionamento correto
# (schema.table_name format)
_CRITICAL_TABLES = ["iam.usuarios", "org.company_themes", "portal.portal_abas", "org.empresas"]


def check_database_health(db: Session) -> dict[str, Any]:
    """Verifica conectividade com o banco e integridade do schema.

    Returns:
        dict com 'status' ('connected', 'disconnected' ou 'degraded'),
        'missing_tables' (lista de tabelas ausentes) e 'error' (mensagem de erro).
    """
    try:
        # Testa conectividade básica
        db.execute(text("SELECT 1"))

        # Verifica se tabelas críticas existem
        inspector = inspect(db.bind)
        existing_tables = inspector.get_table_names()
        missing_tables = [
            t for t in _CRITICAL_TABLES if t not in existing_tables
        ]

        if missing_tables:
            logger.warning(
                "Tabelas críticas ausentes",
                missing_tables=missing_tables,
            )
            return {
                "status": "degraded",
                "missing_tables": missing_tables,
            }

        return {"status": "connected", "missing_tables": []}

    except Exception as exc:
        logger.error("Falha na verificação do banco", error=str(exc))
        return {"status": "disconnected", "error": str(exc)}


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="Verifica a saúde do serviço e a conectividade com o banco PostgreSQL.",
)
def health_check(db: Session = Depends(get_db)):
    """Retorna o status de saúde do serviço."""
    db_result = check_database_health(db)

    if db_result["status"] == "connected" and not db_result.get("missing_tables"):
        logger.info("Health check: healthy")
        return HealthCheckResponse(
            status="healthy",
            service=settings.APP_NAME,
            version=settings.APP_VERSION,
            database={"postgres": "connected"},
            timestamp=datetime.now(timezone.utc),
        )

    # Status degradado — retorna 503
    logger.warning(
        "Health check: degraded",
        db_status=db_result["status"],
        missing_tables=db_result.get("missing_tables"),
        error=db_result.get("error"),
    )
    return JSONResponse(
        status_code=503,
        content=HealthCheckResponse(
            status="degraded",
            service=settings.APP_NAME,
            version=settings.APP_VERSION,
            database={"postgres": db_result["status"]},
            timestamp=datetime.now(timezone.utc),
            details={
                "missing_tables": db_result.get("missing_tables", []),
                "error": db_result.get("error"),
            },
        ).model_dump(mode="json"),
    )
