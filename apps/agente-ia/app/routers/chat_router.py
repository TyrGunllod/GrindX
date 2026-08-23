"""Router de chat do Agente de IA."""

import structlog
from fastapi import APIRouter, HTTPException

from app.core.exceptions import AgenteError, GenerationError
from app.core.logging import log_interaction
from app.rag import embeddings, generation, retrieval, vectorstore
from app.schemas import ChatRequest, ChatResponse, Source

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/v1/agente", tags=["Agente"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        result = retrieval.retrieve(
            question=request.question,
            module=request.module,
            embed_fn=embeddings.embed,
            search_fn=vectorstore.search,
        )
        answer = generation.generate(request.question, result.chunks)
    except GenerationError as exc:
        logger.error("Falha na geração da resposta", error=str(exc))
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except AgenteError as exc:
        logger.error("Falha no pipeline do agente", error=str(exc))
        raise HTTPException(
            status_code=500, detail="Falha ao processar a pergunta"
        ) from exc

    sources = [
        Source(filename=chunk.filename, title=chunk.title, module=chunk.module)
        for chunk in result.chunks
    ]

    log_interaction(
        {
            "question": request.question,
            "module": request.module,
            "used_fallback": result.used_fallback,
            "found": result.has_answer,
            "sources": [source.model_dump() for source in sources],
            "answer": answer,
        }
    )

    return ChatResponse(
        answer=answer,
        sources=sources,
        used_fallback=result.used_fallback,
        found=result.has_answer,
    )
