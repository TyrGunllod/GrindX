"""Router de ingestão de manuais."""

import structlog
from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.core.exceptions import AgenteError
from app.rag import embeddings, ingestion, vectorstore
from app.schemas import IngestRequest, IngestResponse

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/v1/agente", tags=["Agente"])


@router.post("/manuais", response_model=IngestResponse)
def ingest_manual(request: IngestRequest) -> IngestResponse:
    chunks = (
        ingestion.chunk_csv(request.content)
        if request.filename.lower().endswith(".csv")
        else ingestion.chunk_markdown(request.content)
    )
    if not chunks:
        raise HTTPException(status_code=400, detail="Nenhum conteúdo no documento")

    if settings.EMBEDDINGS_ENABLED:
        try:
            vectors = embeddings.embed(
                [f"{chunk.title}\n{chunk.content}" for chunk in chunks]
            )
        except AgenteError as exc:
            logger.error("Falha ao gerar embeddings", error=str(exc))
            raise HTTPException(
                status_code=500, detail="Falha ao gerar embeddings"
            ) from exc

        records = [
            {
                "module": request.module,
                "title": chunk.title,
                "content": chunk.content,
                "filename": request.filename,
                "embedding": vectors[index],
            }
            for index, chunk in enumerate(chunks)
        ]
    else:
        records = [
            {
                "module": request.module,
                "title": chunk.title,
                "content": chunk.content,
                "filename": request.filename,
                "embedding": None,
            }
            for chunk in chunks
        ]

    vectorstore.add_chunks(records)
    return IngestResponse(chunks=len(records))


@router.get("/modulos")
def list_modules() -> dict:
    return {"modules": vectorstore.list_modules()}


@router.get("/manuais")
def list_manuais() -> dict:
    return {"manuais": vectorstore.list_manuals()}


@router.delete("/manuais")
def remove_manual(module: str, filename: str) -> dict:
    removed = vectorstore.delete_manual(module, filename)
    return {"removed": removed}
