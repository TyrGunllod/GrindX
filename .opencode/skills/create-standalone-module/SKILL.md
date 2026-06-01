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

| Opção | Frontend | CSS | JS | Banco | Backend |
|-------|----------|-----|----|-------|---------|
| **(A) Padrão GrindX** (Recomendado) | HTML puro | CSS puro (`var(--...)`, Grid, Flex) | Vanilla JS (fetch, template strings, delegated events) | PostgreSQL (via SQLAlchemy + Alembic) | FastAPI + SQLAlchemy |
| **(B) Outro padrão** | Especificar | Especificar | Especificar | Especificar | Especificar |

- Se escolher **(A)**, siga os templates padrão desta skill (frontend: `index.html`, `script.js`, `style.css` sem dependências; backend: FastAPI + SQLAlchemy + PostgreSQL via Alembic).
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
| 8 | `frontend_path` | "Caminho onde os arquivos frontend serão criados no portal (ex: `modules/recursos`)." | `modules/recursos` | `modules/{module_name}` |
| 9 | `menu_label` | "Rótulo que aparece no menu lateral do portal para este módulo." | `"Recursos"` | `{entity_name}` |
| 10 | `header_title` | "Título que aparece no cabeçalho da página do módulo (ex: \"Gerenciamento de Recursos\")." | `"Gerenciamento de Recursos"` | `"Gerenciamento de {entity_name}"` |
| 11 | `header_description` | "Subtítulo/descrição que aparece abaixo do título no cabeçalho." | `"Cadastro e controle de recursos do sistema."` | `"Módulo de {menu_label} do GrindX."` |

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
├── frontend/                                    # Vanilla JS frontend
│   ├── index.html
│   ├── script.js
│   └── style.css                               # Skin-inheriting (var(--...))
├── migration/
│   └── {revision}_{table_name}.py              # Alembic migration
├── requirements.txt                             # Dependencies
├── pytest.ini
└── run_tests.{ps1|sh}                           # Test runner script
```

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
- `{header_title}` — page header title
- `{header_description}` — page header subtitle

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

```python
from fastapi import APIRouter, Depends, Query
from shared.schemas.base import ErrorResponse, MessageResponse, PaginatedResponse
from shared.security.permissions import Role

from app.auth.dependencies import get_{module_name}_service, require_role
from app.modules.{module_name}.schemas.{module_name} import {entity_name}Create, {entity_name}Response, {entity_name}Update
from app.modules.{module_name}.services.{module_name}_service import {entity_name}Service

router = APIRouter(prefix="{route_prefix}", tags=["{route_tag}"])


@router.get("", response_model=PaginatedResponse[{entity_name}Response],
    summary="Listar", dependencies=[Depends(require_role(Role.ADMIN, Role.OPERADOR, Role.LEITURA))])
def listar(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    service: {entity_name}Service = Depends(get_{module_name}_service)):
    return service.listar(page, page_size)


@router.get("/{{id}}", response_model={entity_name}Response,
    summary="Buscar por ID", responses={{404: {{"model": ErrorResponse}}}},
    dependencies=[Depends(require_role(Role.ADMIN, Role.OPERADOR, Role.LEITURA))])
def buscar(id: int, service: {entity_name}Service = Depends(get_{module_name}_service)):
    return service.buscar(id)


@router.post("", response_model={entity_name}Response, status_code=201,
    summary="Criar", responses={{409: {{"model": ErrorResponse}}}},
    dependencies=[Depends(require_role(Role.ADMIN, Role.OPERADOR))])
def criar(dados: {entity_name}Create, service: {entity_name}Service = Depends(get_{module_name}_service)):
    return service.criar(dados)


@router.put("/{{id}}", response_model={entity_name}Response,
    summary="Atualizar", responses={{404: {{"model": ErrorResponse}}}},
    dependencies=[Depends(require_role(Role.ADMIN, Role.OPERADOR))])
def atualizar(id: int, dados: {entity_name}Update, service: {entity_name}Service = Depends(get_{module_name}_service)):
    return service.atualizar(id, dados)


@router.delete("/{{id}}", response_model=MessageResponse,
    summary="Desativar", responses={{404: {{"model": ErrorResponse}}}},
    dependencies=[Depends(require_role(Role.ADMIN))])
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
if GRINDX_PACKAGES not in sys.path:
    sys.path.insert(0, GRINDX_PACKAGES)

