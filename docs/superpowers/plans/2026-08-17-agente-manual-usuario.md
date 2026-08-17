# Agente de IA "Manual de Usuário Inteligente" do GrindX — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir um agente RAG (FastAPI + pgvector + DeepSeek + sentence-transformers) que responde perguntas sobre os manuais do ERP GrindX, exposto por um widget flutuante nativo no frontend.

**Architecture:** Backend FastAPI isolado em `apps/agente-ia/` (porta 8003) com pipeline RAG (ingestão → chunking por seção → embeddings locais → busca pgvector com filtro por módulo + fallback global → geração DeepSeek). O widget (JS puro no `dashboard.html`) renderiza o chat nativamente e chama `POST /v1/agente/chat`. O pgvector reusa o PostgreSQL existente do GrindX.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2, pgvector, sentence-transformers, httpx (DeepSeek), structlog; frontend vanilla JS/CSS (tokens `var(--...)`).

---

## Arquitetura de arquivos

**Criar (`apps/agente-ia/`):**
- `app/__init__.py` — (já criado)
- `app/core/__init__.py` — (já criado)
- `app/core/config.py` — settings (já criado, precisa de fix no `DATABASE_URL`)
- `app/core/logging.py` — structlog + log JSONL (já criado)
- `app/core/exceptions.py` — exceções (já criado)
- `app/database.py` — engine lazy + `Base` + `get_db` (já criado)
- `app/rag/__init__.py` — (já criado)
- `app/rag/types.py` — dataclass `ChunkResult`
- `app/rag/ingestion.py` — chunking Markdown por seção
- `app/rag/embeddings.py` — sentence-transformers
- `app/rag/vectorstore.py` — modelo + pgvector CRUD/busca
- `app/rag/retrieval.py` — filtro por módulo + fallback
- `app/rag/generation.py` — DeepSeek
- `app/schemas.py` — Pydantic
- `app/routers/__init__.py` — (já criado)
- `app/routers/health_router.py` — health check
- `app/routers/chat_router.py` — `POST /v1/agente/chat`
- `app/routers/ingest_router.py` — `POST /v1/agente/manuais`, `GET /v1/agente/modulos`
- `app/main.py` — app FastAPI
- `requirements.txt`, `.env.example`, `Dockerfile`, `README.md`
- `manuals/estoque.md` — manual de exemplo
- `tests/conftest.py`, `tests/test_ingestion.py`, `tests/test_retrieval.py`, `tests/test_generation.py`

**Modificar (GrindX existente):**
- `apps/frontend-webapp/widget/widget.js` — reescrever para chat nativo
- `apps/frontend-webapp/widget/widget.css` — estilos de chat
- `apps/frontend-webapp/dashboard.js` — (já modificado: expõe `body.dataset.activeModule`)
- `apps/frontend-webapp/dashboard.html` — (já modificado: carrega o widget)

> **Scaffolding já criado** nas tasks anteriores: `config.py`, `logging.py`, `exceptions.py`, `database.py`, `__init__.py` e as edições em `dashboard.js`/`dashboard.html`. A Task 1 valida/ajusta o que existe.

---

## Task 1: Ajustar config (fix do `DATABASE_URL`)

**Files:**
- Modify: `apps/agente-ia/app/core/config.py:28`

- [ ] **Step 1: Tornar `DATABASE_URL` opcional (default `""`)**

Em `app/core/config.py`, trocar a linha:

```python
    # --- Banco de Dados (PostgreSQL do GrindX + pgvector) ---
    DATABASE_URL: str
```

por:

```python
    # --- Banco de Dados (PostgreSQL do GrindX + pgvector) ---
    DATABASE_URL: str = ""
```

Motivo: `Settings()` é instanciado no import. Sem default, qualquer import do config falha fora do ambiente com `.env`, quebrando os testes unitários.

- [ ] **Step 2: Confirmar que o import não falha**

Run: `python -c "import sys; sys.path.insert(0, 'apps/agente-ia'); from app.core.config import settings; print(settings.APP_NAME)"`

Expected: `GrindX Agente IA`

- [ ] **Step 3: Commit**

```bash
git add apps/agente-ia/app/core/config.py
git commit -m "fix(agente): make DATABASE_URL optional for import-safe config"
```

---

## Task 2: Tipos compartilhados do RAG

