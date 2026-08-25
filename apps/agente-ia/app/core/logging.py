"""Configuração de logging (structlog) e registro de execução (JSONL)."""

import json
import logging
import time
from pathlib import Path

import structlog

from app.core.config import settings


def setup_logging() -> None:
    """Configura structlog com saída estruturada em console."""
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        ),
        logger_factory=structlog.PrintLoggerFactory(),
    )


def _logs_path() -> Path:
    """Retorna o caminho do arquivo de logs JSONL."""
    if settings.LOGS_DIR:
        return Path(settings.LOGS_DIR) / "agente.log"
    return Path(__file__).resolve().parent.parent.parent / "logs" / "agente.log"


def log_interaction(entry: dict) -> None:
    """Grava uma linha JSONL com os dados de uma interação do agente.

    Args:
        entry: dicionário com pergunta, módulo, trechos, resposta, fontes, etc.
    """
    record = {"timestamp": time.time(), **entry}
    path = _logs_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