from app.modules.iam.base import IamBase

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
```

**Regras de herança de skins:**
- Usar exclusivamente `var(--...)` para cores, fontes, espaçamentos
- **Nunca** definir cores fixas, fontes ou breakpoints
- Apenas regras de layout (grid, flex, widths, margins, padding)
- Testar visualmente com pelo menos 2 skins antes de exportar

### 3.1.1 Header Padrão (Obrigatório)

Todo módulo GrindX **deve** usar este padrão de header no `index.html`. Copie diretamente, substituindo apenas `{titulo}`, `{descricao}` e os botões de ação.

**Referência:** `Preview/preview.html` (linhas 12–22)

```html
<header class="page-header mb-8">
    <div>
        <h1>{titulo}</h1>
        <p class="text-muted">{descricao}</p>
    </div>
    <div class="actions-group" style="margin-top: var(--space-4);">
        <!-- Botões de ação do módulo aqui -->
    </div>
</header>
```

**Regras obrigatórias:**
- `<header class="page-header mb-8">` — **sem** classes `flex`, `justify-between`, `items-center`
- `<div class="actions-group" style="margin-top: var(--space-4);">` — **sempre** incluir o `style` com `margin-top: var(--space-4)`
- O `<div>` interno agrupa título + subtítulo; o `<div class="actions-group">` agrupa botões
- Botões usam classes `btn`, `btn-primary`, `btn-secondary`, etc. + ícones Font Awesome

**Exemplo com botões:**
```html
<header class="page-header mb-8">
    <div>
        <h1>Gerenciamento de Recursos</h1>
        <p class="text-muted">Cadastro e controle de recursos do sistema.</p>
    </div>
    <div class="actions-group" style="margin-top: var(--space-4);">
        <button class="btn" id="btnRefresh" title="Recarregar">
            <i class="fas fa-sync-alt"></i>
        </button>
        <button class="btn btn-primary" id="btnNovo">
            <i class="fas fa-plus"></i> <span class="hide-mobile">Novo Recurso</span>
        </button>
    </div>
</header>
```

### 3.2 `index.html` e `script.js` (Padrão GrindX — HTML puro + CSS puro + Vanilla JS)

**`index.html`:**
- HTML5 semântico, **zero dependências externas** (sem CDN, sem bibliotecas, sem frameworks)
- Modais usando `<dialog>` nativo com `<form method="dialog">`
- Templates de cards usando `<template>` ou template strings no JS
- Atributos `data-*` para binding de eventos via delegated events
- IDs únicos para binds, classes para estilização
- Estrutura: `<div class="page-container">` → cabeçalho (usar padrão 3.1.1) + grid + empty state + modais

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
  async listar() { return fetch('/api/v1/...').then(r => r.json()) },
  async criar(dados) { return fetch('/api/v1/...', { method: 'POST', body: JSON.stringify(dados), headers: {'Content-Type': 'application/json'} }).then(r => r.json()) },
  async atualizar(id, dados) { return fetch(`/api/v1/.../${id}`, { method: 'PUT', body: JSON.stringify(dados), headers: {'Content-Type': 'application/json'} }).then(r => r.json()) },
  async excluir(id) { return fetch(`/api/v1/.../${id}`, { method: 'DELETE' }).then(r => r.json()) },
}

// Render
function renderizar() { /* template strings -> innerHTML */ }
function abrirModal(item) { /* editingId = item?.id, preencher form, dialog.showModal() */ }
function fecharModal() { /* dialog.close() */ }

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
- Modais usam `<dialog>.showModal()` e `<dialog>.close()`

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

## 6. Manifesto (`module.json`)

Criar `module.json` na raiz do standalone com os metadados do módulo. Este arquivo é usado pelo sistema de importação do GrindX.

```json
{
  "module_name": "{module_name}",
  "entity_name": "{entity_name}",
  "version": "1.0.0",
  "schema_name": "{schema_name}",
  "table_name": "{table_name}",
  "route_prefix": "{route_prefix}",
  "route_tag": "{route_tag}",
  "frontend_url": "{frontend_path}/index.html",
  "menu_label": "{menu_label}",
  "menu_icone": "folder",
  "role_minima": "operador",
  "dependencies": []
}
```

O `module.json` deve ser incluído no `.zip` gerado pelo comando `package` do `export.py`.

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
GRINDX_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent / "GrindX"
GRINDX_API = GRINDX_ROOT / "packages" / "api-postgres"
GRINDX_FRONTEND = GRINDX_ROOT / "packages" / "frontend-webapp"
FRONTEND_SRC = MODULE_SRC.parent.parent.parent.parent.parent / "frontend"
MIGRATION_SRC = MODULE_SRC.parent.parent.parent.parent.parent / "migration"

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
    dest = GRINDX_FRONTEND / "modules" / "{module_name}"
    if dry_run:
        logger.info("[DRY-RUN] Copiaria %%s -> %%s", FRONTEND_SRC, dest)
    else:
        if dest.exists(): shutil.rmtree(dest)
        shutil.copytree(FRONTEND_SRC, dest)
        logger.info("Frontend copiado")


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
    """Empacota o módulo em um .zip com module.json para distribuição."""
    module_dir = MODULE_SRC
    frontend_dir = FRONTEND_SRC
    migration_dir = MIGRATION_SRC
    dist_dir = module_dir.parent.parent.parent.parent.parent / "dist"
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
        manifest_path = MODULE_SRC.parent / "module.json"
        if manifest_path.exists():
            zf.write(manifest_path, "module.json")

        for file in MODULE_SRC.rglob("*"):
            if file.is_file() and "__pycache__" not in file.parts and not file.name.endswith(".pyc"):
                arcname = str(file.relative_to(MODULE_SRC.parent.parent.parent.parent.parent))
                zf.write(file, arcname)

        if frontend_dir.exists():
            for file in frontend_dir.rglob("*"):
                if file.is_file():
                    arcname = str(Path("frontend") / file.relative_to(frontend_dir))
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
            GRINDX_API = GRINDX_ROOT / "packages" / "api-postgres"
            GRINDX_FRONTEND = GRINDX_ROOT / "packages" / "frontend-webapp"
        export(dry_run=args.dry_run)
```