**Files:**
- Create: `apps/agente-ia/app/rag/types.py`

- [ ] **Step 1: Escrever o arquivo**

```python
"""Tipos de dados compartilhados do pipeline RAG."""

from dataclasses import dataclass


@dataclass
class ChunkResult:
    """Trecho recuperado do banco vetorial com sua similaridade."""

    id: int
    module: str
    title: str
    content: str
    filename: str
    similarity: float
```

- [ ] **Step 2: Commit**

```bash
git add apps/agente-ia/app/rag/types.py
git commit -m "feat(agente): add shared RAG result type"
```

---

## Task 3: Ingestão — chunking Markdown

**Files:**
- Create: `apps/agente-ia/app/rag/ingestion.py`
- Test: `apps/agente-ia/tests/test_ingestion.py`

- [ ] **Step 1: Escrever o teste que falha**

```python
from app.rag.ingestion import chunk_markdown


def test_chunk_markdown_splits_by_headings():
    text = (
        "# Manual de Estoque\n"
        "Introdução do manual.\n"
        "## Entrada de Produtos\n"
        "Passo 1: abrir a tela.\n"
        "Passo 2: informar o SKU.\n"
        "## Baixa de Produtos\n"
        "Informar a quantidade a baixar.\n"
    )
    chunks = chunk_markdown(text)
    assert [c.title for c in chunks] == [
        "Manual de Estoque",
        "Entrada de Produtos",
        "Baixa de Produtos",
    ]
    assert "informar o SKU" in chunks[1].content


def test_chunk_markdown_skips_empty_sections():
    text = "## Vazio\n\n## Com conteúdo\nTexto aqui.\n"
    chunks = chunk_markdown(text)
    assert [c.title for c in chunks] == ["Com conteúdo"]
```

- [ ] **Step 2: Rodar para ver falhar**

Run: `python -m pytest apps/agente-ia/tests/test_ingestion.py -v`

Expected: FAIL (`ModuleNotFoundError: app.rag.ingestion`)

- [ ] **Step 3: Implementar**

```python
"""Extração e divisão de manuais Markdown em chunks por seção."""

import re
from dataclasses import dataclass


@dataclass
class Chunk:
    """Trecho de documento (seção) com título e conteúdo."""

    title: str
    content: str


def _split_headings(text: str) -> list[tuple[str, str]]:
    lines = text.splitlines()
    sections: list[tuple[str, str]] = []
    current_title: str | None = None
    current_lines: list[str] = []

    for line in lines:
        match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
        if match:
            if current_title is not None:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = match.group(2).strip()
            current_lines = []
        else:
            if current_title is None:
                current_title = ""
            current_lines.append(line)

    if current_title is not None:
        sections.append((current_title, "\n".join(current_lines).strip()))

    return sections


def chunk_markdown(text: str) -> list[Chunk]:
    """Divide um documento Markdown em chunks, um por seção (título)."""
    return [
        Chunk(title=title, content=content)
        for title, content in _split_headings(text)
        if content.strip()
    ]
```

- [ ] **Step 4: Rodar para ver passar**

Run: `python -m pytest apps/agente-ia/tests/test_ingestion.py -v`

Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add apps/agente-ia/app/rag/ingestion.py apps/agente-ia/tests/test_ingestion.py
git commit -m "feat(agente): markdown chunking by section"
```

---

## Task 4: Embeddings

**Files:**
- Create: `apps/agente-ia/app/rag/embeddings.py`

- [ ] **Step 1: Implementar**

```python
"""Geração de embeddings com sentence-transformers (modelo local)."""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import settings


@lru_cache
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(settings.EMBEDDING_MODEL)


def embed(texts: list[str]) -> list[list[float]]:
    """Gera embeddings normalizados para uma lista de textos."""
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=True)
    return [vector.tolist() for vector in vectors]
```

- [ ] **Step 2: Verificar import (não carrega o modelo ainda)**

Run: `python -c "import sys; sys.path.insert(0, 'apps/agente-ia'); import app.rag.embeddings; print('ok')"`

Expected: `ok` (carrega o modelo apenas na primeira chamada de `embed`)

- [ ] **Step 3: Commit**

```bash
git add apps/agente-ia/app/rag/embeddings.py
git commit -m "feat(agente): local sentence-transformers embeddings"
```

---

## Task 5: Vector store (pgvector)

**Files:**
- Create: `apps/agente-ia/app/rag/vectorstore.py`

- [ ] **Step 1: Implementar**

```python
"""Persistência e busca vetorial com pgvector (PostgreSQL)."""

