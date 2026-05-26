---
name: create-module
description: Use when creating new CRUD modules in the GrindX ERP monorepo - backend (FastAPI), frontend (vanilla JS), or both
---

# Create Module — GrindX

Guia para criar módulos completos (backend + frontend) seguindo os padrões do projeto.

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `module_name` | Nome do módulo (snake_case) | `produto`, `categoria`, `fornecedor` |
| `entity_name` | Nome da entidade (PascalCase) | `Produto`, `Categoria`, `Fornecedor` |
| `schema_name` | Schema do banco (domínio) | `catalogo`, `org`, `portal`, `iam` |
| `route_prefix` | Prefixo da URL | `/v1/estoque` |
| `route_tag` | Tag Swagger | `"Estoque"` |
| `frontend_path` | Caminho no portal | `modules/produtos` |
| `menu_label` | Rótulo no menu | `"Produtos"` |

## Backend Workflow

Criar 7 arquivos na ordem abaixo, dentro de `packages/api-postgres/app/`.

### 1. Model — `modules/{schema}/models/{entity}.py`

```python
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.{schema}.base import {schema|pascal}Base


class {entity_name}({schema|pascal}Base):
    __tablename__ = "{table_name}"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, comment="Nome"
    )
    ativo: Mapped[bool] = mapped_column(
        default=True, nullable=False, comment="Se está ativo"
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

### 2. Model Shim — `models/{entity}.py`

Re-exporta o model do módulo multi-schema para compatibilidade:

```python
from app.modules.{schema}.models.{entity} import {entity_name}

__all__ = ["{entity_name}"]
```

### 3. Schema — `schemas/{entity}.py`

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

### 4. Repository — `repositories/{entity}_repository.py`

```python
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.{entity} import {entity_name}
from app.schemas.{entity} import {entity_name}Create, {entity_name}Update


class {entity_name|pascal}Repository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_por_id(self, id: int) -> {entity_name} | None:
        stmt = select({entity_name}).where({entity_name}.id == id)
        return self.db.execute(stmt).scalar_one_or_none()

    def listar_todos(self, page: int = 1, page_size: int = 20) -> tuple[list[{entity_name}], int]:
        count_stmt = select(func.count()).select_from({entity_name})
        total = self.db.scalar(count_stmt) or 0
        stmt = select({entity_name}).order_by({entity_name}.nome).offset((page - 1) * page_size).limit(page_size)
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

### 5. Service — `services/{entity}_service.py`

```python
import math

import structlog
from shared.exceptions.base import NotFoundError
from shared.schemas.base import PaginatedResponse

from app.repositories.{entity}_repository import {entity_name|pascal}Repository
from app.schemas.{entity} import {entity_name}Create, {entity_name}Update

logger = structlog.get_logger(__name__)


class {entity_name|pascal}Service:
    def __init__(self, repository: {entity_name|pascal}Repository) -> None:
        self.repository = repository

    def buscar(self, id: int):
        obj = self.repository.buscar_por_id(id)
        if not obj:
            raise NotFoundError(f"{entity_name} {id} não encontrado")
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

### 6. Router — `routers/{entity}_router.py`

```python
from fastapi import APIRouter, Depends, Query
from shared.schemas.base import ErrorResponse, MessageResponse, PaginatedResponse
from shared.security.permissions import Role

from app.auth.dependencies import get_{entity}_service, require_role
from app.schemas.{entity} import {entity_name}Create, {entity_name}Response, {entity_name}Update
from app.services.{entity}_service import {entity_name|pascal}Service

router = APIRouter(prefix="{route_prefix}", tags=["{route_tag}"])


@router.get("/{entity_name_plural}", response_model=PaginatedResponse[{entity_name}Response],
    summary="Listar", dependencies=[Depends(require_role(Role.ADMIN, Role.OPERADOR, Role.LEITURA))])
def listar(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    service: {entity_name|pascal}Service = Depends(get_{entity}_service)):
    return service.listar(page, page_size)


@router.get("/{entity_name_plural}/{{id}}", response_model={entity_name}Response,
    summary="Buscar por ID", dependencies=[Depends(require_role(Role.ADMIN, Role.OPERADOR, Role.LEITURA))])
def buscar(id: int, service: {entity_name|pascal}Service = Depends(get_{entity}_service)):
    return service.buscar(id)


@router.post("/{entity_name_plural}", response_model={entity_name}Response, status_code=201,
    summary="Criar", dependencies=[Depends(require_role(Role.OPERADOR, Role.ADMIN))])
def criar(dados: {entity_name}Create, service: {entity_name|pascal}Service = Depends(get_{entity}_service)):
    return service.criar(dados)


@router.put("/{entity_name_plural}/{{id}}", response_model={entity_name}Response,
    summary="Atualizar", dependencies=[Depends(require_role(Role.OPERADOR, Role.ADMIN))])
def atualizar(id: int, dados: {entity_name}Update, service: {entity_name|pascal}Service = Depends(get_{entity}_service)):
    return service.atualizar(id, dados)


@router.delete("/{entity_name_plural}/{{id}}", response_model=MessageResponse,
    summary="Desativar", dependencies=[Depends(require_role(Role.ADMIN))])
