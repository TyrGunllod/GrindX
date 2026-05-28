"""
Configuração de logging estruturado com structlog.

Produz logs em formato JSON com campos padronizados:
timestamp, level, service, request_id, message.
"""

import logging
import sys

import structlog

from app.core.config import settings


def setup_logging() -> None:
    """Configura o structlog com processadores JSON e nível do .env."""

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Processadores que transformam o evento de log antes da saída
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    # Em debug, formato legível; em produção, JSON
    if settings.DEBUG:
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configura o logging padrão do Python para usar structlog
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Silenciar logs verbosos de terceiros
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if settings.DEBUG else logging.WARNING
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Retorna um logger nomeado com contexto do serviço.

    Args:
        name: Nome do módulo ou componente.

    Returns:
        Logger configurado com o nome do serviço.
    """
    return structlog.get_logger(name, service=settings.APP_NAME)