from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import String, Text, delete, select, text
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.core.config import settings
from app.database import Base, get_engine
from app.rag.types import ChunkResult


class Chunk(Base):
    """Chunk de manual indexado com embedding."""

    __tablename__ = settings.AGENT_TABLE
    __table_args__ = {"schema": settings.AGENT_SCHEMA}

    id: Mapped[int] = mapped_column(primary_key=True)
    module: Mapped[str] = mapped_column(String(120), index=True)
    title: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    filename: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    embedding = mapped_column(Vector(settings.EMBEDDING_DIM))


def init_db() -> None:
    """Cria schema, extensão pgvector e tabela (idempotente)."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{settings.AGENT_SCHEMA}"'))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(engine)


def add_chunks(records: list[dict]) -> int:
    """Insere chunks. Cada dict: module, title, content, filename, embedding."""
    with Session(get_engine()) as session:
        session.add_all([Chunk(**record) for record in records])
        session.commit()
    return len(records)


def search(embedding: list[float], module: str | None, k: int) -> list[ChunkResult]:
    """Busca os k chunks mais similares, filtrando por módulo quando informado."""
    stmt = select(
        Chunk,
        (1 - Chunk.embedding.cosine_distance(embedding)).label("similarity"),
    )
    if module:
        stmt = stmt.where(Chunk.module == module)
    stmt = stmt.order_by(Chunk.embedding.cosine_distance(embedding)).limit(k)

    with Session(get_engine()) as session:
        rows = session.execute(stmt).all()

    return [
        ChunkResult(
            id=chunk.id,
            module=chunk.module,
            title=chunk.title,
            content=chunk.content,
            filename=chunk.filename,
            similarity=float(similarity),
        )
        for chunk, similarity in rows
    ]


def list_modules() -> list[str]:
    """Lista os módulos que possuem manuais indexados."""
    stmt = select(Chunk.module).distinct().order_by(Chunk.module)
    with Session(get_engine()) as session:
        return list(session.scalars(stmt))


def clear_module(module: str) -> int:
    """Remove todos os chunks de um módulo e retorna a quantidade removida."""
    with Session(get_engine()) as session:
        result = session.execute(delete(Chunk).where(Chunk.module == module))
        session.commit()
    return result.rowcount or 0
```

- [ ] **Step 2: Commit**

```bash
git add apps/agente-ia/app/rag/vectorstore.py
git commit -m "feat(agente): pgvector store with cosine search"
```

> Nota: `vectorstore` não é coberto por teste unitário (requer PostgreSQL + pgvector reais). A integração é validada manualmente na Task 9.

---

## Task 6: Recuperação (RAG)

**Files:**
- Create: `apps/agente-ia/app/rag/retrieval.py`
- Test: `apps/agente-ia/tests/test_retrieval.py`

- [ ] **Step 1: Escrever o teste que falha**

```python
from app.rag.retrieval import retrieve
from app.rag.types import ChunkResult


def _chunk(similarity: float, module: str = "estoque") -> ChunkResult:
    return ChunkResult(
        id=1,
        module=module,
        title="Entrada de Produtos",
        content="como cadastrar um produto",
        filename="estoque.md",
        similarity=similarity,
    )


def test_retrieve_finds_in_module_without_fallback():
    def embed_fn(texts):
        return [[0.1, 0.2]]

    def search_fn(embedding, module, k):
        return [_chunk(0.8)]

    result = retrieve(
        question="como cadastrar produto?",
        module="estoque",
        embed_fn=embed_fn,
        search_fn=search_fn,
        threshold=0.35,
        top_k=3,
    )
    assert result.has_answer is True
    assert result.used_fallback is False


def test_retrieve_falls_back_to_global_when_module_misses():
    calls = []

    def embed_fn(texts):
        return [[0.1, 0.2]]

    def search_fn(embedding, module, k):
        calls.append(module)
        return [] if module == "estoque" else [_chunk(0.7)]

    result = retrieve(
        question="onde vejo o balanço?",
        module="estoque",
        embed_fn=embed_fn,
        search_fn=search_fn,
        threshold=0.35,
        top_k=3,
    )
    assert result.has_answer is True
    assert result.used_fallback is True
    assert calls == ["estoque", None]


def test_retrieve_returns_no_answer_when_below_threshold():
    def embed_fn(texts):
        return [[0.1, 0.2]]

    def search_fn(embedding, module, k):
        return [_chunk(0.2)]

    result = retrieve(
        question="pergunta sem resposta",
        module="estoque",
        embed_fn=embed_fn,
        search_fn=search_fn,
        threshold=0.35,
        top_k=3,
    )
    assert result.has_answer is False
```

- [ ] **Step 2: Rodar para ver falhar**

Run: `python -m pytest apps/agente-ia/tests/test_retrieval.py -v`

Expected: FAIL

- [ ] **Step 3: Implementar**

```python
"""Camada de recuperação RAG: filtro estrito por módulo + fallback global."""

from dataclasses import dataclass, field

from app.core.config import settings
from app.rag.types import ChunkResult


@dataclass
class RetrievalResult:
    """Resultado da recuperação."""

    chunks: list[ChunkResult] = field(default_factory=list)
    used_fallback: bool = False

    @property
    def has_answer(self) -> bool:
        return bool(self.chunks)


def retrieve(
    question: str,
    module: str,
    embed_fn,
    search_fn,
    threshold: float | None = None,
    top_k: int | None = None,
) -> RetrievalResult:
    """Recupera chunks: primeiro filtrado por módulo, depois busca global."""
    threshold = threshold if threshold is not None else settings.SIMILARITY_THRESHOLD
    top_k = top_k if top_k is not None else settings.TOP_K

    embedding = embed_fn([question])[0]

    results = search_fn(embedding, module=module, k=top_k)
    if results and results[0].similarity >= threshold:
        return RetrievalResult(chunks=results, used_fallback=False)

    global_results = search_fn(embedding, module=None, k=top_k)
    if global_results and global_results[0].similarity >= threshold:
        return RetrievalResult(chunks=global_results, used_fallback=True)

    return RetrievalResult(chunks=[], used_fallback=True)
```

- [ ] **Step 4: Rodar para ver passar**

Run: `python -m pytest apps/agente-ia/tests/test_retrieval.py -v`

Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add apps/agente-ia/app/rag/retrieval.py apps/agente-ia/tests/test_retrieval.py
git commit -m "feat(agente): RAG retrieval with module filter and fallback"
```

---

## Task 7: Geração (DeepSeek)

**Files:**
- Create: `apps/agente-ia/app/rag/generation.py`
- Test: `apps/agente-ia/tests/test_generation.py`

- [ ] **Step 1: Escrever o teste que falha**

```python
import httpx
import pytest

from app.rag import generation
from app.rag.types import ChunkResult


def _chunk() -> ChunkResult:
    return ChunkResult(
        id=1,
        module="estoque",
        title="Entrada de Produtos",
        content="Para cadastrar, vá em Produtos > Novo.",
        filename="estoque.md",
        similarity=0.8,
    )


def test_generate_returns_fallback_when_no_chunks():
    assert generation.generate("pergunta", []) == generation.FALLBACK_ANSWER


def test_build_context_formats_sources():
    context = generation.build_context([_chunk()])
    assert "[estoque.md — Entrada de Produtos]" in context
    assert "Produtos > Novo" in context


def test_generate_calls_deepseek(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "Resposta de teste"}}]}

    def fake_post(url, json=None, headers=None, timeout=None):
        return FakeResponse()

    monkeypatch.setattr(httpx, "post", fake_post)

    answer = generation.generate(
        "como cadastrar?",
        [_chunk()],
        api_key="key",
        base_url="https://api.deepseek.com",
        model="deepseek-chat",
        timeout=10,
    )
    assert answer == "Resposta de teste"
```

- [ ] **Step 2: Rodar para ver falhar**

Run: `python -m pytest apps/agente-ia/tests/test_generation.py -v`

Expected: FAIL

- [ ] **Step 3: Implementar**

```python
"""Geração de respostas com o DeepSeek (deepseek-chat)."""

import httpx

from app.core.config import settings
from app.core.exceptions import GenerationError
from app.rag.types import ChunkResult

SYSTEM_PROMPT = (
    "Você é o assistente de manual do ERP GrindX. "
    "Responda SOMENTE com base no contexto fornecido. "
    "Não use conhecimento externo. "
    "Cite a fonte (manual e seção) de cada informação no formato [manual — seção]. "
    'Se o contexto não cobrir a pergunta, responda exatamente: '
    '"Não encontrei essa informação nos manuais disponíveis."'
)

FALLBACK_ANSWER = "Não encontrei essa informação nos manuais disponíveis."


def build_context(chunks: list[ChunkResult]) -> str:
    """Monta o bloco de contexto a partir dos chunks recuperados."""
    return "\n\n".join(
        f"[{chunk.filename} — {chunk.title}]\n{chunk.content}" for chunk in chunks
    )


def generate(
    question: str,
    chunks: list[ChunkResult],
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
    timeout: int | None = None,
) -> str:
    """Gera a resposta via DeepSeek com base no contexto recuperado."""
    if not chunks:
        return FALLBACK_ANSWER

    api_key = api_key or settings.DEEPSEEK_API_KEY
    base_url = base_url or settings.DEEPSEEK_BASE_URL
    model = model or settings.DEEPSEEK_MODEL
    timeout = timeout or settings.DEEPSEEK_TIMEOUT_SECONDS

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Contexto:\n{build_context(chunks)}\n\nPergunta: {question}",
            },
        ],
        "temperature": 0.2,
        "stream": False,
    }
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    try:
        response = httpx.post(
            f"{base_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise GenerationError(str(exc)) from exc

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()
```

- [ ] **Step 4: Rodar para ver passar**

Run: `python -m pytest apps/agente-ia/tests/test_generation.py -v`

Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add apps/agente-ia/app/rag/generation.py apps/agente-ia/tests/test_generation.py
git commit -m "feat(agente): DeepSeek generation with source citation and fallback"
```

---

## Task 8: Schemas, routers e app principal

**Files:**
- Create: `apps/agente-ia/app/schemas.py`
- Create: `apps/agente-ia/app/routers/health_router.py`
- Create: `apps/agente-ia/app/routers/chat_router.py`
- Create: `apps/agente-ia/app/routers/ingest_router.py`
- Create: `apps/agente-ia/app/main.py`

- [ ] **Step 1: `schemas.py`**

```python
"""Schemas Pydantic de requisição e resposta da API."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    module: str = Field(default="", max_length=120)


