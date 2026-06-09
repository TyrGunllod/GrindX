---
name: create-standalone-module
description: Use when creating new GrindX modules that must be developed and tested independently outside the monorepo, then exported via export.py. Covers backend (FastAPI/SQLAlchemy), frontend (vanilla JS), self-contained tests, Alembic migration, and self-registration.
---

# Create Standalone Module — GrindX

Desenvolver módulos GrindX **fora do monorepo** (ex: `Project_Management/modulo-{nome}/`),
testar isoladamente, exportar via `export.py` apenas após testes verdes.

## Tech Stack Questionnaire (Perguntar Primeiro)

Antes dos parâmetros do módulo, **sempre pergunte qual padrão de frontend e banco** o usuário deseja:

> Use uma chamada `question` tool com a pergunta abaixo. Ofereça os padrões como opções clicáveis.

**"Qual padrão de frontend e banco de dados você quer usar para este módulo?"**

| Opção | Frontend | CSS | JS | Banco | Backend | GrindX API |
|-------|----------|-----|----|-------|---------|------------|
| **(A) Padrão GrindX** (Recomendado) | HTML puro | CSS puro (`var(--...)`, Grid, Flex) | Vanilla JS (fetch, template strings, delegated events) | PostgreSQL (via SQLAlchemy + Alembic) | FastAPI + SQLAlchemy | `api-postgres` |
| **(A2) GrindX + SQL Server** | HTML puro | CSS puro | Vanilla JS | SQL Server (via pyodbc, raw SQL) | FastAPI + SQLAlchemy | `api-sqlserver` |
| **(B) Outro padrão** | Especificar | Especificar | Especificar | Especificar | Especificar | Especificar |

- Se escolher **(A)**, siga os templates padrão desta skill (frontend: `index.html`, `script.js`, `style.css` sem dependências; backend: FastAPI + SQLAlchemy + PostgreSQL via Alembic). Exporta para `api-postgres`.
- Se escolher **(A2)**, segue o mesmo padrão frontend, mas usa SQL Server com raw SQL (sem ORM/Alembic). Exporta para `api-sqlserver`. Ideal para módulos que consultam ERP Protheus.
- Se escolher **(B)**, pergunte detalhadamente qual frontend (React, Vue, etc.), qual CSS (Tailwind, styled-components, etc.), qual JS (TypeScript, jQuery, etc.) e qual banco (SQLite, MySQL, etc.). Anote as respostas e adapte os templates conforme necessário. **Documente o padrão escolhido no spec antes de implementar.**

## Parameter Questionnaire

Após definir o padrão de tech stack, pergunte ao usuário cada parâmetro abaixo. Explique brevemente o que é e dê um exemplo. Ofereça um valor padrão sempre que possível.

Use `question` tool calls para perguntar. Pode perguntar múltiplos parâmetros por vez (agrupe os relacionados). Após coletar todos, confirme a lista com o usuário antes de prosseguir.

| # | Parâmetro | O que perguntar | Exemplo | Padrão |
|---|-----------|-----------------|---------|--------|
| 1 | `module_name` | "Nome do módulo em snake_case (ex: `recurso`, `pedido`, `categoria`). Usado como identificador técnico em todo o código." | `recurso` | — |
| 2 | `entity_name` | "Nome da entidade em PascalCase (ex: `Recurso`, `Pedido`). Usado nas classes Python (model, schemas, service, etc)." | `Recurso` | — |
| 3 | `schema_name` | "Schema do banco PostgreSQL onde a tabela será criada. Opções: `org` (organização/gestão), `catalogo` (produtos/serviços), `portal` (abas/módulos/menu)." | `org` | `org` |
| 4 | `table_name` | "Nome da tabela no banco (snake_case, plural). Se não informado, uso o plural do module_name." | `recursos` | `{module_name}s` |
| 5 | `route_prefix` | "Prefixo da URL da API, começando com `/v1/` (ex: `/v1/recursos`)." | `/v1/recursos` | `/v1/{module_name}s` |
| 6 | `route_api` | "Caminho da API sem a barra inicial (ex: `v1/recursos`). Usado nas chamadas REST do frontend." | `v1/recursos` | `{route_prefix}` sem `/` |
| 7 | `route_tag` | "Tag de agrupamento no Swagger (ex: `\"Recursos\"`)." | `"Recursos"` | `"{entity_name}"` |
| 8 | `frontend_prefix` | "Prefixo abreviado para os sub-módulos frontend (ex: `gp` para gestao_projetos → `gp_dashboard`, `gp_projeto`). Melhora legibilidade." | `gp` | Primeiras letras do module_name |
| 9 | `frontend_tabs` | "Array de abas/tabs do frontend. Cada tab tem `name`, `url`, `menu_icone`, `order`. Ex: Dashboard, Projetos, Tarefas." | Ver exemplo abaixo | — |
| 10 | `menu_label` | "Rótulo que aparece no menu lateral do portal para este módulo." | `"Gestão de Projetos"` | `{entity_name}` |

**Exemplo de `frontend_tabs`:**
```json
{
  "frontend_tabs": [
    {"name": "Dashboard", "url": "modules/gp_dashboard/index.html", "menu_icone": "chart-bar", "order": 1},
    {"name": "Projetos", "url": "modules/gp_projeto/index.html", "menu_icone": "folder", "order": 2}
  ]
}
```

**Nota sobre naming:** O `frontend_prefix` é usado para abreviar nomes de diretórios frontend. Exemplo: `gestao_projetos` → prefixo `gp` → `gp_dashboard`, `gp_projeto`, `gp_tarefas`.

## Directory Structure

```
Project_Management/modulo-{module_name}/        # Standalone root
├── module.json                                 # Manifest for import system
├── app/modules/{module_name}/                  # Full module (backend)
│   ├── __init__.py
│   ├── base.py                                 # {entity_name}Base (shared metadata)
│   ├── models/
│   │   ├── __init__.py
│   │   └── {module_name}.py                    # SQLAlchemy model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── {module_name}.py                    # Pydantic schemas
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── {module_name}_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── {module_name}_service.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── {module_name}_router.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py                         # SQLite + GRINDX_PACKAGES
│   │   ├── test_{module_name}_unit.py
│   │   └── test_{module_name}_integration.py
│   ├── export.py                               # Self-registration script
│   └── README.md
├── frontend/                                    # Vanilla JS frontend (sub-modules)
│   ├── {frontend_prefix}_{tab1}/               # Ex: gp_dashboard/
│   │   ├── index.html
│   │   ├── script.js
│   │   └── style.css
│   ├── {frontend_prefix}_{tab2}/               # Ex: gp_projeto/
│   │   ├── index.html
│   │   ├── script.js
│   │   └── style.css
│   └── shared/                                  # CSS compartilhado (opcional)
│       └── core.css
├── migration/
│   └── {revision}_{table_name}.py              # Alembic migration
├── Makefile                                    # Comandos: test, package, import, clean
├── requirements.txt                             # Dependencies
├── pytest.ini
└── run_tests.{ps1|sh}                           # Test runner script
```