def desativar(id: int, service: {entity_name|pascal}Service = Depends(get_{entity}_service)):
    service.desativar(id)
    return MessageResponse(message=f"{entity_name} {id} desativado com sucesso.")
```

### 7. Dependencies — `auth/dependencies.py`

Adicionar factory do service:

```python
from app.repositories.{entity}_repository import {entity_name|pascal}Repository
from app.services.{entity}_service import {entity_name|pascal}Service


def get_{entity}_service(db: Session = Depends(get_db)) -> {entity_name|pascal}Service:
    repository = {entity_name|pascal}Repository(db)
    return {entity_name|pascal}Service(repository)
```

### 8. Main — `main.py`

Registrar o router:

```python
from app.routers.{entity}_router import router as {entity}_router

app.include_router({entity}_router)
```

## Frontend Workflow

Criar 3 arquivos em `packages/frontend-webapp/modules/{module_name}/`.

### index.html

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{menu_label} — GrindX</title>
    <link rel="stylesheet" href="../../shared/core.css">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="page-container">
        <div class="page-header">
            <h1 id="pageTitle">{menu_label}</h1>
            <button class="btn btn-primary" id="btnNovo">+ Novo</button>
        </div>
        <div id="dataTableContainer"></div>
    </div>

    <div class="modal-overlay hidden" id="modal">
        <div class="modal">
            <div class="modal-header">
                <h2 id="modalTitle">Novo {menu_label}</h2>
                <button type="button" class="modal-close" id="btnModalClose">&times;</button>
            </div>
            <form id="form" class="grid"></form>
        </div>
    </div>

    <script src="../../shared/app.js"></script>
    <script src="../../shared/apiService.js"></script>
    <script src="../../shared/components/LoadingSpinner.js"></script>
    <script src="../../shared/components/DataTable.js"></script>
    <script src="../../shared/components/ReusableModal.js"></script>
    <script src="../../shared/validation.js"></script>
    <script src="../../shared/baseController.js"></script>
    <script src="script.js"></script>
</body>
</html>
```

### script.js

Estender `BaseController` e usar `window.grindx.api` para chamadas REST:

```javascript
class {entity_name|pascal}Controller extends window.grindx.controllers.BaseController {
    constructor() {
        super();
        this.baseUrl = '/{route_api}';
        this.dataTable = null;
        this.modal = null;
        this.init();
    }

    async init() {
        if (!this.requireAuth()) return;
        this.modal = new window.grindx.components.ReusableModal('modal');
        this.dataTable = new window.grindx.components.DataTable('dataTableContainer', {
            columns: [
                { key: 'id', label: 'ID', width: '60px' },
                { key: 'nome', label: 'Nome' },
                { key: 'ativo', label: 'Ativo', width: '80px', render: v => v ? 'Sim' : 'Não' },
            ],
            actions: [
                { label: 'Editar', class: 'btn-sm', onClick: (row) => this.editar(row) },
                { label: 'Excluir', class: 'btn-sm btn-danger', onClick: (row) => this.excluir(row) },
            ],
            onPageChange: (page) => this.carregar(page),
        });
        this.bindEvents();
        this.carregar();
    }

    bindEvents() {
        document.getElementById('btnNovo').addEventListener('click', () => this.abrirModal());
        document.getElementById('form').addEventListener('submit', (e) => this.salvar(e));
        document.getElementById('btnModalClose').addEventListener('click', () => this.modal.close());
    }

    async carregar(page = 1) {
        try {
            const data = await window.grindx.api.get(`${this.baseUrl}?page=${page}&page_size=20`);
            this.dataTable.render(data.items, { page: data.page, total: data.total, totalPages: data.total_pages });
        } catch (err) { this.toastError(err); }
    }
}
```

### style.css

```css
@import url('../../shared/core.css');

.page-container { padding: var(--space-6); }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-6); }
```

## Database Migration

```bash
cd packages/api-postgres
alembic revision --autogenerate -m "criar tabela {table_name}"
alembic upgrade head
```

## Multi-Schema Rules

| Schema | Base Class | Schema Name | Domain |
|--------|-----------|-------------|--------|
| IAM | `IamBase` (primary) | `iam` | Users, auth |
| Catálogo | `CatalogoBase` → `IamBase` | `catalogo` | Products, services |
| Portal | `PortalBase` → `IamBase` | `portal` | Tabs, modules, menu |
| Organização | `OrgBase` → `IamBase` | `org` | Companies, themes |

- Todos os schemas secundários reusam `registry` e `metadata` do `IamBase`
- Models de schemas diferentes podem ter FKs entre si (mesmo MetaData)

## Registration Checklist

- [ ] Backend: model (multi-schema + shim), schema, repository, service, router, dependency, main.py
- [ ] Migration: `alembic revision --autogenerate` + `alembic upgrade head`
- [ ] Test: `make test-postgres` ou `pytest`
- [ ] Frontend: `index.html`, `script.js`, `style.css`
- [ ] Register module in DB via `/v1/portal/modulos` or Structure Management UI