class Source(BaseModel):
    filename: str
    title: str
    module: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    used_fallback: bool
    found: bool


class IngestRequest(BaseModel):
    module: str = Field(min_length=1, max_length=120)
    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class IngestResponse(BaseModel):
    chunks: int


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    database: dict
    timestamp: str
```

- [ ] **Step 2: `health_router.py`**

```python
"""Router de health check da API do Agente."""

from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import get_db
from app.schemas import HealthResponse

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:  # noqa: BLE001
        logger.error("Falha na verificação do banco", error=str(exc))
        db_status = "disconnected"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        database={"postgres": db_status},
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
```

- [ ] **Step 3: `chat_router.py`**

```python
"""Router de chat do Agente de IA."""

import structlog
from fastapi import APIRouter, HTTPException

from app.core.exceptions import AgenteError
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
```

- [ ] **Step 4: `ingest_router.py`**

```python
"""Router de ingestão de manuais."""

import structlog
from fastapi import APIRouter, HTTPException

from app.core.exceptions import AgenteError
from app.rag import embeddings, ingestion, vectorstore
from app.schemas import IngestRequest, IngestResponse

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/v1/agente", tags=["Agente"])


@router.post("/manuais", response_model=IngestResponse)
def ingest_manual(request: IngestRequest) -> IngestResponse:
    chunks = ingestion.chunk_markdown(request.content)
    if not chunks:
        raise HTTPException(status_code=400, detail="Nenhum conteúdo no manual")

    try:
        vectors = embeddings.embed([chunk.content for chunk in chunks])
    except AgenteError as exc:
        logger.error("Falha ao gerar embeddings", error=str(exc))
        raise HTTPException(status_code=500, detail="Falha ao gerar embeddings") from exc

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

    vectorstore.add_chunks(records)
    return IngestResponse(chunks=len(records))