**Nota sobre frontend:** Cada aba/taba do módulo tem seu próprio diretório com prefixo abreviado. Exemplo: módulo `gestao_projetos` com prefixo `gp` → `gp_dashboard/`, `gp_projeto/`, `gp_tarefas/`.

## Parameters Template (use in all code blocks)

Replace these placeholders:
- `{module_name}` — snake_case
- `{entity_name}` — PascalCase
- `{entity_name_lower}` — lowercase
- `{schema_name}` — org/catalogo/portal
- `{schema|pascal}` — PascalCase schema: org→Org, catalogo→Catalogo
- `{base_class}` — `{schema|pascal}Base`
- `{table_name}` — plural snake_case
- `{route_prefix}` — URL prefix
- `{route_tag}` — Swagger tag
- `{menu_label}` — menu display name
- `{route_api}` — API path
- `{frontend_prefix}` — prefixo abreviado para frontend (ex: gp)
- `{frontend_tabs}` — array de abas do frontend

## 1. Backend — Criar Todos os Arquivos

### 1.1 base.py

```python
from sqlalchemy.orm import DeclarativeBase
from app.modules.iam.base import metadata, reg


class {entity_name}Base(DeclarativeBase):
    registry = reg
    metadata = metadata
    __table_args__ = {"schema": "{schema_name}"}
```

### 1.2 Model — `models/{module_name}.py`

```python
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.{module_name}.base import {entity_name}Base


class {entity_name}({entity_name}Base):
    __tablename__ = "{table_name}"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, comment="Nome"
    )
    ativo: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="Se está ativo"
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<{entity_name}(id={self.id}, nome='{self.nome}')>"
```

**Add FKs and UniqueConstraints as needed:**
```python
from sqlalchemy import ForeignKey, UniqueConstraint

# FK example:
user_id: Mapped[int] = mapped_column(
    ForeignKey("iam.usuarios.id"), nullable=False
)

# UniqueConstraint example:
__table_args__ = (
    UniqueConstraint("user_id", "projeto_id", name="uq_{module_name}_user_projeto"),
)
```

### 1.3 Schemas — `schemas/{module_name}.py`

```python
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class {entity_name}Create(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100, description="Nome")


class {entity_name}Update(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=100)


class {entity_name}Response(BaseModel):
    id: int
    nome: str
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)
```

**Add validators as needed:**
```python
from pydantic import field_validator

@field_validator("email")
@classmethod
def validate_email(cls, v: str) -> str:
    if "@" not in v:
        raise ValueError("Email inválido")
    return v
```

### 1.4 Repository — `repositories/{module_name}_repository.py`

```python
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.{module_name}.models.{module_name} import {entity_name}
from app.modules.{module_name}.schemas.{module_name} import {entity_name}Create, {entity_name}Update


class {entity_name}Repository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_por_id(self, id: int) -> {entity_name} | None:
        stmt = select({entity_name}).where({entity_name}.id == id)
        return self.db.execute(stmt).scalar_one_or_none()

    def listar_todos(self, page: int = 1, page_size: int = 20) -> tuple[list[{entity_name}], int]:
        count_stmt = select(func.count()).select_from({entity_name})
        total = self.db.scalar(count_stmt) or 0
        stmt = select({entity_name}).order_by({entity_name}.id).offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.scalars(stmt).all())
        return items, total

    def criar(self, dados: {entity_name}Create) -> {entity_name}:
        obj = {entity_name}(**dados.model_dump())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def atualizar(self, obj: {entity_name}, dados: {entity_name}Update) -> {entity_name}:
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(obj, campo, valor)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def desativar(self, obj: {entity_name}) -> {entity_name}:
        obj.ativo = False
        self.db.commit()
        self.db.refresh(obj)
        return obj
```

**Add custom queries as needed:**
```python
def buscar_por_nome(self, nome: str) -> list[{entity_name}]:
    stmt = select({entity_name}).where({entity_name}.nome.ilike(f"%{nome}%"))
    return list(self.db.scalars(stmt).all())
```

### 1.5 Service — `services/{module_name}_service.py`

```python
import math

import structlog
from shared.exceptions.base import ConflictError, NotFoundError
from shared.schemas.base import PaginatedResponse

from app.modules.{module_name}.repositories.{module_name}_repository import {entity_name}Repository
from app.modules.{module_name}.schemas.{module_name} import {entity_name}Create, {entity_name}Update

logger = structlog.get_logger(__name__)


class {entity_name}Service:
    def __init__(self, repository: {entity_name}Repository) -> None:
        self.repository = repository

    def buscar(self, id: int):
        obj = self.repository.buscar_por_id(id)
        if not obj:
            raise NotFoundError(resource="{entity_name}", identifier=id)
        return obj

    def listar(self, page: int = 1, page_size: int = 20) -> PaginatedResponse:
        items, total = self.repository.listar_todos(page, page_size)
        return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, total_pages=math.ceil(total / page_size) if total else 0)

    def criar(self, dados: {entity_name}Create):
        obj = self.repository.criar(dados)
        logger.info("{entity_name} criado", id=obj.id, nome=obj.nome)
        return obj

    def atualizar(self, id: int, dados: {entity_name}Update):
        obj = self.buscar(id)
        return self.repository.atualizar(obj, dados)

    def desativar(self, id: int):
        obj = self.buscar(id)
        return self.repository.desativar(obj)
```

**NOTA:** `NotFoundError` recebe dois argumentos posicionais `(resource, identifier)`, NÃO uma string de mensagem.

**Add conflict validation as needed:**
```python
def criar(self, dados: {entity_name}Create):
    existente = self.repository.buscar_por_nome(dados.nome)
    if existente:
        raise ConflictError(f"{entity_name} '{dados.nome}' já existe")
    obj = self.repository.criar(dados)
    logger.info("{entity_name} criado", id=obj.id, nome=obj.nome)
    return obj
```

### 1.6 Router — `routers/{module_name}_router.py`

