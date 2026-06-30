"""
Router de consulta de produtos (tabela SB1010 do Protheus).
Read-only — apenas endpoints GET.
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/v1/produtos", tags=["Produtos Protheus"])


class ItemProtheus(BaseModel):
    codigo: str
    descricao: str


@router.get("/por-codigo", response_model=list[ItemProtheus])
def buscar_por_codigo(
    codigo: str = Query(
        ..., min_length=4, description="Código do produto (mín. 4 caracteres)"
    ),
    db: Session = Depends(get_db),
):
    try:
        sql = text(
            "SELECT B1_COD, B1_DESC FROM SB1010 WHERE B1_COD LIKE :codigo ORDER BY B1_COD"
        )
        rows = db.execute(sql, {"codigo": f"{codigo}%"}).fetchall()
        return [ItemProtheus(codigo=r[0], descricao=r[1]) for r in rows]
    except SQLAlchemyError as exc:
        logger.error("Falha ao consultar SB1010 por código", error=str(exc))
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "Erro ao consultar banco de dados"
        )


@router.get("/por-descricao", response_model=list[ItemProtheus])
def buscar_por_descricao(
    descricao: str = Query(
        ..., min_length=4, description="Descrição do produto (mín. 4 caracteres)"
    ),
    db: Session = Depends(get_db),
):
    try:
        sql = text(
            "SELECT B1_COD, B1_DESC FROM SB1010 WHERE B1_DESC LIKE :descricao ORDER BY B1_COD"
        )
        rows = db.execute(sql, {"descricao": f"%{descricao}%"}).fetchall()
        return [ItemProtheus(codigo=r[0], descricao=r[1]) for r in rows]
    except SQLAlchemyError as exc:
        logger.error("Falha ao consultar SB1010 por descrição", error=str(exc))
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "Erro ao consultar banco de dados"
        )