@router.get("/modulos")
def list_modules() -> dict:
    return {"modules": vectorstore.list_modules()}
```

- [ ] **Step 5: `main.py`**

```python
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
```

- [ ] **Step 6: Commit**

```bash
git add apps/agente-ia/app/schemas.py apps/agente-ia/app/routers/ apps/agente-ia/app/main.py
git commit -m "feat(agente): FastAPI app with chat, ingest and health routers"
```

---

## Task 9: Dependências, config, Docker e manuais

**Files:**
- Create: `apps/agente-ia/requirements.txt`
- Create: `apps/agente-ia/.env.example`
- Create: `apps/agente-ia/Dockerfile`
- Create: `apps/agente-ia/README.md`
- Create: `apps/agente-ia/manuals/estoque.md`
- Create: `apps/agente-ia/tests/conftest.py`

- [ ] **Step 1: `requirements.txt`**

```
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.27
psycopg[binary]>=3.1.18
pgvector>=0.3.0
sentence-transformers>=2.7.0
httpx>=0.27.0
pydantic>=2.6.1
pydantic-settings>=2.2.1
python-dotenv>=1.0.1
structlog>=24.1.0
```

- [ ] **Step 2: `.env.example`**

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/grindx
DEEPSEEK_API_KEY=
DEEPSEEK_MODEL=deepseek-chat
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
SIMILARITY_THRESHOLD=0.35
TOP_K=3
CORS_ORIGINS=
```