**IMPORTANTE: Dual-context compatibility** — O router deve funcionar tanto standalone quanto importado no GrindX. Use try/except para detectar o contexto:

```python
# Detectar contexto: GrindX vs Standalone
try:
    from app.database import get_db
    from app.auth.dependencies import get_current_user as _auth_dependency
    _grindx_mode = True
except ImportError:
    from app.core.database_protheus import get_db_protheus as get_db
    from app.core.auth import verify_api_key as _auth_dependency
    _grindx_mode = False
```

- **GrindX**: usa `app.database.get_db` (SQLAlchemy session) + JWT auth (`get_current_user`)
- **Standalone**: usa `app.core.database_protheus.get_db_protheus` + API key auth (`verify_api_key`)
- Ambos são injetados via `Depends()` — o FastAPI resolve automaticamente

**Template do router:**

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from shared.schemas.base import ErrorResponse, MessageResponse, PaginatedResponse

from app.modules.{module_name}.schemas.{module_name} import {entity_name}Create, {entity_name}Response, {entity_name}Update
from app.modules.{module_name}.services.{module_name}_service import {entity_name}Service
from app.modules.{module_name}.repositories.{module_name}_repository import {entity_name}Repository

try:
    from app.database import get_db
    from app.auth.dependencies import get_current_user as _auth_dependency
    _grindx_mode = True
except ImportError:
    from app.core.database_protheus import get_db_protheus as get_db
    from app.core.auth import verify_api_key as _auth_dependency
    _grindx_mode = False

router = APIRouter(prefix="{route_prefix}", tags=["{route_tag}"])


def get_{module_name}_service(db: Session = Depends(get_db)) -> {entity_name}Service:
    repository = {entity_name}Repository(db)
    return {entity_name}Service(repository)


@router.get("", response_model=PaginatedResponse[{entity_name}Response],
    summary="Listar", dependencies=[Depends(_auth_dependency)])
def listar(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    service: {entity_name}Service = Depends(get_{module_name}_service)):
    return service.listar(page, page_size)


@router.get("/{{id}}", response_model={entity_name}Response,
    summary="Buscar por ID", responses={{404: {{"model": ErrorResponse}}}},
    dependencies=[Depends(_auth_dependency)])
def buscar(id: int, service: {entity_name}Service = Depends(get_{module_name}_service)):
    return service.buscar(id)


@router.post("", response_model={entity_name}Response, status_code=201,
    summary="Criar", responses={{409: {{"model": ErrorResponse}}}},
    dependencies=[Depends(_auth_dependency)])
def criar(dados: {entity_name}Create, service: {entity_name}Service = Depends(get_{module_name}_service)):
    return service.criar(dados)


@router.put("/{{id}}", response_model={entity_name}Response,
    summary="Atualizar", responses={{404: {{"model": ErrorResponse}}}},
    dependencies=[Depends(_auth_dependency)])
def atualizar(id: int, dados: {entity_name}Update, service: {entity_name}Service = Depends(get_{module_name}_service)):
    return service.atualizar(id, dados)


@router.delete("/{{id}}", response_model=MessageResponse,
    summary="Desativar", responses={{404: {{"model": ErrorResponse}}}},
    dependencies=[Depends(_auth_dependency)])
def desativar(id: int, service: {entity_name}Service = Depends(get_{module_name}_service)):
    service.desativar(id)
    return MessageResponse(message=f"{entity_name} {{id}} desativado com sucesso.")
```

### 1.7 `__init__.py` files

Each layer directory gets an `__init__.py`:

```python
# schemas/__init__.py
from app.modules.{module_name}.schemas.{module_name} import {entity_name}Create, {entity_name}Update, {entity_name}Response
__all__ = ["{entity_name}Create", "{entity_name}Update", "{entity_name}Response"]

# repositories/__init__.py
from app.modules.{module_name}.repositories.{module_name}_repository import {entity_name}Repository
__all__ = ["{entity_name}Repository"]

# services/__init__.py
from app.modules.{module_name}.services.{module_name}_service import {entity_name}Service
__all__ = ["{entity_name}Service"]

# routers/__init__.py
from app.modules.{module_name}.routers.{module_name}_router import router
__all__ = ["router"]
```

## 2. Tests — conftest.py + Test Files

### 2.1 `tests/conftest.py`

```python
"""
Fixtures para testes do módulo {entity_name}.

Requer a variável de ambiente GRINDX_PACKAGES apontando para o diretório
packages/ do projeto GrindX (ex: D:\\_Projetos\\GrindX\\packages).
"""

import importlib.util
import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

GRINDX_PACKAGES = os.environ.get(
    "GRINDX_PACKAGES",
    str(Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent / "GrindX" / "packages"),
)
GRINDX_API = str(Path(GRINDX_PACKAGES).parent / "apps" / "api-postgres")
LOCAL_MODULES = str(Path(__file__).resolve().parent.parent.parent)

for p in [GRINDX_PACKAGES, GRINDX_API, LOCAL_MODULES]:
    if p not in sys.path:
        sys.path.insert(0, p)

import app  # noqa: E402
import app.modules  # noqa: E402

