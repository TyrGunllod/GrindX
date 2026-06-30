# Produtos Protheus — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two read-only endpoints to api-sqlserver for querying Protheus products table SB1 by code and description.

**Architecture:** New router `protheus_router.py` with two GET endpoints using raw SQL via `text()`. Both validate minimum 4 characters and return `[{ codigo, descricao }]`. Table SB1 has fields B1_COD (code) and B1_DESC (description).

**Tech Stack:** FastAPI, SQLAlchemy (raw text queries), SQL Server (Protheus)

---

### Task 1: Create protheus_router.py

**Files:**
- Create: `apps/api-sqlserver/app/routers/protheus_router.py`
- Test: `apps/api-sqlserver/tests/integration/test_protheus.py`

- [ ] **Step 1: Write the failing integration tests**

File `apps/api-sqlserver/tests/integration/test_protheus.py`:

```python
"""Testes para o router de consulta de produtos Protheus."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session


class TestPorCodigo:
    def test_por_codigo_retorna_itens(self, client: TestClient, db_session: Session):
        db_session.execute(text("""
            CREATE TABLE SB1 (B1_COD VARCHAR(20), B1_DESC VARCHAR(100))
        """))
        db_session.execute(text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('ABC123', 'Produto Teste')
        """))
        db_session.execute(text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('ABC456', 'Outro Produto')
        """))
        db_session.commit()

        resp = client.get("/v1/produtos/por-codigo?codigo=ABC")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["codigo"] == "ABC123"
        assert data[0]["descricao"] == "Produto Teste"

    def test_por_codigo_minimo_4_caracteres(self, client: TestClient):
        resp = client.get("/v1/produtos/por-codigo?codigo=AB")
        assert resp.status_code == 422
        assert "4" in resp.text or "mínimo" in resp.text.lower()

    def test_por_codigo_sem_resultados(self, client: TestClient, db_session: Session):
        db_session.execute(text("""
            CREATE TABLE SB1 (B1_COD VARCHAR(20), B1_DESC VARCHAR(100))
        """))
        db_session.commit()
        resp = client.get("/v1/produtos/por-codigo?codigo=ZZZZ")
        assert resp.status_code == 200
        assert resp.json() == []


class TestPorDescricao:
    def test_por_descricao_modo_inicio(self, client: TestClient, db_session: Session):
        db_session.execute(text("""
            CREATE TABLE SB1 (B1_COD VARCHAR(20), B1_DESC VARCHAR(100))
        """))
        db_session.execute(text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('001', 'Produto Teste Um')
        """))
        db_session.execute(text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('002', 'Produto Teste Dois')
        """))
        db_session.execute(text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('003', 'Outro Item')
        """))
        db_session.commit()

        resp = client.get("/v1/produtos/por-descricao?descricao=Produto&modo=inicio")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    def test_por_descricao_modo_exato(self, client: TestClient, db_session: Session):
        db_session.execute(text("""
            CREATE TABLE SB1 (B1_COD VARCHAR(20), B1_DESC VARCHAR(100))
        """))
        db_session.execute(text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('001', 'Produto Teste')
        """))
        db_session.execute(text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('002', 'Produto Teste Completo')
        """))
        db_session.commit()

        resp = client.get("/v1/produtos/por-descricao?descricao=Produto Teste&modo=exato")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["codigo"] == "001"

    def test_por_descricao_modo_trecho(self, client: TestClient, db_session: Session):
        db_session.execute(text("""
            CREATE TABLE SB1 (B1_COD VARCHAR(20), B1_DESC VARCHAR(100))
        """))
        db_session.execute(text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('001', 'Este é um Produto Teste')
        """))
        db_session.execute(text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('002', 'Outro Item Qualquer')
        """))
        db_session.commit()

        resp = client.get("/v1/produtos/por-descricao?descricao=Produto&modo=trecho")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1

    def test_por_descricao_minimo_4_caracteres(self, client: TestClient):
        resp = client.get("/v1/produtos/por-descricao?descricao=AB&modo=inicio")
        assert resp.status_code == 422

    def test_por_descricao_modo_invalido(self, client: TestClient):
        resp = client.get("/v1/produtos/por-descricao?descricao=ABCD&modo=xpto")
        assert resp.status_code == 422

    def test_por_descricao_padrao_modo_inicio(self, client: TestClient, db_session: Session):
        db_session.execute(text("""
            CREATE TABLE SB1 (B1_COD VARCHAR(20), B1_DESC VARCHAR(100))
        """))
        db_session.execute(text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('001', 'Produto Inicio')
        """))
        db_session.commit()

        resp = client.get("/v1/produtos/por-descricao?descricao=Produto")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `$env:DB_URL_OVERRIDE="sqlite:///:memory:"; $env:SECRET_KEY="test"; python -m pytest apps/api-sqlserver/tests/integration/test_protheus.py -v`
Expected: FAIL - ImportError or 404 (router not registered yet)

- [ ] **Step 3: Create protheus_router.py**

File `apps/api-sqlserver/app/routers/protheus_router.py`:

```python
"""
Router de consulta de produtos (tabela SB1 do Protheus).
Read-only — apenas endpoints GET.
"""

