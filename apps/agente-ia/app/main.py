"""Ponto de entrada da API do Agente de IA."""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.rag import vectorstore
from app.routers import chat_router, health_router, ingest_router

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    try:
        vectorstore.init_db()
    except Exception as exc:  # noqa: BLE001
        logger.error("Falha ao inicializar pgvector", error=str(exc))
    logger.info(
        "Serviço iniciado",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
    )
    yield
    logger.info("Serviço encerrado", service=settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Agente de IA (RAG) — manual de usuário inteligente do GrindX.",
    docs_url="/v1/docs",
    redoc_url="/v1/redoc",
    openapi_url="/v1/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router.router)
app.include_router(chat_router.router)
app.include_router(ingest_router.router)