- [ ] **Step 3: `Dockerfile`**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8003

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
```

- [ ] **Step 4: `manuals/estoque.md`**

```markdown
# Manual do Módulo de Estoque

## Entrada de Produtos
Para dar entrada em um produto, acesse o menu **Estoque > Entrada**.
Informe o SKU, a quantidade e o fornecedor e clique em **Salvar**.

## Baixa de Produtos
Acesse **Estoque > Baixa**, selecione o produto, informe a quantidade a baixar e o motivo.

## Consulta de Saldo
Na tela **Estoque > Saldo**, digite o SKU para ver o saldo atual e a localização no depósito.
```

- [ ] **Step 5: `tests/conftest.py`**

```python
"""Configuração dos testes do agente."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("DEEPSEEK_API_KEY", "")
```

- [ ] **Step 6: `README.md`**

```markdown
# GrindX Agente IA

Assistente de IA (RAG) que responde perguntas sobre os manuais do ERP GrindX.

## Endpoints

- `GET  /health` — health check
- `POST /v1/agente/chat` — pergunta + módulo → resposta com fontes
- `POST /v1/agente/manuais` — ingestão de manual Markdown por módulo
- `GET  /v1/agente/modulos` — lista módulos indexados

## Execução local

```bash
pip install -r requirements.txt
copy .env.example .env   # preencher DATABASE_URL e DEEPSEEK_API_KEY
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

## Testes

```bash
python -m pytest tests/ -v
```
```

- [ ] **Step 7: Commit**

```bash
git add apps/agente-ia/requirements.txt apps/agente-ia/.env.example apps/agente-ia/Dockerfile apps/agente-ia/README.md apps/agente-ia/manuals/ apps/agente-ia/tests/conftest.py
git commit -m "chore(agente): deps, env example, dockerfile, sample manual, readme"
```

---

## Task 10: Widget — chat nativo (sem iframe)

**Files:**
- Modify: `apps/frontend-webapp/widget/widget.js`
- Modify: `apps/frontend-webapp/widget/widget.css`

- [ ] **Step 1: Reescrever `widget.js`**

```javascript
/**
 * AGENTE IA — WIDGET FLUTUANTE (Mascote)
 *
 * Botão flutuante no canto do dashboard que abre um painel de chat nativo.
 * Chama POST /v1/agente/chat com o módulo ativo (body.dataset.activeModule).
 * URL do agente: configurável via window.__GRINDX_AGENT_URL no deploy.
 */
(function () {
    'use strict';

    const AGENT_URL = window.__GRINDX_AGENT_URL || 'http://localhost:8003';
    const CHAT_ENDPOINT = AGENT_URL.replace(/\/+$/, '') + '/v1/agente/chat';

    function getActiveModule() {
        return document.body.dataset.activeModule || '';
    }

    function createWidget() {
        const fab = document.createElement('button');
        fab.className = 'grindx-ai-fab';
        fab.type = 'button';
        fab.setAttribute('aria-label', 'Abrir assistente de IA');
        fab.innerHTML = '<i class="fas fa-robot" aria-hidden="true"></i>';

        const panel = document.createElement('div');
        panel.className = 'grindx-ai-panel';
        panel.setAttribute('aria-hidden', 'true');
        panel.innerHTML =
            '<div class="grindx-ai-panel-header">' +
                '<span><i class="fas fa-robot" aria-hidden="true"></i> Assistente GrindX</span>' +
                '<button type="button" class="grindx-ai-close" aria-label="Fechar">&times;</button>' +
            '</div>' +
            '<div class="grindx-ai-messages"></div>' +
            '<div class="grindx-ai-input">' +
                '<input type="text" class="grindx-ai-field" placeholder="Pergunte sobre esta tela..." aria-label="Sua pergunta" />' +
                '<button type="button" class="grindx-ai-send" aria-label="Enviar"><i class="fas fa-paper-plane" aria-hidden="true"></i></button>' +
            '</div>';

        document.body.appendChild(fab);
        document.body.appendChild(panel);

        const messages = panel.querySelector('.grindx-ai-messages');
        const field = panel.querySelector('.grindx-ai-field');
        const sendBtn = panel.querySelector('.grindx-ai-send');
        const closeBtn = panel.querySelector('.grindx-ai-close');

        function addMessage(text, role) {
            const bubble = document.createElement('div');
            bubble.className = 'grindx-ai-msg grindx-ai-msg-' + role;
            bubble.textContent = text;
            messages.appendChild(bubble);
            messages.scrollTop = messages.scrollHeight;
            return bubble;
        }

        function addSources(sources) {
            const line = document.createElement('div');
            line.className = 'grindx-ai-sources';
            line.textContent = 'Fontes: ' + sources
                .map(function (s) { return s.filename + ' — ' + s.title; })
                .join(' · ');
            messages.appendChild(line);
            messages.scrollTop = messages.scrollHeight;
        }

        async function ask(question) {
            const text = (question || '').trim();
            if (!text) return;
            addMessage(text, 'user');
            field.value = '';

            const thinking = addMessage('Pensando...', 'assistant');
            try {
                const response = await fetch(CHAT_ENDPOINT, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: text, module: getActiveModule() })
                });
                if (!response.ok) throw new Error('HTTP ' + response.status);
                const data = await response.json();
                thinking.remove();
                addMessage(data.answer, 'assistant');
                if (data.sources && data.sources.length) {
                    addSources(data.sources);
                }
            } catch (err) {
                thinking.remove();
                addMessage('Não foi possível falar com o assistente. Tente novamente.', 'assistant');
            }
        }

        sendBtn.addEventListener('click', function () { ask(field.value); });
        field.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') ask(field.value);
        });
        fab.addEventListener('click', function () {
            const open = panel.classList.toggle('open');
            panel.setAttribute('aria-hidden', String(!open));
            if (open) field.focus();
        });
        closeBtn.addEventListener('click', function () {
            panel.classList.remove('open');
            panel.setAttribute('aria-hidden', 'true');
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createWidget);
    } else {
        createWidget();
    }
})();
```

- [ ] **Step 2: Reescrever `widget.css`**

```css
/* ==========================================
   AGENTE IA — WIDGET FLUTUANTE (Mascote)
   Design System: Glassmorphism + tokens var(--...)
   ========================================== */

.grindx-ai-fab {
    position: fixed;
    bottom: 24px;
    right: 24px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    border: 1px solid var(--border-color);
    background: var(--bg-card);
    color: var(--primary);
    font-size: 1.5rem;
    cursor: pointer;
    z-index: 9000;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.2s, box-shadow 0.2s;
}

.grindx-ai-fab:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.24);
}

.grindx-ai-panel {
    position: fixed;
    bottom: 96px;
    right: 24px;
    width: 380px;
    max-width: calc(100vw - 32px);
    height: 560px;
    max-height: calc(100vh - 120px);
    display: flex;
    flex-direction: column;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 0.75rem;
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.28);
    overflow: hidden;
    z-index: 9000;
    opacity: 0;
    visibility: hidden;
    transform: translateY(16px);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    pointer-events: none;
}

.grindx-ai-panel.open {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
    pointer-events: auto;
}

.grindx-ai-panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border-color);
    color: var(--text-main);
    font-weight: 600;
    font-size: 0.9rem;
    flex-shrink: 0;
}

.grindx-ai-panel-header span {
    display: flex;
    align-items: center;
    gap: var(--space-2);
}

.grindx-ai-panel-header i {
    color: var(--primary);
}

.grindx-ai-close {
    border: none;
    background: none;
    color: var(--text-muted);
    font-size: 1.25rem;
    cursor: pointer;
    line-height: 1;
    padding: 0;
}

.grindx-ai-close:hover {
    color: var(--text-main);
}

.grindx-ai-messages {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    background: var(--bg-main);
}

.grindx-ai-msg {
    max-width: 85%;
    padding: 0.6rem 0.8rem;
    border-radius: 0.75rem;
    font-size: 0.85rem;
    line-height: 1.45;
    white-space: pre-wrap;
    word-break: break-word;
}

.grindx-ai-msg-user {
    align-self: flex-end;
    background: var(--primary);
    color: #ffffff;
}

.grindx-ai-msg-assistant {
    align-self: flex-start;
    background: var(--bg-card);
    color: var(--text-main);
    border: 1px solid var(--border-color);
}

.grindx-ai-sources {
    align-self: flex-start;
    font-size: 0.7rem;
    color: var(--text-muted);
    padding: 0 0.25rem;
}

.grindx-ai-input {
    display: flex;
    gap: var(--space-2);
    padding: 0.6rem;
    border-top: 1px solid var(--border-color);
    flex-shrink: 0;
}

.grindx-ai-field {
    flex: 1;
    border: 1px solid var(--border-color);
    background: var(--bg-main);
    color: var(--text-main);
    border-radius: 0.5rem;
    padding: 0.5rem 0.75rem;
    font-size: 0.85rem;
}

.grindx-ai-send {
    border: none;
    background: var(--primary);
    color: #ffffff;
    border-radius: 0.5rem;
    padding: 0 0.9rem;
    cursor: pointer;
    font-size: 0.9rem;
}

@media (max-width: 480px) {
    .grindx-ai-fab {
        width: 52px;
        height: 52px;
        bottom: 16px;
        right: 16px;
    }
    .grindx-ai-panel {
        bottom: 80px;
        right: 16px;
        left: 16px;
        width: auto;
        height: calc(100vh - 120px);
    }
}
```

- [ ] **Step 3: Validar sintaxe JS**

Run: `node --check apps/frontend-webapp/widget/widget.js`

Expected: sem saída (sem erros)

- [ ] **Step 4: Commit**

```bash
git add apps/frontend-webapp/widget/widget.js apps/frontend-webapp/widget/widget.css
git commit -m "feat(frontend): native chat widget for AI assistant"
```

---

## Task 11: Validação final (ruff + testes)

**Files:** nenhum

- [ ] **Step 1: Rodar os testes do agente**

Run: `python -m pytest apps/agente-ia/tests/ -v`

Expected: 8 passed (2 ingestion + 3 retrieval + 3 generation)

- [ ] **Step 2: Rodar ruff no app do agente**

Run: `ruff check apps/agente-ia/ && ruff format --check apps/agente-ia/`

Expected: sem erros

- [ ] **Step 3: Rodar os testes do monorepo (garantir que nada quebrou)**

Run: `make test-all`

Expected: suíte existente continua passando

- [ ] **Step 4: Commit final (se houver ajustes de lint)**

```bash
git add -A
git commit -m "chore(agente): lint and test fixes"
```

---

## Self-Review

- **Spec coverage:** todas as etapas do desafio cobertas — coleta/ingestão (Task 8 ingest_router), processamento (Task 3), indexação vetorial (Tasks 4-5), recuperação RAG (Task 6), geração/validação (Task 7), interface (Task 10), deploy OCI (Task 9 Dockerfile — deploy efetivo em follow-up), registro (logging JSONL em `core/logging.py`), README (Task 9).
- **Type consistency:** `ChunkResult` definido em `types.py` e usado em `vectorstore.py`, `retrieval.py`, `generation.py`; `embed` retorna `list[list[float]]`; `search(embedding, module, k)` assinatura consistente entre `retrieval` (mock) e `vectorstore`.
- **Placeholder scan:** nenhum TBD/TODO; todos os passos têm código completo.

> **Fora deste plano (follow-up):** deploy real na OCI (Ampere A1 + Docker + Object Storage + OCIR), adicionar o app ao `compose.yaml`/`Makefile`, e documentação em `docs/` do GrindX (Docs Sync exigido pelo AGENTS.md).
