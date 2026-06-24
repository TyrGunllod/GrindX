"""
Ponto de entrada da API SQL Server (somente health check).

Configura o app FastAPI com middlewares de segurança e o router de health.
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.request_id import RequestIdMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.modules.custo.routers.custo_produto_router import (
    router as custo_produto_router,
)
from app.routers.health_router import router as health_router

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia startup e shutdown da aplicação."""
    setup_logging()
    logger.info(
        "Serviço iniciado",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )
    yield
    logger.info("Serviço encerrado", service=settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Health check da conexão com o SQL Server. "
        "Apenas o endpoint /health está disponível."
    ),
    docs_url="/v1/docs",
    redoc_url="/v1/redoc",
    openapi_url="/v1/openapi.json",
    lifespan=lifespan,
)

# Middlewares
app.add_middleware(
    SecurityHeadersMiddleware,
    connect_srcs=settings.csp_connect_srcs,
)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Routers
app.include_router(health_router)
app.include_router(custo_produto_router)
