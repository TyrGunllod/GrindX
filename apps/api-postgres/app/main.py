"""
Ponto de entrada da API PostgreSQL.

Configura o app FastAPI com:
- Lifespan (startup/shutdown gracioso)
- CORS
- Middlewares (request_id, security_headers, rate_limit)
- Exception handlers
- Routers (auth, health)
- Documentação Swagger/ReDoc em /v1/
- Arquivos estáticos (uploads)
"""

import os
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.auth.router import router as auth_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIdMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.routers.health_router import router as health_router
from app.routers.import_router import router as import_router
from app.routers.portal_router import router as portal_router
from app.routers.theme_router import router as theme_router
from app.routers.usuario_router import router as usuario_router

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia startup e shutdown da aplicação.

    Startup: configura logging.
    Shutdown: encerramento gracioso.
    """
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
        "API principal do ERP — CRUD completo e autenticação centralizada. "
        "Persistência no PostgreSQL (rede local)."
    ),
    docs_url="/v1/docs",
    redoc_url="/v1/redoc",
    openapi_url="/v1/openapi.json",
    lifespan=lifespan,
)

# =========================================================
# Middlewares (ordem importa: último adicionado é executado primeiro)
# =========================================================

# Rate limiting por IP
app.add_middleware(
    RateLimitMiddleware,
    max_requests=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
    exclude_paths=["/health", "/v1/docs", "/v1/redoc", "/v1/openapi.json"],
)

# Headers de segurança
app.add_middleware(
    SecurityHeadersMiddleware,
    connect_srcs=settings.csp_connect_srcs,
)

# Request ID para rastreabilidade
app.add_middleware(RequestIdMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# =========================================================
# Exception Handlers
# =========================================================

register_exception_handlers(app)

# =========================================================
# Static Files (uploads)
# =========================================================

# Create uploads directory if it doesn't exist
uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
logos_dir = os.path.join(uploads_dir, "logos")
fonts_dir = os.path.join(uploads_dir, "fonts")
icons_dir = os.path.join(uploads_dir, "icons")
os.makedirs(logos_dir, exist_ok=True)
os.makedirs(fonts_dir, exist_ok=True)
os.makedirs(icons_dir, exist_ok=True)

# Mount static files for serving uploaded logos
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# =========================================================
# Routers
# =========================================================

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(usuario_router)
app.include_router(portal_router)
app.include_router(theme_router)
app.include_router(import_router)