_local_pkg = Path(LOCAL_MODULES) / "{module_name}"
_spec = importlib.util.spec_from_file_location(
    "app.modules.{module_name}",
    str(_local_pkg / "__init__.py"),
    submodule_search_locations=[str(_local_pkg)],
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["app.modules.{module_name}"] = _mod
_spec.loader.exec_module(_mod)

from app.modules.iam.base import IamBase  # noqa: E402

_SCHEMA_TRANSLATE = {{"iam": None, "portal": None, "catalogo": None, "org": None}}
_all_metadata = IamBase.metadata


@pytest.fixture(scope="function")
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:", connect_args={{"check_same_thread": False}}, poolclass=StaticPool)

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    with engine.execution_options(schema_translate_map=_SCHEMA_TRANSLATE).connect() as conn:
        _all_metadata.create_all(conn)

    TestingSession = sessionmaker(bind=engine.execution_options(schema_translate_map=_SCHEMA_TRANSLATE))
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        with engine.execution_options(schema_translate_map=_SCHEMA_TRANSLATE).connect() as conn:
            _all_metadata.drop_all(conn)


@pytest.fixture
def repository(db_session: Session):
    from app.modules.{module_name}.repositories.{module_name}_repository import {entity_name}Repository
    return {entity_name}Repository(db_session)


@pytest.fixture
def service(repository):
    from app.modules.{module_name}.services.{module_name}_service import {entity_name}Service
    return {entity_name}Service(repository)
```

**NOTA:** O padrão `importlib.util` injeta o módulo local no namespace `app.modules.*` do GrindX, evitando conflito entre o pacote `app` local e o do GrindX.

### 2.2 `tests/test_{module_name}_unit.py`

Testes com repositório mockado (MagicMock):

```python
from unittest.mock import MagicMock
import pytest
from shared.exceptions.base import NotFoundError, ConflictError
from app.modules.{module_name}.schemas.{module_name} import {entity_name}Create, {entity_name}Update
from app.modules.{module_name}.services.{module_name}_service import {entity_name}Service


@pytest.fixture
def mock_repository():
    return MagicMock()


@pytest.fixture
def service(mock_repository):
    return {entity_name}Service(mock_repository)


class TestBuscar:
    def test_quando_encontrado_retorna_objeto(self, service, mock_repository):
        mock_repository.buscar_por_id.return_value = MagicMock(id=1)
        result = service.buscar(1)
        assert result.id == 1
        mock_repository.buscar_por_id.assert_called_once_with(1)

    def test_quando_nao_encontrado_lanca_not_found(self, service, mock_repository):
        mock_repository.buscar_por_id.return_value = None
        with pytest.raises(NotFoundError):
            service.buscar(999)


class TestCriar:
    def test_cria_com_sucesso(self, service, mock_repository):
        mock_repository.criar.return_value = MagicMock(id=1)
        dados = {entity_name}Create(nome="Teste")
        result = service.criar(dados)
        assert result.id == 1
        mock_repository.criar.assert_called_once_with(dados)


class TestAtualizar:
    def test_atualiza_campos_fornecidos(self, service, mock_repository):
        obj = MagicMock(id=1)
        mock_repository.buscar_por_id.return_value = obj
        dados = {entity_name}Update(nome="Novo Nome")
        service.atualizar(1, dados)
        mock_repository.atualizar.assert_called_once_with(obj, dados)


class TestDesativar:
    def test_desativa_recurso_existente(self, service, mock_repository):
        obj = MagicMock(id=1)
        mock_repository.buscar_por_id.return_value = obj
        service.desativar(1)
        mock_repository.desativar.assert_called_once_with(obj)
```

### 2.3 `tests/test_{module_name}_integration.py`

Testes com banco SQLite real (usa fixtures do conftest):

```python
from shared.exceptions.base import NotFoundError, ConflictError
from app.modules.{module_name}.schemas.{module_name} import {entity_name}Create, {entity_name}Update


class TestRepository:
    def test_criar_e_buscar_por_id(self, repository):
        obj = repository.criar({entity_name}Create(nome="Teste"))
        assert obj.id is not None
        assert repository.buscar_por_id(obj.id) is not None

    def test_listar_com_paginacao(self, repository):
        for i in range(5):
            repository.criar({entity_name}Create(nome=f"Item {{i}}"))
        items, total = repository.listar_todos(page=1, page_size=2)
        assert total == 5
        assert len(items) == 2

    def test_atualizar(self, repository):
        obj = repository.criar({entity_name}Create(nome="Original"))
        dados = {entity_name}Update(nome="Alterado")
        atualizado = repository.atualizar(obj, dados)
        assert atualizado.nome == "Alterado"

    def test_desativar(self, repository):
        obj = repository.criar({entity_name}Create(nome="Teste"))
        assert obj.ativo is True
        desativado = repository.desativar(obj)
        assert desativado.ativo is False


class TestService:
    def test_buscar_inexistente_lanca_not_found(self, service):
        with pytest.raises(NotFoundError):
            service.buscar(9999)

    def test_listar_retorna_todos(self, service, repository):
        for i in range(3):
            repository.criar({entity_name}Create(nome=f"Item {{i}}"))
        result = service.listar()
        assert result.total == 3
```

## 3. Frontend

> **Siga o padrão escolhido no Tech Stack Questionnaire (seção inicial).**
>
> Se o usuário escolheu **(A) Padrão GrindX** (HTML puro + CSS puro + Vanilla JS), use as seções 3.1–3.3 abaixo.
>
> Se escolheu **(B) Outro padrão**, adapte para o tech stack especificado. Neste caso, ignore seções 3.1–3.3 e crie o frontend conforme combinado, mas mantenha a estrutura de diretórios `frontend/index.html`, `frontend/script.js`, `frontend/style.css` (com o conteúdo adaptado para o framework/biblioteca escolhido).

### 3.1 `style.css` — Apenas layout, herda skins

```css
@import url('../../shared/core.css');

.page-container {{ padding: var(--space-6); }}
.page-header {{ display: flex; flex-direction: column; align-items: flex-start; margin-bottom: var(--space-6); }}

/* Buttons — padrão GrindX (core.css) */
.btn {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-2) var(--space-4);
    border-radius: 0.5rem;
    font-family: inherit;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
    min-height: 44px;
    gap: var(--space-2);
}}
.btn-primary {{ background: var(--primary); color: white; }}
.btn-primary:hover {{ background: var(--primary-hover); transform: translateY(-1px); }}
.btn-primary:focus {{ outline: 3px solid var(--focus-ring); outline-offset: 2px; }}
.btn-secondary {{ background: var(--border-color); color: var(--text-main); }}
.btn-secondary:hover {{ background: var(--text-muted); color: white; }}
.btn-danger {{ background: var(--danger); color: white; }}
.btn-danger:hover {{ filter: brightness(0.9); transform: translateY(-1px); }}
.btn-outline {{ border: 1px solid var(--border-color); background: transparent; color: var(--text-main); }}
.btn-outline:hover {{ background: var(--accent); }}
.btn-sm {{ padding: var(--space-1) var(--space-2); min-height: 32px; font-size: 0.8rem; }}
.btn:disabled {{ cursor: not-allowed; opacity: 0.65; transform: none; }}
.btn-icon {{
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 1.25rem;
    color: var(--text-muted);
    transition: color 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 0.25rem;
}}
.btn-icon:hover {{ color: var(--text-main); background: rgba(0,0,0,0.05); }}