## 8. Execution / Test Workflow

```powershell
# 1. Criar estrutura do módulo
# (seguir os templates acima manualmente ou com subagent)

# 2. Rodar testes (independente, fora do GrindX)
$env:GRINDX_PACKAGES = "D:\\_Projetos\\GrindX\\packages"
python -m pytest app/modules/{module_name}/tests/ -v
# Esperado: 10+ testes PASS

# 3. Gerar pacote .zip (após testes verdes)
python -m app.modules.{module_name}.package --dry-run   # simular
python -m app.modules.{module_name}.package              # gerar dist/modulo-{module_name}.zip

# 4. Exportar para o GrindX (via CLI, alternativa ao .zip)
python -m app.modules.{module_name}.export --dry-run   # simular
python -m app.modules.{module_name}.export              # executar

# 5. Verificar no GrindX
cd D:\\_Projetos\\GrindX\\packages\\api-postgres
pytest tests/ -k {module_name} -v
```

## Registration Checklist

- [ ] **Tech Stack definido**: Padrão GrindX (HTML puro + CSS puro + Vanilla JS + PostgreSQL) ou padrão alternativo especificado
- [ ] Backend: base, model, schemas, repository, service, router + __init__.py
- [ ] Tests: conftest.py, unit tests (mocked repo), integration tests (SQLite)
- [ ] Migration: Alembic migration file (PostgreSQL)
- [ ] Frontend: index.html, script.js, style.css (se Padrão GrindX: HTML puro, CSS com `var(--...)`, Vanilla JS puro)
- [ ] Header segue padrão 3.1.1: `class="page-header mb-8"` sem flex, `actions-group` com `margin-top: var(--space-4)`
- [ ] Support: requirements.txt, pytest.ini, run_tests.ps1
- [ ] Testes passam: `pytest app/modules/{module_name}/tests/ -v`
- [ ] `module.json` criado na raiz do standalone com metadados do módulo
- [ ] `export.py`: `--dry-run` simula sem alterar GrindX
- [ ] `export.py`: `--grindx-root` aceita caminho customizado
- [ ] `export.py`: comando `package` gera `.zip` com `module.json` incluso
- [ ] Herança de skins: style.css usa `var(--...)`, sem cores fixas