from enum import Enum

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/v1/produtos", tags=["Produtos Protheus"])


class ModoDescricao(str, Enum):
    inicio = "inicio"
    exato = "exato"
    trecho = "trecho"


class ItemProtheus(BaseModel):
    codigo: str
    descricao: str


@router.get("/por-codigo", response_model=list[ItemProtheus])
def buscar_por_codigo(
    codigo: str = Query(..., min_length=4, description="Código do produto (mín. 4 caracteres)"),
    db: Session = Depends(get_db),
):
    sql = text("SELECT B1_COD, B1_DESC FROM SB1 WHERE B1_COD LIKE :codigo ORDER BY B1_COD")
    rows = db.execute(sql, {"codigo": f"{codigo}%"}).fetchall()
    return [ItemProtheus(codigo=r[0], descricao=r[1]) for r in rows]


@router.get("/por-descricao", response_model=list[ItemProtheus])
def buscar_por_descricao(
    descricao: str = Query(..., min_length=4, description="Descrição do produto (mín. 4 caracteres)"),
    modo: ModoDescricao = Query(ModoDescricao.inicio, description="Modo de busca: inicio, exato ou trecho"),
    db: Session = Depends(get_db),
):
    if modo == ModoDescricao.exato:
        sql = text("SELECT B1_COD, B1_DESC FROM SB1 WHERE B1_DESC = :descricao ORDER BY B1_COD")
        params = {"descricao": descricao}
    elif modo == ModoDescricao.trecho:
        sql = text("SELECT B1_COD, B1_DESC FROM SB1 WHERE B1_DESC LIKE :descricao ORDER BY B1_COD")
        params = {"descricao": f"%{descricao}%"}
    else:
        sql = text("SELECT B1_COD, B1_DESC FROM SB1 WHERE B1_DESC LIKE :descricao ORDER BY B1_COD")
        params = {"descricao": f"{descricao}%"}

    rows = db.execute(sql, params).fetchall()
    return [ItemProtheus(codigo=r[0], descricao=r[1]) for r in rows]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `$env:DB_URL_OVERRIDE="sqlite:///:memory:"; $env:SECRET_KEY="test"; python -m pytest apps/api-sqlserver/tests/integration/test_protheus.py -v`
Expected: all tests pass

- [ ] **Step 5: Commit**

```bash
git add apps/api-sqlserver/app/routers/protheus_router.py apps/api-sqlserver/tests/integration/test_protheus.py
git commit -m "feat: add produto endpoints (por-codigo / por-descricao) for Protheus SB1"
```

---

### Task 2: Register router in main.py

**Files:**
- Modify: `apps/api-sqlserver/app/main.py`

- [ ] **Step 1: Add import and include_router**

After line 17 (`from app.routers.health_router import router as health_router`), add:
```python
from app.routers.protheus_router import router as protheus_router
```

After line 64 (`app.include_router(health_router)`), add:
```python
app.include_router(protheus_router)
```

Also update the app description (line 39-42) to reflect the new endpoints:
```python
    description=(
        "Consultas read-only ao SQL Server Protheus. "
        "Endpoints: /health, /v1/produtos/por-codigo, /v1/produtos/por-descricao"
    ),
```

- [ ] **Step 2: Run all tests to verify no regression**

Run: `$env:DB_URL_OVERRIDE="sqlite:///:memory:"; $env:SECRET_KEY="test"; python -m pytest apps/api-sqlserver/tests/ -v`
Expected: all tests pass (existing health tests + new produto tests)

- [ ] **Step 3: Commit**

```bash
git add apps/api-sqlserver/app/main.py
git commit -m "feat: register protheus_router in main.py"
```

---

### Task 3: Run linter and format

- [ ] **Step 1: Format and lint**

Run: `ruff format apps/api-sqlserver/ && ruff check --fix apps/api-sqlserver/ && ruff check apps/api-sqlserver/`
Expected: no errors

- [ ] **Step 2: Final commit**

```bash
git commit -m "style: format protheus router with ruff"
```