/* Modal — padrão GrindX skins (modal-overlay + modal-card) */
.modal-overlay {{
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.6);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: var(--space-4);
}}
.modal-card {{
    background: var(--bg-card);
    width: 100%;
    max-width: 600px;
    border-radius: 0.5rem;
    padding: var(--space-8);
    box-shadow: 0 20px 25px -5px rgba(0,0,0,0.2);
}}
.modal-card--sm {{ max-width: 400px; }}
.modal-header {{
    margin-bottom: var(--space-4);
    border-bottom: 1px solid var(--border-color);
    padding-bottom: var(--space-2);
}}
.modal-header h2 {{ margin: 0; font-size: var(--font-size-xl); }}
.modal-body {{ display: flex; flex-direction: column; gap: var(--space-4); }}
.modal-footer {{
    margin-top: var(--space-4);
    padding-top: var(--space-4);
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: flex-end;
    gap: var(--space-2);
}}
.hidden {{ display: none !important; }}
```

**Regras de herança de skins:**
- Usar exclusivamente `var(--...)` para cores, fontes, espaçamentos
- **Nunca** definir cores fixas, fontes ou breakpoints
- Apenas regras de layout (grid, flex, widths, margins, padding)
- Testar visualmente com pelo menos 2 skins antes de exportar
- Botões e modais seguem o padrão canonical do `core.css` do GrindX
- Modal usa `modal-overlay` + `modal-card` (NÃO `<dialog>` nativo)

### 3.2 `index.html` e `script.js` (Padrão GrindX — HTML puro + CSS puro + Vanilla JS)

**`index.html`:**
- HTML5 semântico, **zero dependências externas** (sem CDN, sem bibliotecas, sem frameworks)
- Modais usando `<div class="modal-overlay" style="display: none;">` + `<div class="modal-card">` com toggle via `style.display`
- Atributos de acessibilidade: `role="dialog"`, `aria-modal="true"`, `aria-labelledby`
- Botão fechar com `btn-icon` e `&times;`
- Footer com `modal-footer flex justify-end gap-2`
- Templates de cards usando `<template>` ou template strings no JS
- Atributos `data-*` para binding de eventos via delegated events
- IDs únicos para binds, classes para estilização
- Estrutura: `<div class="page-container">` → cabeçalho + grid + empty state + modais

**Estrutura padrão do modal:**
```html
<div class="modal-overlay" id="modal-id" role="dialog" aria-modal="true" aria-labelledby="modal-title" style="display: none;">
  <div class="modal-card">
    <header class="modal-header flex justify-between">
      <h3 id="modal-title">Título</h3>
      <button class="btn-icon" id="close-modal" aria-label="Fechar">&times;</button>
    </header>
    <form id="form-id" class="grid grid-md-2">
      <!-- campos do formulário -->
    </form>
    <footer class="modal-footer flex justify-end gap-2">
      <button type="button" class="btn" id="btn-cancel">Cancelar</button>
      <button type="button" class="btn btn-primary" id="btn-save">Salvar</button>
    </footer>
  </div>
</div>
```

**`script.js`:**
- Vanilla JS puro, sem classes de framework, sem TypeScript
- Padrão Controller com objeto literal ou funções modulares
- Chamadas API com `fetch()` puro (encapsulado em objeto `api`)
- Estado local em arrays/objetos globais (escopo do módulo)
- Renderização via template strings: `innerHTML` ou `insertAdjacentHTML`
- Eventos via delegated event bubbling no container pai
- Ciclo de vida: `DOMContentLoaded` → `init()` → carregar dados → renderizar

**Arquitetura do script.js:**
```javascript
// Estado
let items = []
let editingId = null

// API calls
const api = {
  async listar() { return fetch('/v1/...').then(r => r.json()) },
  async criar(dados) { return fetch('/v1/...', { method: 'POST', body: JSON.stringify(dados), headers: {'Content-Type': 'application/json'} }).then(r => r.json()) },
  async atualizar(id, dados) { return fetch(`/v1/.../${id}`, { method: 'PUT', body: JSON.stringify(dados), headers: {'Content-Type': 'application/json'} }).then(r => r.json()) },
  async excluir(id) { return fetch(`/v1/.../${id}`, { method: 'DELETE' }).then(r => r.json()) },
}

// Render
function renderizar() { /* template strings -> innerHTML */ }
function abrirModal(item) { /* editingId = item?.id, preencher form, style.display = 'flex' */ }
function fecharModal() { /* style.display = 'none' */ }

// Handlers
async function handleSubmit(e) { /* ... */ }
async function handleDelete(id) { /* ... */ }

// Init
document.addEventListener('DOMContentLoaded', async () => {
  items = await api.listar()
  renderizar()
  // binds de eventos
})
```

**Regras:**
- NUNCA importar bibliotecas externas (React, Vue, jQuery, Axios, etc.)
- NUNCA usar TypeScript no frontend (apenas JS puro com `// @ts-nocheck` se necessário)
- Eventos de clique em ações (editar/excluir) usam `data-action` + `e.target.closest()` no container
- Modais usam `style.display = 'flex'` para abrir e `style.display = 'none'` para fechar
- Modais devem ter `role="dialog"`, `aria-modal="true"`, `aria-labelledby`
- Botão fechar deve ter `aria-label="Fechar"`

**Dual-context auth (GrindX JWT vs Standalone API Key):**

O frontend deve detectar se está rodando dentro do GrindX e usar o wrapper de API correto:

```javascript
// Detectar contexto (session existe via app.js, que é compartilhado)
const _isGrindx = typeof window !== 'undefined' && window.grindx && window.grindx.session;

// Helper: fetch com auth automática
async function _fetch(url, options) {
    const headers = {};
    if (_isGrindx) {
        const token = window.grindx.session.getToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;
    } else if (API_KEY) {
        headers['X-API-Key'] = API_KEY;
    }
    const response = await fetch(url, { ...options, headers: { ...headers, ...options?.headers } });
    return response.json();
}

// Helper: download de PDF/binário
function downloadFromUrl(url, filename) {
    if (_isGrindx) {
        const token = window.grindx.session.getToken();
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        fetch(url, { headers })
            .then(res => { if (!res.ok) throw new Error('Erro ao baixar'); return res.blob(); })
            .then(blob => {
                const blobUrl = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = blobUrl; a.download = filename;
                document.body.appendChild(a); a.click();
                setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(blobUrl); }, 1000);
            });
    } else {
        const urlWithKey = API_KEY ? url + (url.includes('?') ? '&' : '?') + 'api_key=' + API_KEY : url;
        const a = document.createElement('a');
        a.href = urlWithKey; a.download = filename;
        document.body.appendChild(a); a.click();
        setTimeout(() => document.body.removeChild(a), 1000);
    }
}
```

**IMPORTANTE:** O módulo DEVE incluir `app.js` no `<head>` para ter acesso a `window.grindx.session`:
```html
<script src="../../shared/app.js"></script>
<script src="script.js" defer></script>
```

- **GrindX**: `window.grindx.session.getToken()` retorna o JWT (via `localStorage.access_token`)
- **Standalone**: usa `X-API-Key` header
- Para PDFs standalone, usa `?api_key=` query param (pois downloads não suportam headers custom)
- **NÃO usar `window.grindx.api`** — ele aponta para api-postgres (porta 8002), não api-sqlserver

## 4. Migration

```python
"""criar tabela {table_name}

Revision ID: {{revision}}
Revises: {{down_revision}}
Create Date: {{date}}
"""

from typing import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "{{revision}}"
down_revision: str | None = "{{down_revision}}"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "{table_name}",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="{schema_name}",
    )


def downgrade() -> None:
    op.drop_table("{table_name}", schema="{schema_name}")
```

## 5. Support Files

### `run_tests.ps1`

```powershell
param(
    [string]$GrindxPackages = "D:\\_Projetos\\GrindX\\packages",
    [switch]$Verbose
)
$env:GRINDX_PACKAGES = $GrindxPackages
$pytestArgs = @("-v")
if ($Verbose) {{ $pytestArgs += "--tb=long" }} else {{ $pytestArgs += "--tb=short" }}
python -m pytest "app/modules/{module_name}/tests/" @pytestArgs
```

### `requirements.txt`

```
pytest>=8.0
sqlalchemy>=2.0
pydantic>=2.0
structlog>=24.0
fastapi>=0.110
```

### `pytest.ini`

```ini
[pytest]
testpaths = app/modules/{module_name}/tests
```

### `Makefile`

Cross-platform Makefile (funciona no Linux, Mac e Windows com GnuMake):

```makefile
# ==========================================
# Módulo {entity_name} — Standalone
# ==========================================

MODULE := {module_name}
ENTITY := {entity_name}

.PHONY: test test-unit test-integration package export dry-run clean help

# ==========================================
# Testes
# ==========================================

test:
	@python -m pytest app/modules/$(MODULE)/tests/ -v --tb=short

test-unit:
	@python -m pytest app/modules/$(MODULE)/tests/ -v --tb=short -k "unit"

test-integration:
	@python -m pytest app/modules/$(MODULE)/tests/ -v --tb=short -k "integration"

# ==========================================
# Empacotamento & Exportação
# ==========================================

package:
	@python -m app.modules.$(MODULE).export package
	@echo.
	@echo Zip gerado: dist/modulo-$(MODULE).zip
	@echo Estrutura:
	@python -c "import zipfile; [print('  ' + f) for f in zipfile.ZipFile('dist/modulo-$(MODULE).zip').namelist()[:10]]"
	@python -c "import zipfile; n=len(zipfile.ZipFile('dist/modulo-$(MODULE).zip').namelist()); print(f'  ... ({n} arquivos total)')"

dry-run:
	@python -m app.modules.$(MODULE).export package --dry-run

export:
	@python -m app.modules.$(MODULE).export

export-dry:
	@python -m app.modules.$(MODULE).export --dry-run

# ==========================================
# Importação
# ==========================================

import: package
	@echo.
	@echo Copiando zip para import/ do GrindX...
	@python -c "import shutil,os; os.makedirs('../GrindX/import',exist_ok=True); shutil.copy2('dist/modulo-$(MODULE).zip','../GrindX/import/'); print('Copiado para ../GrindX/import/modulo-$(MODULE).zip')"
	@echo.
	@echo Proximo passo: importar via API ou frontend
	@echo   API:  curl -X POST -H "Authorization: Bearer ^<token^>" "http://localhost:8000/v1/import/$(MODULE)?force=true"
	@echo   Frontend: Gestao -> Importar Modulos -> $(ENTITY) -> Importar

# ==========================================
# Utilitários
# ==========================================

clean:
	@echo Limpando caches...
	@if exist dist rmdir /s /q dist
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	@if exist .pytest_cache rmdir /s /q .pytest_cache
	@echo Limpeza concluida

help:
	@echo.
	@echo Modulo $(ENTITY) — Comandos disponibles:
	@echo.
	@echo   make test             Roda todos os testes
	@echo   make test-unit        Roda apenas testes unitarios
	@echo   make test-integration Roda apenas testes de integracao
	@echo   make package          Gera o zip para importacao
	@echo   make dry-run          Simula a geracao do zip
	@echo   make export           Exporta direto para o GrindX (CLI)
	@echo   make import           Gera zip + copia para import/ do GrindX
	@echo   make clean            Limpa caches e __pycache__
	@echo   make help             Exibe esta ajuda
	@echo
```

## 6. Manifesto (`module.json`)

Criar `module.json` na raiz do standalone com os metadados do módulo. Este arquivo é usado pelo sistema de importação do GrindX.

```json
{
  "module_name": "{module_name}",
  "entity_name": "{entity_name}",
  "version": "1.0.0",
  "schema_name": "{schema_name}",
  "tables": ["{table_name}"],
  "route_prefix": "{route_prefix}",
  "route_tag": "{route_tag}",
  "frontend_tabs": [
    {
      "name": "Nome da Aba",
      "url": "modules/{frontend_prefix}_{aba}/index.html",
      "menu_icone": "icon-name",
      "order": 1
    }
  ],
  "menu_label": "{menu_label}",
  "menu_icone": "folder",
  "role_minima": "operador",
  "dependencies": []
}
```

**Campos do `frontend_tabs`:**
- `name`: Nome da aba exibido no menu
- `url`: Caminho relativo ao `frontend-webapp/modules/`
- `menu_icone`: Nome do ícone (Font Awesome sem `fa-`)
- `order`: Ordem de exibição no menu

**Nota:** O `register_menu` no GrindX apenas loga as informações do módulo. A associação com abas deve ser feita manualmente no Portal → Estrutura após a importação.

O `module.json` deve ser incluído no `.zip` gerado pelo comando `package` do `export.py`.

Para o procedimento completo de importação via zip, veja `docs/IMPORTACAO.md`.

## 7. export.py

Criar `app/modules/{module_name}/export.py`:

```python
"""
export.py — Exporta o módulo {entity_name} para o sistema GrindX.

Uso:
    python -m app.modules.{module_name}.export [--dry-run] [--grindx-root PATH]

Sem --dry-run, copia arquivos e registra.
Com --dry-run, apenas exibe o que seria feito.
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)

MODULE_NAME = "{entity_name}"
MODULE_SRC = Path(__file__).parent
STANDALONE_ROOT = MODULE_SRC.parent.parent.parent  # raiz do modulo-{module_name}/
GRINDX_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent / "GrindX"
# Alterar para "api-sqlserver" se o módulo usa SQL Server (Protheus)
# Backend fica em apps/, frontend em packages/
GRINDX_API = GRINDX_ROOT / "apps" / "api-postgres"
GRINDX_FRONTEND = GRINDX_ROOT / "packages" / "frontend-webapp"
FRONTEND_SRC = STANDALONE_ROOT / "frontend"
MIGRATION_SRC = STANDALONE_ROOT / "migration"

ROUTER_IMPORT = "from app.modules.{module_name}.routers.{module_name}_router import router as {module_name}_router"
ROUTER_REGISTER = "app.include_router({module_name}_router)"


def copy_backend(dry_run: bool = False):
    dest = GRINDX_API / "app" / "modules" / "{module_name}"
    if dry_run:
        logger.info("[DRY-RUN] Copiaria %%s -> %%s", MODULE_SRC, dest)
    else:
        if dest.exists(): shutil.rmtree(dest)
        shutil.copytree(MODULE_SRC, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        logger.info("Backend copiado")


def copy_frontend(dry_run: bool = False):
    dest_base = GRINDX_FRONTEND / "modules"
    if dry_run:
        logger.info("[DRY-RUN] Copiaria sub-modulos de %%s -> %%s", FRONTEND_SRC, dest_base)
    else:
        for sub in FRONTEND_SRC.iterdir():
            if sub.is_dir():
                dest = dest_base / sub.name
                if dest.exists(): shutil.rmtree(dest)
                shutil.copytree(sub, dest)
                logger.info("Frontend copiado: %%s -> %%s", sub.name, dest)
            elif sub.is_file():
                dest = dest_base / sub.name
                shutil.copy2(sub, dest)
                logger.info("Arquivo copiado: %%s", sub.name)


def copy_migration(dry_run: bool = False):
    dest = GRINDX_API / "alembic" / "versions"
    if dry_run:
        logger.info("[DRY-RUN] Copiaria migrations de %%s -> %%s", MIGRATION_SRC, dest)
    else:
        for f in MIGRATION_SRC.glob("*.py"):
            shutil.copy2(f, dest / f.name)
            logger.info("Migration %%s copiada", f.name)


def register_routes(dry_run: bool = False):
    main_py = GRINDX_API / "app" / "main.py"
    content = main_py.read_text(encoding="utf-8")
    if ROUTER_IMPORT in content:
        logger.info("Rotas já registradas")
        return
    lines = content.splitlines(keepends=True)
    last_import = last_include = None
    for i, line in enumerate(lines):
        if "from app." in line and "import router as" in line: last_import = i
        if "app.include_router(" in line: last_include = i
    if last_import is not None:
        lines.insert(last_import + 1, ROUTER_IMPORT + "\\n")
        if last_include is not None and last_include >= last_import: last_include += 1
    if last_include is not None:
        lines.insert(last_include + 1, ROUTER_REGISTER + "\\n")
    if dry_run:
        logger.info("[DRY-RUN] main.py alterado")
    else:
        main_py.write_text("".join(lines), encoding="utf-8")
        logger.info("Rotas registradas")


def register_dependency(dry_run: bool = False):
    deps_py = GRINDX_API / "app" / "auth" / "dependencies.py"
    content = deps_py.read_text(encoding="utf-8")
    marker = "# --- Versões vinculadas das permissões ---"
    factory = (
        "from app.modules.{module_name}.repositories.{module_name}_repository import {entity_name}Repository\\n"
        "from app.modules.{module_name}.services.{module_name}_service import {entity_name}Service\\n\\n\\n"
        "def get_{module_name}_service(db: Session = Depends(get_db)) -> {entity_name}Service:\\n"
        '    """Factory para o {entity_name}Service."""\\n'
        "    repository = {entity_name}Repository(db)\\n"
        "    return {entity_name}Service(repository)\\n\\n\\n"
        f"{{marker}}\\n"
    )
    if "get_{module_name}_service" in content:
        logger.info("Dependency já registrada")
        return
    if dry_run:
        logger.info("[DRY-RUN] auth/dependencies.py alterado")
    else:
        deps_py.write_text(content.replace(marker, factory), encoding="utf-8")
        logger.info("Dependency registrada")


def register_alembic_import(dry_run: bool = False):
    env_py = GRINDX_API / "alembic" / "env.py"
    content = env_py.read_text(encoding="utf-8")
    line = "from app.modules.{module_name}.models.{module_name} import {entity_name}  # noqa: F401"
    if line in content:
        logger.info("Import já registrado")
        return
    marker = "from app.modules.portal.models.portal import Aba, Modulo  # noqa: F401"
    if dry_run:
        logger.info("[DRY-RUN] alembic/env.py alterado")
    else:
        env_py.write_text(content.replace(marker, marker + "\\n" + line), encoding="utf-8")
        logger.info("Import registrado")


def run_migrations(dry_run: bool = False):
    cmd = [sys.executable, "-m", "alembic", "upgrade", "head"]
    if dry_run:
        logger.info("[DRY-RUN] Comando: %%s", " ".join(cmd))
    else:
        result = subprocess.run(cmd, cwd=GRINDX_API, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            logger.error("Migration falhou", stderr=result.stderr)
            raise RuntimeError(f"Migration error: {{result.stderr}}")
        logger.info("Migrations executadas")


def package(dry_run: bool = False):
    """Empacota o módulo em um .zip com module.json para distribuição.

    IMPORTANTE: O frontend no zip deve ser `frontend/custos/...`, NÃO `frontend/modules/custos/`.
    O GrindX importer coloca os arquivos de frontend em `modules/`, então se o zip
    tiver `frontend/modules/custos/`, o resultado será `modules/frontend/modules/custos/` (caminho errado).
    """
    module_dir = MODULE_SRC
    frontend_dir = FRONTEND_SRC
    migration_dir = MIGRATION_SRC
    dist_dir = STANDALONE_ROOT / "dist"
    zip_path = dist_dir / f"modulo-{MODULE_NAME.lower()}.zip"

    if dry_run:
        logger.info("[DRY-RUN] Criaria %s com:", zip_path)
        logger.info("  - module.json")
        logger.info("  - app/modules/%s/", MODULE_NAME)
        logger.info("  - frontend/")
        logger.info("  - migration/")
        return

    dist_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        manifest_path = STANDALONE_ROOT / "module.json"
        if manifest_path.exists():
            zf.write(manifest_path, "module.json")

        # Backend: mantém app/modules/{module_name}/ no zip
        for file in module_dir.rglob("*"):
            if file.is_file() and "__pycache__" not in file.parts and not file.name.endswith(".pyc"):
                arcname = str(file.relative_to(STANDALONE_ROOT))
                zf.write(file, arcname)

        if frontend_dir.exists():
            for file in frontend_dir.rglob("*"):
                if file.is_file():
                    # Remove prefixo 'modules/' para evitar path duplicado no importer
                    # frontend/modules/gp_dashboard/ → frontend/gp_dashboard/
                    rel = file.relative_to(frontend_dir)
                    parts = list(rel.parts)
                    if parts and parts[0] == "modules":
                        parts = parts[1:]
                    arcname = str(Path("frontend") / Path(*parts))
                    zf.write(file, arcname)

        if migration_dir.exists():
            for file in migration_dir.glob("*.py"):
                zf.write(file, f"migration/{file.name}")

    logger.info("Pacote criado: %s", zip_path)


def export(dry_run: bool = False):
    logger.info("Exportando módulo %%s", MODULE_NAME, dry_run=dry_run)
    copy_backend(dry_run)
    copy_frontend(dry_run)
    copy_migration(dry_run)
    register_routes(dry_run)
    register_dependency(dry_run)
    register_alembic_import(dry_run)
    run_migrations(dry_run)
    logger.info("Módulo exportado com sucesso")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Ferramentas do módulo {{MODULE_NAME}}")
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    # export
    export_parser = subparsers.add_parser("export", help="Exporta para o GrindX")
    export_parser.add_argument("--dry-run", action="store_true", help="Apenas simula")
    export_parser.add_argument("--grindx-root", default=None, help="Raiz do GrindX")

    # package
    pkg_parser = subparsers.add_parser("package", help="Empacota como .zip")
    pkg_parser.add_argument("--dry-run", action="store_true", help="Apenas simula")

    args = parser.parse_args()

    if args.command == "package":
        package(dry_run=args.dry_run)
    elif args.command == "export":
        if getattr(args, "grindx_root", None):
            global GRINDX_ROOT, GRINDX_API, GRINDX_FRONTEND
            GRINDX_ROOT = Path(args.grindx_root)
            GRINDX_API = GRINDX_ROOT / "apps" / "api-postgres"
            GRINDX_FRONTEND = GRINDX_ROOT / "packages" / "frontend-webapp"
        export(dry_run=args.dry_run)
```

## 8. Execution / Test Workflow

```powershell
# 1. Criar estrutura do módulo
# (seguir os templates acima manualmente ou com subagent)

# 2. Rodar testes (independente, fora do GrindX)
make test                                          # via Makefile
# ou manualmente:
$env:GRINDX_PACKAGES = "D:\\_Projetos\\GrindX\\packages"
python -m pytest app/modules/{module_name}/tests/ -v
# Esperado: 10+ testes PASS

# 3. Gerar pacote .zip (após testes verdes)
make package                                       # via Makefile
# ou manualmente:
python -m app.modules.{module_name}.export package

# 4. Verificar estrutura do zip
# (o make package já exibe a estrutura)
# ou manualmente:
python -c "import zipfile; [print(f) for f in zipfile.ZipFile('dist/modulo-{module_name}.zip').namelist()]"

# 5. Importar no GrindX
make import                                        # gera zip + copia para import/
# ou manualmente:
Copy-Item dist\modulo-{module_name}.zip D:\_Projetos\GrindX\import\
# Via API: POST /v1/import/{module_name}
# Via frontend: Gestão → Importar Módulos
# Veja docs/IMPORTACAO.md para procedimento completo e ordem de importação

# 6. Exportar para o GrindX (via CLI, alternativa ao .zip)
make export                                        # via Makefile
# ou manualmente:
python -m app.modules.{module_name}.export

# 7. Verificar no GrindX
cd D:\\_Projetos\\GrindX\\packages\\api-postgres
pytest tests/ -k {module_name} -v
```

## Registration Checklist

- [ ] **Tech Stack definido**: Padrão GrindX (HTML puro + CSS puro + Vanilla JS + PostgreSQL) ou padrão alternativo especificado
- [ ] **Frontend prefix definido**: Prefixo abreviado para sub-módulos (ex: `gp` para gestao_projetos)
- [ ] **Frontend tabs definido**: Array de abas com name, url, menu_icone, order
- [ ] Backend: base, model, schemas, repository, service, router + __init__.py
- [ ] **Router dual-context**: try/except para `get_db`/`get_current_user` (GrindX) vs `get_db_protheus`/`verify_api_key` (standalone)
- [ ] **Frontend dual-context**: `_fetch()` e `downloadFromUrl()` com detecção `window.grindx.session` + `index.html` inclui `app.js`
- [ ] **PDF opcional**: se módulo gera PDF, instalar `xhtml2pdf` no venv do GrindX (`pip install xhtml2pdf`)
- [ ] Tests: conftest.py (com padrão `importlib.util`), unit tests (mocked repo), integration tests (SQLite)
- [ ] Migration: Alembic migration file (PostgreSQL) — ou diretório vazio para módulos read-only
- [ ] Frontend: sub-módulos com prefixo (ex: `gp_dashboard/`, `gp_projeto/`), cada um com index.html, script.js, style.css
- [ ] Modal: padrão `modal-overlay` + `modal-card` com `style.display`, `role="dialog"`, `aria-modal`, `aria-labelledby`
- [ ] Support: requirements.txt, pytest.ini, run_tests.ps1, Makefile
- [ ] Testes passam: `pytest app/modules/{module_name}/tests/ -v`
- [ ] `module.json` criado na raiz do standalone com `frontend_tabs` array
- [ ] `export.py`: usa `STANDALONE_ROOT` para paths de frontend, migration e dist
- [ ] `export.py`: `copy_frontend` copia sub-módulos para `modules/` (raiz)
- [ ] `export.py`: `--dry-run` simula sem alterar GrindX
- [ ] `export.py`: `--grindx-root` aceita caminho customizado
- [ ] `export.py`: comando `package` gera `.zip` com estrutura compatível com o importer
- [ ] Herança de skins: style.css usa `var(--...)`, sem cores fixas
- [ ] Zip verificado: `module.json` na raiz, `app/modules/{name}/` na raiz, `frontend/` na raiz (sem `modules/` extra)
- [ ] **Pós-importação**: Associar abas manualmente no Portal → Estrutura
