# Mensageiro (Mensagens Internas) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the central asynchronous messaging/notification module (Mensageiro) — threads with replies, attachments, unread badge on the AI mascot, and a dedicated frontend module — per `docs/superpowers/specs/2026-08-25-mensageiro-design.md`.

**Architecture:** Backend as a top-level `app/mensagens/` package (like `app/audit/`) with `models.py`, `schemas.py`, `service.py`, `router.py`; tables in `org` schema via `OrgBase`. Frontend: `shared/notificationBridge.js` (postMessage between module iframes and shell), a `shared/mensagensWidget.js` widget manager for the mascot badge/balloon, and a standard module `modules/mensagens/`. Refresh is polling (10 min) + postMessage events; no WebSockets.

**Tech Stack:** FastAPI, SQLAlchemy 2.x, Alembic, PostgreSQL (SQLite in tests via `schema_translate_map`), Vanilla JS, `node:test` for frontend.

---

## File Structure

**Backend (new):**
- `apps/api-postgres/alembic/versions/023_add_mensagens.py` — migration (mensagens + anexos_mensagem tables, indexes, partial index).
- `apps/api-postgres/app/mensagens/__init__.py` — empty.
- `apps/api-postgres/app/mensagens/models.py` — `Mensagem`, `AnexoMensagem`.
- `apps/api-postgres/app/mensagens/schemas.py` — enums + `MensagemCreate`, `RespostaCreate`, `MensagemResponse`, `AnexoResponse`.
- `apps/api-postgres/app/mensagens/service.py` — `MensagensService`.
- `apps/api-postgres/app/mensagens/router.py` — APIRouter `/v1/mensagens`.

**Backend (modified):**
- `apps/api-postgres/app/main.py` — register `mensagens_router`.

**Backend tests (new):**
- `apps/api-postgres/tests/unit/test_mensagens_models.py`
- `apps/api-postgres/tests/unit/test_mensagens_service.py`
- `apps/api-postgres/tests/integration/test_mensagens_api.py`

**Frontend (new):**
- `apps/frontend-webapp/shared/notificationBridge.js`
- `apps/frontend-webapp/shared/mensagensWidget.js`
- `apps/frontend-webapp/modules/mensagens/index.html`
- `apps/frontend-webapp/modules/mensagens/style.css`
- `apps/frontend-webapp/modules/mensagens/script.js`
- `apps/frontend-webapp/tests/notificationBridge.test.js`
- `apps/frontend-webapp/tests/mensagensWidget.test.js`

**Frontend (modified):**
- `apps/frontend-webapp/dashboard.html` — add `notificationBridge.js` script; add "Mensagens" dropdown button.
- `apps/frontend-webapp/dashboard.js` — postMessage listener + dropdown wiring + dropdown badge refresh.
- `apps/frontend-webapp/widget/widget.js` — instantiate `MensagensWidget` with badge/balloon DOM.
- `apps/frontend-webapp/widget/widget.css` — badge/balloon styles.

**Seed & docs:**
- `apps/api-postgres/seed.py` — register `mensagens` module in `modulos_seed`.
- `README.md`, `docs/API.md`, `docs/DATABASE.md`.

---

## Task 1: Alembic Migration `023_add_mensagens`

**Files:**
- Create: `apps/api-postgres/alembic/versions/023_add_mensagens.py`
- Reference: `apps/api-postgres/alembic/versions/022_add_audit_tables.py` (current head `f49af6b8a8d4`)

- [ ] **Step 1: Write the migration**

Create `apps/api-postgres/alembic/versions/023_add_mensagens.py`:

```python
"""add mensagens and anexos_mensagem tables

Revision ID: 023a4c5d6e7f
Revises: f49af6b8a8d4
Create Date: 2026-08-25 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "023a4c5d6e7f"
down_revision: Union[str, None] = "f49af6b8a8d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "mensagens",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "resposta_a_id",
            sa.BigInteger(),
            sa.ForeignKey("org.mensagens.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "remetente_id",
            sa.BigInteger(),
            sa.ForeignKey("iam.usuarios.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "destinatario_id",
            sa.BigInteger(),
            sa.ForeignKey("iam.usuarios.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("titulo", sa.String(150), nullable=False),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column(
            "categoria",
            sa.String(20),
            server_default=sa.text("'DIRETA'"),
            nullable=False,
        ),
        sa.Column("url_acao", sa.String(255), nullable=True),
        sa.Column("lida_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("arquivada_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "categoria IN ('SISTEMA', 'DIRETA', 'AVISO')",
            name="ck_mensagens_categoria",
        ),
        sa.Index("ix_mensagens_destinatario_id", "destinatario_id", "criado_em"),
        sa.Index("ix_mensagens_resposta_a", "resposta_a_id"),
        schema="org",
    )
    op.create_index(
        "ix_mensagens_nao_lidas",
        "mensagens",
        ["destinatario_id", "criado_em"],
        unique=False,
        postgresql_where=sa.text("lida_em IS NULL"),
        schema="org",
    )
    op.create_table(
        "anexos_mensagem",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "mensagem_id",
            sa.BigInteger(),
            sa.ForeignKey("org.mensagens.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("nome_arquivo_original", sa.String(255), nullable=False),
        sa.Column("caminho", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("tamanho_bytes", sa.Integer(), nullable=False),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Index("ix_anexos_mensagem_mensagem_id", "mensagem_id"),
        schema="org",
    )


def downgrade() -> None:
    op.drop_table("anexos_mensagem", schema="org")
    op.drop_index("ix_mensagens_nao_lidas", table_name="mensagens", schema="org")
    op.drop_table("mensagens", schema="org")
```

- [ ] **Step 2: Validate the migration imports and revision chain**

Run (workdir `apps/api-postgres`):
```bash
python -c "import importlib.util, sys; spec=importlib.util.spec_from_file_location('m023','alembic/versions/023_add_mensagens.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); assert m.down_revision=='f49af6b8a8d4'; print('OK', m.revision)"
```
Expected: `OK 023a4c5d6e7f`

- [ ] **Step 3: Commit**

```bash
git add alembic/versions/023_add_mensagens.py
git commit -m "feat(mensagens): add mensagens and anexos_mensagem migration"
```

---

## Task 2: Models + unit test

**Files:**
- Create: `apps/api-postgres/app/mensagens/__init__.py`
- Create: `apps/api-postgres/app/mensagens/models.py`
- Test: `apps/api-postgres/tests/unit/test_mensagens_models.py`
- Reference: `apps/api-postgres/app/audit/models.py`

- [ ] **Step 1: Create package init**

Create `apps/api-postgres/app/mensagens/__init__.py` (empty file).

- [ ] **Step 2: Write the failing test**

Create `apps/api-postgres/tests/unit/test_mensagens_models.py`:

```python
"""Testes de modelos do módulo de mensagens."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.mensagens.models import AnexoMensagem, Mensagem
from app.models.usuario import Usuario
from shared.security.jwt import gerar_hash_senha


def _usuario(db: Session, username: str) -> Usuario:
    u = Usuario(
        username=username,
        email=f"{username}@x.com",
        nome_completo=username,
        senha_hash=gerar_hash_senha("senha123"),
        role="operador",
    )
    db.add(u)
    db.commit()
    return u


def test_mensagem_cria_e_resposta_aponta_raiz(db_session: Session):
    a = _usuario(db_session, "alice")
    b = _usuario(db_session, "bob")

    raiz = Mensagem(
        remetente_id=a.id,
        destinatario_id=b.id,
        titulo="Olá",
        texto="Mensagem inicial",
        categoria="DIRETA",
    )
    db_session.add(raiz)
    db_session.commit()

    resposta = Mensagem(
        resposta_a_id=raiz.id,
        remetente_id=b.id,
        destinatario_id=a.id,
        titulo="Re: Olá",
        texto="Resposta",
        categoria="DIRETA",
    )
    db_session.add(resposta)
    db_session.commit()

    assert raiz.id is not None
    assert resposta.resposta_a_id == raiz.id
    assert isinstance(raiz.criado_em, datetime)


def test_anexo_mensagem_cria_e_relaciona(db_session: Session):
    a = _usuario(db_session, "alice2")
    b = _usuario(db_session, "bob2")
    msg = Mensagem(
        remetente_id=a.id,
        destinatario_id=b.id,
        titulo="Com anexo",
        texto="Texto",
        categoria="DIRETA",
    )
    db_session.add(msg)
    db_session.commit()

    anexo = AnexoMensagem(
        mensagem_id=msg.id,
        nome_arquivo_original="doc.pdf",
        caminho="mensagens/abc.pdf",
        content_type="application/pdf",
        tamanho_bytes=10,
    )
    db_session.add(anexo)
    db_session.commit()

    assert anexo.id is not None
    assert anexo.mensagem_id == msg.id
    assert anexo.tamanho_bytes == 10
```

- [ ] **Step 3: Run test to verify it fails**

Run (workdir `apps/api-postgres`):
```bash
python -m pytest tests/unit/test_mensagens_models.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'app.mensagens.models'`

- [ ] **Step 4: Write the models**

Create `apps/api-postgres/app/mensagens/models.py`:

```python
"""Modelos do módulo central de mensagens."""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.org.base import OrgBase


class Mensagem(OrgBase):
    __tablename__ = "mensagens"

    __table_args__ = (
        CheckConstraint(
            "categoria IN ('SISTEMA', 'DIRETA', 'AVISO')",
            name="ck_mensagens_categoria",
        ),
        Index("ix_mensagens_destinatario_id", "destinatario_id", "criado_em"),
        Index("ix_mensagens_resposta_a", "resposta_a_id"),
        {"schema": "org"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resposta_a_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("org.mensagens.id", ondelete="CASCADE"),
        nullable=True,
        comment="Mensagem raiz da thread (NULL para mensagens raiz)",
    )
    remetente_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("iam.usuarios.id", ondelete="SET NULL"),
        nullable=True,
        comment="NULL indica mensagem gerada pelo sistema",
    )
    destinatario_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("iam.usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    categoria: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="DIRETA"
    )
    url_acao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lida_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    arquivada_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<Mensagem(id={self.id}, titulo='{self.titulo}', "
            f"categoria='{self.categoria}')>"
        )


class AnexoMensagem(OrgBase):
    __tablename__ = "anexos_mensagem"

    __table_args__ = (
        Index("ix_anexos_mensagem_mensagem_id", "mensagem_id"),
        {"schema": "org"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    mensagem_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("org.mensagens.id", ondelete="CASCADE"),
        nullable=False,
    )
    nome_arquivo_original: Mapped[str] = mapped_column(String(255), nullable=False)
    caminho: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    tamanho_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<AnexoMensagem(id={self.id}, "
            f"nome='{self.nome_arquivo_original}', size={self.tamanho_bytes})>"
        )
```

**IMPORTANT:** The model intentionally does NOT declare the partial index `ix_mensagens_nao_lidas` (Postgres `postgresql_where` breaks SQLite `create_all` in tests). It lives only in the migration (Task 1).

- [ ] **Step 5: Run test to verify it passes**

Run (workdir `apps/api-postgres`):
```bash
python -m pytest tests/unit/test_mensagens_models.py -v
```
Expected: PASS (2 tests)

- [ ] **Step 6: Commit**

```bash
git add app/mensagens/__init__.py app/mensagens/models.py tests/unit/test_mensagens_models.py
git commit -m "feat(mensagens): add Mensagem and AnexoMensagem models"
```

---

## Task 3: Schemas

**Files:**
- Create: `apps/api-postgres/app/mensagens/schemas.py`
- Reference: `apps/api-postgres/app/schemas/audit.py` (uses `class Config: from_attributes = True`)

- [ ] **Step 1: Write the schemas**

Create `apps/api-postgres/app/mensagens/schemas.py`:

```python
"""Schemas do módulo central de mensagens."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class CategoriaMensagem(StrEnum):
    SISTEMA = "SISTEMA"
    DIRETA = "DIRETA"
    AVISO = "AVISO"


class StatusMensagem(StrEnum):
    TODAS = "todas"
    NAO_LIDAS = "nao_lidas"
    LIDAS = "lidas"
    ARQUIVADAS = "arquivadas"


class OrdemMensagem(StrEnum):
    CRESCENTE = "crescente"
    DECRESCENTE = "decrescente"


class MensagemCreate(BaseModel):
    """Criação de mensagem raiz."""

    destinatario_id: int = Field(..., ge=1)
    titulo: str = Field(..., min_length=1, max_length=150)
    texto: str = Field(..., min_length=1)
    categoria: CategoriaMensagem = CategoriaMensagem.DIRETA
    url_acao: str | None = Field(default=None, max_length=255)


class RespostaCreate(BaseModel):
    """Criação de resposta em uma thread."""

    texto: str = Field(..., min_length=1)
    titulo: str | None = Field(default=None, max_length=150)
    url_acao: str | None = Field(default=None, max_length=255)


class ArquivarRequest(BaseModel):
    """Body opcional do arquivamento (default: arquivar)."""

    arquivar: bool = True


class AnexoResponse(BaseModel):
    """Resposta com metadados de anexo."""

    id: int
    nome_arquivo_original: str
    content_type: str
    tamanho_bytes: int
    criado_em: datetime | None = None

    class Config:
        from_attributes = True


class MensagemResponse(BaseModel):
    """Resposta de uma mensagem (raiz ou resposta)."""

    id: int
    resposta_a_id: int | None = None
    remetente_id: int | None = None
    remetente_nome: str | None = None
    destinatario_id: int
    titulo: str
    texto: str
    categoria: str
    url_acao: str | None = None
    lida_em: datetime | None = None
    arquivada_em: datetime | None = None
    criado_em: datetime | None = None
    quantidade_respostas: int = 0
    ultima_resposta_em: datetime | None = None
    anexos: list[AnexoResponse] = []
    anexos_count: int = 0

    class Config:
        from_attributes = True


class CountResponse(BaseModel):
    """Resposta do contador de não lidas."""

    count: int
```

- [ ] **Step 2: Verify import**

Run (workdir `apps/api-postgres`):
```bash
python -c "from app.mensagens.schemas import CategoriaMensagem, MensagemCreate, StatusMensagem, OrdemMensagem; m=MensagemCreate(destinatario_id=1, titulo='x', texto='y'); print(m.categoria); print(list(StatusMensagem))"
```
Expected: `DIRETA` and the status enum list.

- [ ] **Step 3: Commit**

```bash
git add app/mensagens/schemas.py
git commit -m "feat(mensagens): add schemas and enums"
```

---

## Task 4: Service (CRUD, threads, arquivar, contador) + unit tests

**Files:**
- Create: `apps/api-postgres/app/mensagens/service.py`
- Test: `apps/api-postgres/tests/unit/test_mensagens_service.py`

- [ ] **Step 1: Write the failing tests**

Create `apps/api-postgres/tests/unit/test_mensagens_service.py`:

```python
"""Testes de unidade do service de mensagens."""

import pytest
from shared.exceptions.base import BusinessValidationError, ForbiddenError, NotFoundError
from sqlalchemy.orm import Session

from app.mensagens.models import Mensagem
from app.mensagens.schemas import (
    MensagemCreate,
    OrdemMensagem,
    RespostaCreate,
    StatusMensagem,
)
from app.mensagens.service import MensagensService
from app.models.usuario import Usuario
from shared.security.jwt import gerar_hash_senha


def _usuario(db: Session, username: str, role: str = "operador") -> Usuario:
    u = Usuario(
        username=username,
        email=f"{username}@x.com",
        nome_completo=username,
        senha_hash=gerar_hash_senha("senha123"),
        role=role,
    )
    db.add(u)
    db.commit()
    return u


def _criar_raiz(db, de, para, **kwargs):
    dados = MensagemCreate(
        destinatario_id=para.id,
        titulo=kwargs.get("titulo", "Título"),
        texto=kwargs.get("texto", "Texto"),
        categoria=kwargs.get("categoria", "DIRETA"),
        url_acao=kwargs.get("url_acao"),
    )
    return MensagensService(db).criar_mensagem(
        usuario_id=de.id, dados=dados, is_admin=kwargs.get("is_admin", False)
    )


def test_criar_mensagem_direta_define_remetente_logado(db_session: Session):
    a = _usuario(db_session, "rem1")
    b = _usuario(db_session, "dest1")
    msg = _criar_raiz(db_session, a, b)
    assert msg.remetente_id == a.id
    assert msg.destinatario_id == b.id
    assert msg.categoria == "DIRETA"
    assert msg.lida_em is None


def test_criar_mensagem_sistema_requer_admin_e_remetente_null(db_session: Session):
    admin = _usuario(db_session, "adm1", role="admin")
    comum = _usuario(db_session, "comum1", role="operador")
    b = _usuario(db_session, "dest2")

    # Usuário comum NÃO pode enviar SISTEMA
    with pytest.raises(ForbiddenError):
        _criar_raiz(db_session, comum, b, categoria="SISTEMA")

    # Admin pode; remetente fica NULL
    msg = _criar_raiz(db_session, admin, b, categoria="AVISO", is_admin=True)
    assert msg.remetente_id is None
    assert msg.categoria == "AVISO"


def test_criar_mensagem_destinatario_inexistente(db_session: Session):
    a = _usuario(db_session, "rem2")
    dados = MensagemCreate(
        destinatario_id=99999, titulo="X", texto="Y", categoria="DIRETA"
    )
    with pytest.raises(NotFoundError):
        MensagensService(db_session).criar_mensagem(a.id, dados, is_admin=False)


def test_contar_nao_lidas_ignora_lidas_e_arquivadas(db_session: Session):
    a = _usuario(db_session, "rem3")
    b = _usuario(db_session, "dest3")
    svc = MensagensService(db_session)

    m1 = _criar_raiz(db_session, a, b, titulo="Não lida")
    m2 = _criar_raiz(db_session, a, b, titulo="Lida")
    m3 = _criar_raiz(db_session, a, b, titulo="Arquivada")

    svc.marcar_lida(b.id, m2.id)
    svc.arquivar(b.id, m3.id, arquivar=True)

    assert svc.contar_nao_lidas(b.id) == 1  # apenas m1


def test_listar_retorna_apenas_raizes_com_filtros(db_session: Session):
    a = _usuario(db_session, "rem4")
    b = _usuario(db_session, "dest4")
    svc = MensagensService(db_session)

    raiz1 = _criar_raiz(db_session, a, b, titulo="Raiz 1")
    raiz2 = _criar_raiz(db_session, a, b, titulo="Raiz 2")

    svc.arquivar(b.id, raiz2.id, arquivar=True)
    svc.criar_resposta(b.id, raiz1.id, RespostaCreate(texto="resposta"))
    svc.marcar_lida(b.id, raiz1.id)

    itens, total = svc.listar_mensagens(
        b.id, StatusMensagem.TODAS, OrdemMensagem.DECRESCENTE, 1, 20
    )
    assert total == 1  # "todas" exclui arquivadas
    assert itens[0]["titulo"] == "Raiz 1"
    assert itens[0]["quantidade_respostas"] == 1

    lidas, total_lidas = svc.listar_mensagens(
        b.id, StatusMensagem.LIDAS, OrdemMensagem.DECRESCENTE, 1, 20
    )
    assert total_lidas == 1

    nao_lidas, total_nl = svc.listar_mensagens(
        b.id, StatusMensagem.NAO_LIDAS, OrdemMensagem.DECRESCENTE, 1, 20
    )
    assert total_nl == 0  # raiz1 lida e resposta é de b para a (não conta para b)

    arq_itens, total_arq = svc.listar_mensagens(
        b.id, StatusMensagem.ARQUIVADAS, OrdemMensagem.DECRESCENTE, 1, 20
    )
    assert total_arq == 1
    assert arq_itens[0]["titulo"] == "Raiz 2"


def test_marcar_lida_apenas_destinatario(db_session: Session):
    a = _usuario(db_session, "rem5")
    b = _usuario(db_session, "dest5")
    c = _usuario(db_session, "terc")
    raiz = _criar_raiz(db_session, a, b)
    svc = MensagensService(db_session)

    with pytest.raises(ForbiddenError):
        svc.marcar_lida(c.id, raiz.id)
    with pytest.raises(ForbiddenError):
        svc.marcar_lida(a.id, raiz.id)

    marcada = svc.marcar_lida(b.id, raiz.id)
    assert marcada.lida_em is not None


def test_marcar_thread_lida_marca_raiz_e_respostas(db_session: Session):
    a = _usuario(db_session, "rem6")
    b = _usuario(db_session, "dest6")
    svc = MensagensService(db_session)

    raiz = _criar_raiz(db_session, a, b, titulo="Thread")
    svc.criar_resposta(b.id, raiz.id, RespostaCreate(texto="r1"))
    svc.criar_resposta(a.id, raiz.id, RespostaCreate(texto="r2"))

    updated = svc.marcar_thread_lida(b.id, raiz.id)
    assert updated == 2  # raiz (a->b) + r2 (a->b); r1 é de b->a e não conta para b

    raiz_r = db_session.get(Mensagem, raiz.id)
    assert raiz_r.lida_em is not None


def test_arquivar_thread_somente_destinatario_da_raiz(db_session: Session):
    a = _usuario(db_session, "rem7")
    b = _usuario(db_session, "dest7")
    raiz = _criar_raiz(db_session, a, b)
    svc = MensagensService(db_session)

    with pytest.raises(ForbiddenError):
        svc.arquivar(a.id, raiz.id, arquivar=True)

    arq = svc.arquivar(b.id, raiz.id, arquivar=True)
    assert arq.arquivada_em is not None
    restaurada = svc.arquivar(b.id, raiz.id, arquivar=False)
    assert restaurada.arquivada_em is None


def test_resposta_negada_para_mensagem_de_sistema(db_session: Session):
    admin = _usuario(db_session, "adm8", role="admin")
    b = _usuario(db_session, "dest8")
    raiz = _criar_raiz(db_session, admin, b, categoria="AVISO", is_admin=True)
    svc = MensagensService(db_session)

    with pytest.raises(ForbiddenError):
        svc.criar_resposta(b.id, raiz.id, RespostaCreate(texto="não deve"))

    assert db_session.query(Mensagem).count() == 1


def test_resposta_deriva_destinatario_e_categoria_direta(db_session: Session):
    a = _usuario(db_session, "rem9")
    b = _usuario(db_session, "dest9")
    raiz = _criar_raiz(db_session, a, b)
    svc = MensagensService(db_session)

    resp = svc.criar_resposta(b.id, raiz.id, RespostaCreate(texto="oi"))
    assert resp.resposta_a_id == raiz.id
    assert resp.remetente_id == b.id
    assert resp.destinatario_id == a.id
    assert resp.categoria == "DIRETA"
    assert resp.titulo == raiz.titulo  # herda título
```

> **Nota do `test_listar_retorna_apenas_raizes_com_filtros`:** a raiz "Arquivada" foi criada com `categoria="DIRETA"` (padrão) — verifique que `total == 2` considera apenas raízes não arquivadas; o filtro `todas` exclui arquivadas.

- [ ] **Step 2: Run tests to verify they fail**

Run (workdir `apps/api-postgres`):
```bash
python -m pytest tests/unit/test_mensagens_service.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'app.mensagens.service'`

- [ ] **Step 3: Write the service**

Create `apps/api-postgres/app/mensagens/service.py`:

```python
"""Service do módulo central de mensagens."""

import structlog
from shared.exceptions.base import ForbiddenError, NotFoundError
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, aliased

from app.mensagens.models import AnexoMensagem, Mensagem
from app.mensagens.schemas import (
    MensagemCreate,
    OrdemMensagem,
    RespostaCreate,
    StatusMensagem,
)
from app.models.usuario import Usuario

logger = structlog.get_logger(__name__)

_CATEGORIAS_SISTEMA = {"SISTEMA", "AVISO"}


class MensagensService:
    """Regras de negócio de mensagens, threads e anexos."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _obter_raiz(self, mensagem_id: int) -> Mensagem:
        msg = self.db.get(Mensagem, mensagem_id)
        if msg is None:
            raise NotFoundError("Mensagem", mensagem_id)
        if msg.resposta_a_id is not None:
            raiz = self.db.get(Mensagem, msg.resposta_a_id)
            if raiz is None:
                raise NotFoundError("Mensagem", msg.resposta_a_id)
            return raiz
        return msg

    def _verificar_participante(self, raiz: Mensagem, usuario_id: int) -> None:
        participantes = {raiz.remetente_id, raiz.destinatario_id}
        if usuario_id not in participantes:
            raise ForbiddenError(
                message="Acesso restrito aos participantes da conversa."
            )

    def _verificar_destinatario(self, msg: Mensagem, usuario_id: int) -> None:
        if msg.destinatario_id != usuario_id:
            raise ForbiddenError(message="Permissão insuficiente para esta mensagem.")

    # ------------------------------------------------------------------
    # Criação
    # ------------------------------------------------------------------
    def criar_mensagem(
        self, usuario_id: int, dados: MensagemCreate, is_admin: bool = False
    ) -> Mensagem:
        destinatario = self.db.get(Usuario, dados.destinatario_id)
        if destinatario is None:
            raise NotFoundError("Usuario", dados.destinatario_id)

        categoria = dados.categoria.value
        if categoria in _CATEGORIAS_SISTEMA and not is_admin:
            raise ForbiddenError(
                message="Apenas administradores podem enviar mensagens "
                "das categorias SISTEMA ou AVISO."
            )

        msg = Mensagem(
            remetente_id=None if categoria in _CATEGORIAS_SISTEMA else usuario_id,
            destinatario_id=dados.destinatario_id,
            titulo=dados.titulo.strip(),
            texto=dados.texto,
            categoria=categoria,
            url_acao=dados.url_acao,
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        logger.info("Mensagem criada", id=msg.id, categoria=categoria)
        return msg

    def criar_resposta(
        self, usuario_id: int, mensagem_id: int, dados: RespostaCreate
    ) -> Mensagem:
        raiz = self._obter_raiz(mensagem_id)
        self._verificar_participante(raiz, usuario_id)

        if raiz.remetente_id is None:
            raise ForbiddenError(
                message="Não é possível responder a mensagens do sistema."
            )

        outro = raiz.destinatario_id if raiz.remetente_id == usuario_id else raiz.remetente_id
        resposta = Mensagem(
            resposta_a_id=raiz.id,
            remetente_id=usuario_id,
            destinatario_id=outro,
            titulo=(dados.titulo or raiz.titulo).strip(),
            texto=dados.texto,
            categoria="DIRETA",
            url_acao=dados.url_acao,
        )
        self.db.add(resposta)
        self.db.commit()
        self.db.refresh(resposta)
        logger.info("Resposta criada", id=resposta.id, raiz_id=raiz.id)
        return resposta

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------
    def listar_mensagens(
        self,
        usuario_id: int,
        status: StatusMensagem,
        ordem: OrdemMensagem,
        page: int,
        page_size: int,
    ) -> tuple[list[dict], int]:
        resposta_alias = aliased(Mensagem)

        tem_resposta_nao_lida = (
            self.db.query(func.count(resposta_alias.id))
            .filter(
                resposta_alias.resposta_a_id == Mensagem.id,
                resposta_alias.destinatario_id == usuario_id,
                resposta_alias.lida_em.is_(None),
            )
            .as_scalar()
            > 0
        )

        subq = (
            self.db.query(
                Mensagem.resposta_a_id.label("raiz_id"),
                func.count(Mensagem.id).label("qtd_respostas"),
                func.max(Mensagem.criado_em).label("ultima_resposta"),
            )
            .filter(Mensagem.resposta_a_id.isnot(None))
            .group_by(Mensagem.resposta_a_id)
            .subquery()
        )

        anexos_subq = (
            self.db.query(
                AnexoMensagem.mensagem_id.label("msg_id"),
                func.count(AnexoMensagem.id).label("qtd_anexos"),
            )
            .group_by(AnexoMensagem.mensagem_id)
            .subquery()
        )

        q = (
            self.db.query(
                Mensagem,
                Usuario.nome_completo,
                subq.c.qtd_respostas,
                subq.c.ultima_resposta,
                anexos_subq.c.qtd_anexos,
            )
            .outerjoin(subq, subq.c.raiz_id == Mensagem.id)
            .outerjoin(Usuario, Usuario.id == Mensagem.remetente_id)
            .outerjoin(anexos_subq, anexos_subq.c.msg_id == Mensagem.id)
            .filter(Mensagem.resposta_a_id.is_(None))
            .filter(Mensagem.destinatario_id == usuario_id)
        )

        if status == StatusMensagem.NAO_LIDAS:
            q = q.filter(or_(Mensagem.lida_em.is_(None), tem_resposta_nao_lida))
        elif status == StatusMensagem.LIDAS:
            q = q.filter(and_(Mensagem.lida_em.isnot(None), ~tem_resposta_nao_lida))
        elif status == StatusMensagem.ARQUIVADAS:
            q = q.filter(Mensagem.arquivada_em.isnot(None))
        else:  # TODAS
            q = q.filter(Mensagem.arquivada_em.is_(None))

        atividade = func.coalesce(subq.c.ultima_resposta, Mensagem.criado_em)
        ordem_dir = atividade.desc() if ordem == OrdemMensagem.DECRESCENTE else atividade.asc()
        q = q.order_by(ordem_dir)

        total = q.count()
        rows = q.offset((page - 1) * page_size).limit(page_size).all()

        itens = []
        for msg, nome, qtd, ultima, qtd_anexos in rows:
            item = {
                "id": msg.id,
                "resposta_a_id": msg.resposta_a_id,
                "remetente_id": msg.remetente_id,
                "remetente_nome": nome,
                "destinatario_id": msg.destinatario_id,
                "titulo": msg.titulo,
                "texto": msg.texto,
                "categoria": msg.categoria,
                "url_acao": msg.url_acao,
                "lida_em": msg.lida_em,
                "arquivada_em": msg.arquivada_em,
                "criado_em": msg.criado_em,
                "quantidade_respostas": qtd or 0,
                "ultima_resposta_em": ultima,
                "anexos_count": qtd_anexos or 0,
            }
            itens.append(item)
        return itens, total

    def listar_thread(self, usuario_id: int, mensagem_id: int) -> list[dict]:
        raiz = self._obter_raiz(mensagem_id)
        self._verificar_participante(raiz, usuario_id)

        rows = (
            self.db.query(Mensagem, Usuario.nome_completo)
            .outerjoin(Usuario, Usuario.id == Mensagem.remetente_id)
            .filter(
                or_(Mensagem.id == raiz.id, Mensagem.resposta_a_id == raiz.id)
            )
            .order_by(Mensagem.criado_em.asc(), Mensagem.id.asc())
            .all()
        )
        ids = [m.id for m, _ in rows]
        anexos = (
            self.db.query(AnexoMensagem)
            .filter(AnexoMensagem.mensagem_id.in_(ids))
            .order_by(AnexoMensagem.id.asc())
            .all()
        )
        anexos_por_msg: dict[int, list] = {}
        for anexo in anexos:
            anexos_por_msg.setdefault(anexo.mensagem_id, []).append(anexo)

        itens = []
        for msg, nome in rows:
            item = {
                "id": msg.id,
                "resposta_a_id": msg.resposta_a_id,
                "remetente_id": msg.remetente_id,
                "remetente_nome": nome,
                "destinatario_id": msg.destinatario_id,
                "titulo": msg.titulo,
                "texto": msg.texto,
                "categoria": msg.categoria,
                "url_acao": msg.url_acao,
                "lida_em": msg.lida_em,
                "arquivada_em": msg.arquivada_em,
                "criado_em": msg.criado_em,
                "quantidade_respostas": 0,
                "ultima_resposta_em": None,
                "anexos_count": len(anexos_por_msg.get(msg.id, [])),
                "anexos": [
                    {
                        "id": a.id,
                        "nome_arquivo_original": a.nome_arquivo_original,
                        "content_type": a.content_type,
                        "tamanho_bytes": a.tamanho_bytes,
                        "criado_em": a.criado_em,
                    }
                    for a in anexos_por_msg.get(msg.id, [])
                ],
            }
            itens.append(item)
        return itens

    def contar_nao_lidas(self, usuario_id: int) -> int:
        raiz_alias = aliased(Mensagem)
        return (
            self.db.query(Mensagem)
            .outerjoin(raiz_alias, Mensagem.resposta_a_id == raiz_alias.id)
            .filter(
                Mensagem.destinatario_id == usuario_id,
                Mensagem.lida_em.is_(None),
                func.coalesce(
                    Mensagem.arquivada_em, raiz_alias.arquivada_em
                ).is_(None),
            )
            .count()
        )

    # ------------------------------------------------------------------
    # Ações
    # ------------------------------------------------------------------
    def marcar_lida(self, usuario_id: int, mensagem_id: int) -> Mensagem:
        msg = self.db.get(Mensagem, mensagem_id)
        if msg is None:
            raise NotFoundError("Mensagem", mensagem_id)
        self._verificar_destinatario(msg, usuario_id)
        if msg.lida_em is None:
            msg.lida_em = func.now()
            self.db.commit()
            self.db.refresh(msg)
        return msg

    def marcar_thread_lida(self, usuario_id: int, mensagem_id: int) -> int:
        raiz = self._obter_raiz(mensagem_id)
        self._verificar_participante(raiz, usuario_id)
        q = self.db.query(Mensagem).filter(
            or_(Mensagem.id == raiz.id, Mensagem.resposta_a_id == raiz.id),
            Mensagem.destinatario_id == usuario_id,
            Mensagem.lida_em.is_(None),
        )
        count = q.count()
        q.update({Mensagem.lida_em: func.now()}, synchronize_session=False)
        self.db.commit()
        return count

    def arquivar(
        self, usuario_id: int, mensagem_id: int, arquivar: bool = True
    ) -> Mensagem:
        raiz = self._obter_raiz(mensagem_id)
        self._verificar_destinatario(raiz, usuario_id)
        raiz.arquivada_em = func.now() if arquivar else None
        self.db.commit()
        self.db.refresh(raiz)
        return raiz

    # ------------------------------------------------------------------
    # Anexos
    # ------------------------------------------------------------------
    def listar_anexos(self, usuario_id: int, mensagem_id: int) -> list[AnexoMensagem]:
        msg = self.db.get(Mensagem, mensagem_id)
        if msg is None:
            raise NotFoundError("Mensagem", mensagem_id)
        raiz = self._obter_raiz(mensagem_id)
        self._verificar_participante(raiz, usuario_id)
        return (
            self.db.query(AnexoMensagem)
            .filter(AnexoMensagem.mensagem_id == mensagem_id)
            .order_by(AnexoMensagem.id.asc())
            .all()
        )

    def salvar_anexo_meta(
        self,
        mensagem_id: int,
        nome_original: str,
        caminho: str,
        content_type: str,
        tamanho_bytes: int,
    ) -> AnexoMensagem:
        anexo = AnexoMensagem(
            mensagem_id=mensagem_id,
            nome_arquivo_original=nome_original,
            caminho=caminho,
            content_type=content_type,
            tamanho_bytes=tamanho_bytes,
        )
        self.db.add(anexo)
        self.db.commit()
        self.db.refresh(anexo)
        return anexo

    def obter_anexo(
        self, usuario_id: int, mensagem_id: int, anexo_id: int
    ) -> AnexoMensagem:
        raiz = self._obter_raiz(mensagem_id)
        self._verificar_participante(raiz, usuario_id)
        anexo = (
            self.db.query(AnexoMensagem)
            .filter(AnexoMensagem.id == anexo_id)
            .filter(AnexoMensagem.mensagem_id == mensagem_id)
            .first()
        )
        if anexo is None:
            raise NotFoundError("Anexo", anexo_id)
        return anexo
```

- [ ] **Step 4: Run tests to verify they pass**

Run (workdir `apps/api-postgres`):
```bash
python -m pytest tests/unit/test_mensagens_service.py -v
```
Expected: PASS (10 tests).

- [ ] **Step 5: Commit**

```bash
git add app/mensagens/service.py tests/unit/test_mensagens_service.py
git commit -m "feat(mensagens): add MensagensService with threads, archive and unread count"
```

---

## Task 5: Router + registro no main + testes de integração

**Files:**
- Create: `apps/api-postgres/app/mensagens/router.py`
- Modify: `apps/api-postgres/app/main.py`
- Test: `apps/api-postgres/tests/integration/test_mensagens_api.py`

- [ ] **Step 1: Write the failing integration tests**

Create `apps/api-postgres/tests/integration/test_mensagens_api.py`:

```python
"""Testes de integração da API de mensagens."""

import os
import uuid

from fastapi.testclient import TestClient
from shared.security.jwt import gerar_hash_senha
from sqlalchemy.orm import Session

from app.mensagens.models import Mensagem
from app.models.usuario import Usuario


def _criar_usuario(db: Session, username: str, role: str = "operador") -> Usuario:
    u = Usuario(
        username=username,
        email=f"{username}@x.com",
        nome_completo=username,
        senha_hash=gerar_hash_senha("senha123"),
        role=role,
    )
    db.add(u)
    db.commit()
    return u


def _token(client: TestClient, username: str) -> dict[str, str]:
    resp = client.post(
        "/v1/auth/token",
        json={"username": username, "password": "senha123"},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_fluxo_completo_mensagem_thread_e_lida(
    client: TestClient, db_session: Session
):
    a = _criar_usuario(db_session, "msg_a")
    b = _criar_usuario(db_session, "msg_b")
    h_a = _token(client, "msg_a")
    h_b = _token(client, "msg_b")

    # count inicial = 0
    resp = client.get("/v1/mensagens/nao-lidas/count", headers=h_a)
    assert resp.status_code == 200
    assert resp.json()["count"] == 0

    # A envia para B
    resp = client.post(
        "/v1/mensagens",
        headers=h_a,
        json={
            "destinatario_id": b.id,
            "titulo": "Pedido aprovado",
            "texto": "Seu pedido #88 foi aprovado.",
            "url_acao": "modules/home/index.html",
        },
    )
    assert resp.status_code == 200, resp.text
    raiz = resp.json()
    assert raiz["remetente_id"] == a.id
    assert raiz["categoria"] == "DIRETA"
    assert raiz["remetente_nome"] == "msg_a"

    # count de B = 1
    resp = client.get("/v1/mensagens/nao-lidas/count", headers=h_b)
    assert resp.json()["count"] == 1

    # B responde
    resp = client.post(
        f"/v1/mensagens/{raiz['id']}/respostas",
        headers=h_b,
        json={"texto": "Obrigado!"},
    )
    assert resp.status_code == 200, resp.text
    resposta = resp.json()
    assert resposta["resposta_a_id"] == raiz["id"]
    assert resposta["destinatario_id"] == a.id

    # thread de B lista raiz + resposta
    resp = client.get(f"/v1/mensagens/{raiz['id']}/thread", headers=h_b)
    assert resp.status_code == 200
    assert len(resp.json()) == 2

    # B marca thread como lida -> count de B volta a 0 (só a raiz era de B)
    resp = client.patch(f"/v1/mensagens/{raiz['id']}/thread/lida", headers=h_b)
    assert resp.status_code == 200
    assert resp.json()["count"] == 1

    resp = client.get("/v1/mensagens/nao-lidas/count", headers=h_b)
    assert resp.json()["count"] == 0


def test_sistema_aviso_requer_admin(client: TestClient, db_session: Session):
    comum = _criar_usuario(db_session, "msg_comum")
    alvo = _criar_usuario(db_session, "msg_alvo")
    h = _token(client, "msg_comum")

    resp = client.post(
        "/v1/mensagens",
        headers=h,
        json={
            "destinatario_id": alvo.id,
            "titulo": "Aviso",
            "texto": "Mensagem",
            "categoria": "AVISO",
        },
    )
    assert resp.status_code == 403, resp.text


def test_apenas_destinatario_marca_lida(client: TestClient, db_session: Session):
    a = _criar_usuario(db_session, "msg_a2")
    b = _criar_usuario(db_session, "msg_b2")
    c = _criar_usuario(db_session, "msg_c2")
    h_a = _token(client, "msg_a2")
    h_c = _token(client, "msg_c2")

    resp = client.post(
        "/v1/mensagens",
        headers=h_a,
        json={"destinatario_id": b.id, "titulo": "X", "texto": "Y"},
    )
    msg_id = resp.json()["id"]

    resp = client.patch(f"/v1/mensagens/{msg_id}/lida", headers=h_c)
    assert resp.status_code == 403, resp.text


def test_arquivar_restaura_via_body(client: TestClient, db_session: Session):
    a = _criar_usuario(db_session, "msg_a4")
    b = _criar_usuario(db_session, "msg_b4")
    h_a = _token(client, "msg_a4")
    h_b = _token(client, "msg_b4")

    resp = client.post(
        "/v1/mensagens",
        headers=h_a,
        json={"destinatario_id": b.id, "titulo": "Arq", "texto": "Texto"},
    )
    msg_id = resp.json()["id"]

    resp = client.patch(f"/v1/mensagens/{msg_id}/arquivar", headers=h_b)
    assert resp.status_code == 200
    assert resp.json()["arquivada_em"] is not None

    resp = client.patch(
        f"/v1/mensagens/{msg_id}/arquivar",
        headers=h_b,
        json={"arquivar": False},
    )
    assert resp.status_code == 200
    assert resp.json()["arquivada_em"] is None


def test_anexo_upload_e_download_autenticado(
    client: TestClient, db_session: Session, tmp_path, monkeypatch
):
    from app.mensagens import router as mensagens_router

    monkeypatch.setattr(mensagens_router, "UPLOADS_DIR", str(tmp_path))

    a = _criar_usuario(db_session, "msg_a3")
    b = _criar_usuario(db_session, "msg_b3")
    h_a = _token(client, "msg_a3")
    h_b = _token(client, "msg_b3")

    resp = client.post(
        "/v1/mensagens",
        headers=h_a,
        json={"destinatario_id": b.id, "titulo": "Com anexo", "texto": "Veja"},
    )
    msg_id = resp.json()["id"]

    resp = client.post(
        f"/v1/mensagens/{msg_id}/anexos",
        headers=h_a,
        files={"file": ("relatorio.pdf", b"%PDF-1.4 exemplo", "application/pdf")},
    )
    assert resp.status_code == 201, resp.text
    anexo = resp.json()
    assert anexo["nome_arquivo_original"] == "relatorio.pdf"
    assert anexo["tamanho_bytes"] == 14

    # terceiro não participa -> 403 no download
    c = _criar_usuario(db_session, "msg_c3")
    h_c = _token(client, "msg_c3")
    resp = client.get(
        f"/v1/mensagens/{msg_id}/anexos/{anexo['id']}/download", headers=h_c
    )
    assert resp.status_code == 403

    # participante (destinatário) baixa
    resp = client.get(
        f"/v1/mensagens/{msg_id}/anexos/{anexo['id']}/download", headers=h_b
    )
    assert resp.status_code == 200
    assert resp.content == b"%PDF-1.4 exemplo"

    # upload por não-remetente -> 403
    resp = client.post(
        f"/v1/mensagens/{msg_id}/anexos",
        headers=h_b,
        files={"file": ("x.txt", b"ola", "text/plain")},
    )
    assert resp.status_code == 403
```

- [ ] **Step 2: Run tests to verify they fail**

Run (workdir `apps/api-postgres`):
```bash
python -m pytest tests/integration/test_mensagens_api.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'app.mensagens.router'`

- [ ] **Step 3: Write the router**

Create `apps/api-postgres/app/mensagens/router.py`:

```python
"""Router do módulo central de mensagens."""

import os
import uuid

import structlog
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from shared.exceptions.base import ForbiddenError, NotFoundError
from shared.schemas.auth import TokenPayload
from shared.schemas.base import PaginatedResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.mensagens.models import Mensagem
from app.mensagens.schemas import (
    AnexoResponse,
    ArquivarRequest,
    CountResponse,
    MensagemCreate,
    MensagemResponse,
    OrdemMensagem,
    RespostaCreate,
    StatusMensagem,
)
from app.mensagens.service import MensagensService
from app.models.usuario import Usuario

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/v1/mensagens", tags=["Mensagens"])

UPLOADS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads"
)

MAX_ANEXO_BYTES = 10 * 1024 * 1024  # 10 MB
CONTENT_TYPES_PERMITIDOS = {
    "application/pdf",
    "text/plain",
    "text/csv",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/zip",
}


def _get_mensagens_service(db: Session = Depends(get_db)) -> MensagensService:
    return MensagensService(db)


def _is_admin(user: TokenPayload) -> bool:
    return user.role == "admin"


@router.get("", response_model=PaginatedResponse[MensagemResponse])
def listar_mensagens(
    status: StatusMensagem = Query(StatusMensagem.TODAS),
    ordem: OrdemMensagem = Query(OrdemMensagem.DECRESCENTE),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Lista as mensagens raiz do destinatário logado."""
    service = MensagensService(db)
    itens, total = service.listar_mensagens(
        int(current_user.sub), status, ordem, page, page_size
    )
    return PaginatedResponse(
        items=[MensagemResponse.model_validate(i) for i in itens],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/nao-lidas/count", response_model=CountResponse)
def contar_nao_lidas(
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Total de mensagens não lidas (raiz e respostas, excluindo arquivadas)."""
    service = MensagensService(db)
    return CountResponse(count=service.contar_nao_lidas(int(current_user.sub)))


@router.post("", response_model=MensagemResponse)
def criar_mensagem(
    dados: MensagemCreate,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Cria mensagem raiz. SISTEMA/AVISO exigem admin."""
    service = MensagensService(db)
    msg = service.criar_mensagem(
        int(current_user.sub), dados, is_admin=_is_admin(current_user)
    )
    resp = MensagemResponse.model_validate(msg)
    resp.remetente_nome = None
    if msg.remetente_id is not None:
        u = db.get(Usuario, msg.remetente_id)
        resp.remetente_nome = u.nome_completo if u else None
    return resp


@router.get("/{mensagem_id}/thread", response_model=list[MensagemResponse])
def listar_thread(
    mensagem_id: int,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Retorna a raiz e todas as respostas da thread."""
    service = MensagensService(db)
    itens = service.listar_thread(int(current_user.sub), mensagem_id)
    return [MensagemResponse.model_validate(i) for i in itens]


@router.post("/{mensagem_id}/respostas", response_model=MensagemResponse)
def criar_resposta(
    mensagem_id: int,
    dados: RespostaCreate,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Responde à thread (apenas participantes; categorias diretas)."""
    service = MensagensService(db)
    resposta = service.criar_resposta(
        int(current_user.sub), mensagem_id, dados
    )
    return MensagemResponse.model_validate(resposta)


@router.patch("/{mensagem_id}/lida", response_model=MensagemResponse)
def marcar_lida(
    mensagem_id: int,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Marca a mensagem como lida (apenas o destinatário)."""
    service = MensagensService(db)
    msg = service.marcar_lida(int(current_user.sub), mensagem_id)
    return MensagemResponse.model_validate(msg)


@router.patch("/{mensagem_id}/thread/lida", response_model=CountResponse)
def marcar_thread_lida(
    mensagem_id: int,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Marca todas as mensagens da thread destinadas ao usuário como lidas."""
    service = MensagensService(db)
    count = service.marcar_thread_lida(int(current_user.sub), mensagem_id)
    return CountResponse(count=count)


@router.patch("/{mensagem_id}/arquivar", response_model=MensagemResponse)
def arquivar_mensagem(
    mensagem_id: int,
    payload: ArquivarRequest | None = None,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Arquiva/restaura a thread (apenas o destinatário da raiz)."""
    service = MensagensService(db)
    arquivar = payload.arquivar if payload is not None else True
    msg = service.arquivar(int(current_user.sub), mensagem_id, arquivar=arquivar)
    return MensagemResponse.model_validate(msg)


@router.post(
    "/{mensagem_id}/anexos",
    response_model=AnexoResponse,
    status_code=201,
)
async def anexar_arquivo(
    mensagem_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Anexa um arquivo à mensagem (apenas o remetente da mensagem)."""
    msg = db.get(Mensagem, mensagem_id)
    if msg is None:
        raise NotFoundError("Mensagem", mensagem_id)
    if msg.remetente_id != int(current_user.sub):
        raise ForbiddenError(message="Apenas o remetente pode anexar arquivos.")

    if file.content_type not in CONTENT_TYPES_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de arquivo não permitido: {file.content_type}",
        )

    content = await file.read()
    if len(content) > MAX_ANEXO_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo muito grande. Tamanho máximo: {MAX_ANEXO_BYTES // (1024 * 1024)}MB",
        )

    ext = os.path.splitext(file.filename or "")[1].lower()
    unique_filename = f"{uuid.uuid4()}{ext}"
    sub_dir = "mensagens"
    dest_dir = os.path.join(UPLOADS_DIR, sub_dir)
    os.makedirs(dest_dir, exist_ok=True)
    caminho = os.path.join(sub_dir, unique_filename)
    file_path = os.path.join(dest_dir, unique_filename)
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    service = MensagensService(db)
    anexo = service.salvar_anexo_meta(
        mensagem_id=msg.id,
        nome_original=file.filename or unique_filename,
        caminho=caminho,
        content_type=file.content_type,
        tamanho_bytes=len(content),
    )
    logger.info("Anexo salvo", anexo_id=anexo.id, mensagem_id=msg.id, bytes=len(content))
    return anexo


@router.get("/{mensagem_id}/anexos", response_model=list[AnexoResponse])
def listar_anexos(
    mensagem_id: int,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Lista anexos da mensagem (participantes da thread)."""
    service = MensagensService(db)
    return service.listar_anexos(int(current_user.sub), mensagem_id)


@router.get("/{mensagem_id}/anexos/{anexo_id}/download")
def baixar_anexo(
    mensagem_id: int,
    anexo_id: int,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Baixa o anexo com autenticação (participantes da thread)."""
    service = MensagensService(db)
    anexo = service.obter_anexo(int(current_user.sub), mensagem_id, anexo_id)
    file_path = os.path.join(UPLOADS_DIR, anexo.caminho)
    if not os.path.exists(file_path):
        raise NotFoundError("Anexo", anexo_id)
    return FileResponse(
        file_path,
        media_type=anexo.content_type,
        filename=anexo.nome_arquivo_original,
    )
```

> **Route order warning:** FastAPI matches routes in declaration order. `POST /{mensagem_id}/respostas` and `PATCH /{mensagem_id}/lida` are declared before `/nao-lidas/count`? No — `/nao-lidas/count` is declared first (before any `/{mensagem_id}`). Keep the order as written above.

- [ ] **Step 4: Register the router in `app/main.py`**

Edit `apps/api-postgres/app/main.py`:
- Add import after `from app.auth.router import router as auth_router`:
  ```python
  from app.mensagens.router import router as mensagens_router
  ```
- Add `app.include_router(mensagens_router)` after `app.include_router(audit_router)`.

- [ ] **Step 5: Run tests to verify they pass**

Run (workdir `apps/api-postgres`):
```bash
python -m pytest tests/integration/test_mensagens_api.py -v
```
Expected: PASS (5 tests).

- [ ] **Step 6: Commit**

```bash
git add app/mensagens/router.py app/main.py tests/integration/test_mensagens_api.py
git commit -m "feat(mensagens): add /v1/mensagens router with threads and attachments"
```

---

## Task 6: Bridge `shared/notificationBridge.js` + testes

**Files:**
- Create: `apps/frontend-webapp/shared/notificationBridge.js`
- Test: `apps/frontend-webapp/tests/notificationBridge.test.js`

- [ ] **Step 1: Write the failing test**

Create `apps/frontend-webapp/tests/notificationBridge.test.js`:

```js
'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');

const { NotificationBridge } = require('../shared/notificationBridge.js');

function makeParent() {
    const calls = [];
    return {
        calls,
        postMessage: (data, origin) => calls.push({ data, origin })
    };
}

test('notifyMensagens envia postMessage ao pai em iframe', () => {
    const parent = makeParent();
    const bridge = new NotificationBridge({ parent, isIframe: true, origin: '*' });
    assert.equal(bridge.notifyMensagens(), true);
    assert.deepEqual(parent.calls[0].data, { type: 'grindx:mensagens-atualizar' });
});

test('navegarPara envia tipo e url', () => {
    const parent = makeParent();
    const bridge = new NotificationBridge({ parent, isIframe: true, origin: '*' });
    bridge.navegarPara('modules/estoque/index.html');
    assert.deepEqual(parent.calls[0].data, {
        type: 'grindx:navegar',
        url: 'modules/estoque/index.html'
    });
});

test('fora de iframe não envia nada', () => {
    const parent = makeParent();
    const bridge = new NotificationBridge({ parent, isIframe: false, origin: '*' });
    assert.equal(bridge.notifyMensagens(), false);
    assert.equal(parent.calls.length, 0);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run (workdir `apps/frontend-webapp`):
```bash
node --test tests/notificationBridge.test.js
```
Expected: FAIL — `Cannot find module '../shared/notificationBridge.js'`

- [ ] **Step 3: Write the bridge**

Create `apps/frontend-webapp/shared/notificationBridge.js`:

```js
/**
 * Notification Bridge — GrindX
 *
 * Comunicação módulo (iframe) -> janela pai via postMessage.
 *  - notifyMensagens(): avisa o pai para recalcular o contador de não lidas.
 *  - navegarPara(url): pede ao pai para navegar o iframe para um caminho interno.
 *
 * Uso no browser: carregado após apiService.js. Expõe window.grindx.notifyMensagens
 * e window.grindx.navegarPara.
 * Uso em testes: module.exports = { NotificationBridge } (Node test runner).
 */

(function initNotificationBridge(globalScope) {
    function isIframe(win) {
        if (!win) return true;
        try {
            return win.self !== win.top;
        } catch (e) {
            return true;
        }
    }

    class NotificationBridge {
        constructor(options = {}) {
            const win = options.window || globalScope.window || null;
            this.window = win;
            this.parent = options.parent || (win ? win.parent : null);
            this.origin = options.origin || '*';
            this._isIframe = options.isIframe !== undefined
                ? options.isIframe
                : isIframe(win);
        }

        notifyMensagens() {
            return this._post('grindx:mensagens-atualizar');
        }

        navegarPara(url) {
            return this._post('grindx:navegar', { url });
        }

        _post(type, payload) {
            if (!this._isIframe || !this.parent || typeof this.parent.postMessage !== 'function') {
                return false;
            }
            this.parent.postMessage(Object.assign({ type }, payload || {}), this.origin);
            return true;
        }
    }

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = { NotificationBridge };
    }

    if (globalScope && globalScope.document) {
        globalScope.grindx = globalScope.grindx || {};
        const bridge = new NotificationBridge({ window: globalScope });
        globalScope.grindx.notifyMensagens = function () {
            return bridge.notifyMensagens();
        };
        globalScope.grindx.navegarPara = function (url) {
            return bridge.navegarPara(url);
        };
    }
})(typeof window !== 'undefined' ? window : (typeof globalThis !== 'undefined' ? globalThis : this));
```

- [ ] **Step 4: Run test to verify it passes**

Run (workdir `apps/frontend-webapp`):
```bash
node --test tests/notificationBridge.test.js
```
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add shared/notificationBridge.js tests/notificationBridge.test.js
git commit -m "feat(frontend): add notificationBridge for iframe-to-parent messaging"
```

---

## Task 7: Widget `shared/mensagensWidget.js` + testes + integração no mascote

**Files:**
- Create: `apps/frontend-webapp/shared/mensagensWidget.js`
- Test: `apps/frontend-webapp/tests/mensagensWidget.test.js`
- Modify: `apps/frontend-webapp/widget/widget.js`
- Modify: `apps/frontend-webapp/widget/widget.css`

- [ ] **Step 1: Write the failing test**

Create `apps/frontend-webapp/tests/mensagensWidget.test.js`:

```js
'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');

const { MensagensWidget } = require('../shared/mensagensWidget.js');

function fakeClassList() {
    const classes = new Set();
    return {
        classes,
        add: (c) => classes.add(c),
        remove: (c) => classes.delete(c),
        toggle: (c, force) => {
            const show = force !== undefined ? force : !classes.has(c);
            if (show) classes.add(c); else classes.delete(c);
            return show;
        },
        contains: (c) => classes.has(c)
    };
}

function fakeEl() {
    return { textContent: '', classList: fakeClassList(), setAttribute() {} };
}

test('count 0 esconde badge e balão', async () => {
    const badge = fakeEl();
    const balloon = fakeEl();
    const widget = new MensagensWidget({
        badge, balloon,
        getUnread: async () => 0,
        autoInit: false
    });
    await widget.refresh();
    assert.equal(badge.textContent, '');
    assert.equal(badge.classList.contains('visible'), false);
    assert.equal(balloon.classList.contains('visible'), false);
});

test('count > 0 mostra badge e balão até marcar visto', async () => {
    const badge = fakeEl();
    const balloon = fakeEl();
    const widget = new MensagensWidget({
        badge, balloon,
        getUnread: async () => 3,
        autoInit: false
    });
    await widget.refresh();
    assert.equal(badge.textContent, '3');
    assert.equal(badge.classList.contains('visible'), true);
    assert.equal(balloon.classList.contains('visible'), true);

    widget.markSeen();
    assert.equal(balloon.classList.contains('visible'), false);
    assert.equal(badge.classList.contains('visible'), true, 'badge permanece visível');
});

test('refresh dispara onCountChange e nova mensagem reaparece balão', async () => {
    let unread = 2;
    const balloon = fakeEl();
    let lastCount = null;
    const widget = new MensagensWidget({
        badge: fakeEl(), balloon,
        getUnread: async () => unread,
        onCountChange: (c) => { lastCount = c; },
        autoInit: false
    });
    await widget.refresh();
    assert.equal(lastCount, 2);
    widget.markSeen();
    assert.equal(balloon.classList.contains('visible'), false);

    unread = 5;
    await widget.refresh();
    assert.equal(lastCount, 5);
    assert.equal(balloon.classList.contains('visible'), true, 'novo recado reaparece');
});
```

- [ ] **Step 2: Run test to verify it fails**

Run (workdir `apps/frontend-webapp`):
```bash
node --test tests/mensagensWidget.test.js
```
Expected: FAIL — `Cannot find module '../shared/mensagensWidget.js'`

- [ ] **Step 3: Write the widget manager**

Create `apps/frontend-webapp/shared/mensagensWidget.js`:

```js
/**
 * Mensagens Widget Manager — GrindX
 *
 * Gerencia o estado do contador de mensagens não lidas no mascote:
 * badge (contagem) e balão de fala clicável.
 *
 * Uso no browser: widget.js cria os elementos DOM e instancia este manager,
 * expondo window.grindx.mensagens.
 * Uso em testes: module.exports = { MensagensWidget } (Node test runner).
 */

(function initMensagensWidget(globalScope) {
    const DEFAULT_POLL_INTERVAL = 10 * 60 * 1000; // 10 minutos

    class MensagensWidget {
        constructor(options = {}) {
            this.badge = options.badge || null;
            this.balloon = options.balloon || null;
            this.api = options.api || null;
            this.onOpenRecados = options.onOpenRecados || null;
            this.onCountChange = options.onCountChange || null;
            this.POLL_INTERVAL = options.pollInterval || DEFAULT_POLL_INTERVAL;

            this.count = 0;
            this.seen = false;
            this.intervalId = null;

            this.getUnread = options.getUnread || this._defaultGetUnread.bind(this);

            if (options.autoInit !== false) this.init();
        }

        _defaultGetUnread() {
            if (!this.api || typeof this.api.get !== 'function') {
                return Promise.resolve(0);
            }
            return this.api
                .get('/mensagens/nao-lidas/count')
                .then((data) => (data && typeof data.count === 'number') ? data.count : 0)
                .catch(() => 0);
        }

        init() {
            this.refresh();
            this.startPolling();
        }

        startPolling() {
            if (this.intervalId) clearInterval(this.intervalId);
            this.intervalId = setInterval(() => this.refresh(), this.POLL_INTERVAL);
        }

        stopPolling() {
            if (this.intervalId) {
                clearInterval(this.intervalId);
                this.intervalId = null;
            }
        }

        async refresh() {
            const next = await this.getUnread();
            this.count = next;
            this.render();
            if (this.onCountChange) this.onCountChange(next);
            return next;
        }

        markSeen() {
            this.seen = true;
            this.render();
        }

        openRecados() {
            this.markSeen();
            if (this.onOpenRecados) this.onOpenRecados();
        }

        render() {
            if (this.badge) {
                this.badge.textContent = this.count > 0 ? String(this.count) : '';
                this.badge.classList.toggle('visible', this.count > 0);
                this.badge.setAttribute('aria-hidden', this.count > 0 ? 'false' : 'true');
            }
            if (this.balloon) {
                const show = this.count > 0 && !this.seen;
                this.balloon.classList.toggle('visible', show);
                this.balloon.setAttribute('aria-hidden', show ? 'false' : 'true');
            }
        }
    }

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = { MensagensWidget };
    }

    if (globalScope && globalScope.document) {
        globalScope.grindx = globalScope.grindx || {};
        globalScope.grindx.MensagensWidget = MensagensWidget;
    }
})(typeof window !== 'undefined' ? window : (typeof globalThis !== 'undefined' ? globalThis : this));
```

- [ ] **Step 4: Run test to verify it passes**

Run (workdir `apps/frontend-webapp`):
```bash
node --test tests/mensagensWidget.test.js
```
Expected: PASS (3 tests)

- [ ] **Step 5: Integrate no mascote — modificar `widget/widget.js`**

Edit `apps/frontend-webapp/widget/widget.js`:

a) Add at the top of the IIFE (before `createWidget` is called), a helper that updates the balloon text and the dropdown badges:

```js
    function renderMensagensCount(count) {
        const strong = document.querySelector('.grindx-ai-msg-bubble-text strong');
        if (strong) strong.textContent = count;
        document.querySelectorAll('[data-mensagens-badge]').forEach((el) => {
            el.textContent = count > 0 ? String(count) : '';
            el.classList.toggle('visible', count > 0);
        });
    }
```

b) In `createWidget()`, after `document.body.appendChild(bubble);` (line ~69), add the badge, the message balloon and the `MensagensWidget` instantiation:

```js
        // ---- Contador de mensagens não lidas (Mensageiro) ----
        const unreadBadge = document.createElement('span');
        unreadBadge.className = 'grindx-ai-badge';
        unreadBadge.setAttribute('aria-hidden', 'true');
        fab.appendChild(unreadBadge);

        const msgBubble = document.createElement('div');
        msgBubble.className = 'grindx-ai-msg-bubble';
        msgBubble.setAttribute('role', 'button');
        msgBubble.setAttribute('tabindex', '0');
        msgBubble.setAttribute('aria-hidden', 'true');
        msgBubble.setAttribute('aria-label', 'Abrir recados');
        msgBubble.innerHTML =
            '<span class="grindx-ai-msg-bubble-icon"><i class="fas fa-envelope" aria-hidden="true"></i></span>' +
            '<span class="grindx-ai-msg-bubble-text">Você tem <strong>0</strong> novos recados!</span>';
        document.body.appendChild(msgBubble);

        const mensagens = window.grindx.MensagensWidget
            ? new window.grindx.MensagensWidget({
                badge: unreadBadge,
                balloon: msgBubble,
                api: window.grindx.api,
                onCountChange: renderMensagensCount,
                onOpenRecados: () => {
                    if (window.dashboard && typeof window.dashboard.navigateToModule === 'function') {
                        window.dashboard.navigateToModule('modules/mensagens/index.html');
                    }
                }
            })
            : null;
        window.grindx.mensagens = mensagens;

        msgBubble.addEventListener('click', () => {
            if (mensagens) mensagens.openRecados();
        });
        msgBubble.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                if (mensagens) mensagens.openRecados();
            }
        });
```

- [ ] **Step 6: Add CSS em `widget/widget.css`**

Append to `apps/frontend-webapp/widget/widget.css`:

```css
/* ---- Contador de não lidas no mascote (Mensageiro) ---- */
.grindx-ai-badge {
    position: absolute;
    top: -4px;
    right: -4px;
    min-width: 20px;
    height: 20px;
    padding: 0 5px;
    border-radius: 10px;
    background: var(--skin-danger, #dc2626);
    color: #fff;
    font-size: 0.72rem;
    font-weight: 700;
    line-height: 20px;
    text-align: center;
    display: none;
}
.grindx-ai-badge.visible {
    display: inline-block;
}

.grindx-ai-msg-bubble {
    position: fixed;
    right: 84px;
    bottom: 24px;
    max-width: 300px;
    padding: 12px 16px;
    border-radius: 12px;
    background: var(--skin-surface, #ffffff);
    color: var(--skin-text, #1f2937);
    border: 1px solid var(--skin-border, rgba(255, 255, 255, 0.18));
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
    display: none;
    cursor: pointer;
    align-items: center;
    gap: 10px;
    z-index: 10000;
}
.grindx-ai-msg-bubble.visible {
    display: flex;
}
.grindx-ai-msg-bubble-icon {
    color: var(--skin-primary, #00c2e0);
    font-size: 1.1rem;
}
.grindx-ai-msg-bubble-text {
    font-size: 0.85rem;
    line-height: 1.35;
}
```

- [ ] **Step 7: Commit**

```bash
git add shared/mensagensWidget.js tests/mensagensWidget.test.js widget/widget.js widget/widget.css
git commit -m "feat(frontend): add unread badge and balloon to mascot widget"
```

---

## Task 8: Dropdown "Mensagens" no dashboard + listener postMessage

**Files:**
- Modify: `apps/frontend-webapp/dashboard.html`
- Modify: `apps/frontend-webapp/dashboard.js`

- [ ] **Step 1: Add script e botão no `dashboard.html`**

Edit `apps/frontend-webapp/dashboard.html`:

a) Add the bridge script after `shared/apiService.js`:
```html
    <script src="shared/apiService.js"></script>
    <script src="shared/notificationBridge.js"></script>
```

b) Add a "Mensagens" item in BOTH dropdowns, below "Meu Perfil". Sidebar dropdown (after the `data-profile` button, before the divider/logout):
```html
                         <button class="nav-dropdown-item" role="menuitem" data-profile="true">
                             <i class="fas fa-user"></i> Meu Perfil
                         </button>
                         <button class="nav-dropdown-item" role="menuitem" data-mensagens="true">
                             <i class="fas fa-envelope"></i> Mensagens
                             <span class="nav-dropdown-badge" data-mensagens-badge aria-hidden="true"></span>
                         </button>
                         <div class="nav-dropdown-divider"></div>
```

Topbar dropdown (same pattern after its `data-profile` button):
```html
                    <button class="nav-dropdown-item" role="menuitem" data-profile="true">
                        <i class="fas fa-user"></i> Meu Perfil
                    </button>
                    <button class="nav-dropdown-item" role="menuitem" data-mensagens="true">
                        <i class="fas fa-envelope"></i> Mensagens
                        <span class="nav-dropdown-badge" data-mensagens-badge aria-hidden="true"></span>
                    </button>
                    <div class="nav-dropdown-divider"></div>
```

- [ ] **Step 2: Adicionar listener e navegação em `dashboard.js`**

Edit `apps/frontend-webapp/dashboard.js`:

a) In the `window.addEventListener('message', ...)` block inside `bindEvents` (around line 118), add mensagens handling. The existing block starts with `window.addEventListener('message', (e) => { if (e.data === 'sidebar-update') ...` — append:

```js
            if (e.data && e.data.type === 'grindx:mensagens-atualizar') {
                if (window.grindx.mensagens && typeof window.grindx.mensagens.refresh === 'function') {
                    window.grindx.mensagens.refresh();
                }
            }
            if (e.data && e.data.type === 'grindx:navegar' && typeof e.data.url === 'string') {
                if (this.isInternalPath(e.data.url)) {
                    this.navigateToModule(e.data.url);
                }
            }
```

b) Add a method `isInternalPath(url)` to `DashboardController`:

```js
    isInternalPath(url) {
        return !!url
            && url.indexOf('://') === -1
            && url.indexOf('javascript:') === -1
            && url.indexOf('data:') === -1
            && url.indexOf('vbscript:') === -1
            && url.startsWith('modules/');
    }
```

c) Wire the new dropdown buttons in `bindEvents` (next to the existing `[data-profile="true"]` handler):

```js
            document.querySelectorAll('[data-mensagens="true"]').forEach((btn) => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.navigateToModule('modules/mensagens/index.html');
                    document.querySelectorAll('.logo-clickable.open').forEach((el) => {
                        el.classList.remove('open');
                    });
                });
            });
```

d) Refresh the dropdown badges on startup — add to the existing `init()` flow (e.g., after `loadDynamicMenu()`), calling `window.grindx.mensagens.refresh()` if present:

```js
        if (window.grindx.mensagens && typeof window.grindx.mensagens.refresh === 'function') {
            window.grindx.mensagens.refresh();
        }
```

- [ ] **Step 3: Adicionar CSS do badge no dropdown**

Append to `apps/frontend-webapp/dashboard.css`:

```css
.nav-dropdown-badge {
    margin-left: auto;
    min-width: 18px;
    height: 18px;
    padding: 0 4px;
    border-radius: 9px;
    background: var(--skin-danger, #dc2626);
    color: #fff;
    font-size: 0.7rem;
    font-weight: 700;
    line-height: 18px;
    text-align: center;
    display: none;
}
.nav-dropdown-badge.visible {
    display: inline-block;
}
```

- [ ] **Step 4: Smoke-test de sintaxe**

Run (workdir `apps/frontend-webapp`):
```bash
node --check dashboard.js && node --check widget/widget.js && node --check shared/notificationBridge.js && node --check shared/mensagensWidget.js
```
Expected: no output (OK)

- [ ] **Step 5: Commit**

```bash
git add dashboard.html dashboard.js dashboard.css
git commit -m "feat(frontend): add Mensagens dropdown item and postMessage listener"
```

---

## Task 9: Módulo frontend `modules/mensagens/`

**Files:**
- Create: `apps/frontend-webapp/modules/mensagens/index.html`
- Create: `apps/frontend-webapp/modules/mensagens/style.css`
- Create: `apps/frontend-webapp/modules/mensagens/script.js`

- [ ] **Step 1: Write `index.html`**

Create `apps/frontend-webapp/modules/mensagens/index.html`:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GrindX — Mensagens</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="../../shared/core.css">
    <link rel="stylesheet" href="style.css">
</head>
<body class="module-page">
    <div class="container animate-in">
        <header class="page-header mb-8">
            <div>
                <div class="page-header-container">
                    <h1>Mensagens</h1>
                    <span class="viz-version" id="viz-version" aria-label="Versão do sistema"></span>
                </div>
                <p class="text-muted">Recados internos, avisos e notificações do sistema.</p>
            </div>
        </header>

        <section class="msg-toolbar" aria-label="Filtros e ações">
            <div class="msg-toolbar-filters">
                <label class="msg-select-label">
                    <span>Status</span>
                    <select id="statusFilter" class="form-control">
                        <option value="todas">Todas</option>
                        <option value="nao_lidas">Não lidas</option>
                        <option value="lidas">Lidas</option>
                        <option value="arquivadas">Arquivadas</option>
                    </select>
                </label>
                <label class="msg-select-label">
                    <span>Ordenar por data</span>
                    <select id="ordemFilter" class="form-control">
                        <option value="decrescente">Mais recentes primeiro</option>
                        <option value="crescente">Mais antigas primeiro</option>
                    </select>
                </label>
            </div>
            <button class="btn btn-primary" id="novaMensagemBtn" type="button">
                <i class="fas fa-paper-plane"></i> Nova Mensagem
            </button>
        </section>

        <section id="listaView" aria-label="Lista de mensagens">
            <div id="listaMensagens" class="msg-list"></div>
            <footer class="msg-pagination">
                <button class="btn btn-outline" id="listaPrev" aria-label="Página anterior">
                    <i class="fas fa-chevron-left"></i> Anterior
                </button>
                <span class="msg-page-info" id="listaPageInfo"></span>
                <button class="btn btn-outline" id="listaNext" aria-label="Próxima página">
                    Próxima <i class="fas fa-chevron-right"></i>
                </button>
            </footer>
        </section>

        <section id="threadView" class="msg-thread" style="display: none;" aria-label="Conversa">
            <div class="msg-thread-header">
                <button class="btn btn-outline" id="voltarBtn" type="button">
                    <i class="fas fa-arrow-left"></i> Voltar
                </button>
                <h2 id="threadTitulo"></h2>
            </div>
            <div id="threadMensagens" class="msg-thread-mensagens"></div>
            <div class="msg-thread-reply">
                <textarea id="respostaTexto" class="form-control" rows="3"
                          placeholder="Escreva sua resposta..." aria-label="Resposta"></textarea>
                <div class="msg-thread-reply-actions">
                    <label class="btn btn-outline msg-file-btn">
                        <i class="fas fa-paperclip"></i> Anexar
                        <input type="file" id="respostaAnexos" multiple style="display:none;">
                    </label>
                    <button class="btn btn-primary" id="enviarRespostaBtn" type="button">
                        <i class="fas fa-paper-plane"></i> Responder
                    </button>
                </div>
                <div id="respostaArquivos" class="msg-anexos-pendentes"></div>
            </div>
        </section>
    </div>

    <!-- Modal Nova Mensagem -->
    <div class="msg-modal-overlay" id="composeModal" style="display:none;" role="dialog" aria-modal="true" aria-label="Nova mensagem">
        <div class="msg-modal">
            <header class="msg-modal-header">
                <h3>Nova Mensagem</h3>
                <button class="btn-icon" id="fecharModalBtn" aria-label="Fechar">&times;</button>
            </header>
            <form id="composeForm" class="msg-modal-body">
                <div class="form-group">
                    <label for="destinatarioSelect">Destinatário</label>
                    <select id="destinatarioSelect" class="form-control" required></select>
                </div>
                <div class="form-group">
                    <label for="categoriaSelect">Categoria</label>
                    <select id="categoriaSelect" class="form-control">
                        <option value="DIRETA">Direta</option>
                        <option value="AVISO">Aviso</option>
                        <option value="SISTEMA">Sistema</option>
                    </select>
                    <p class="text-muted msg-hint" id="categoriaHint">Apenas administradores podem enviar Avisos ou mensagens do Sistema.</p>
                </div>
                <div class="form-group">
                    <label for="tituloInput">Título</label>
                    <input type="text" id="tituloInput" class="form-control" maxlength="150" required>
                </div>
                <div class="form-group">
                    <label for="textoInput">Texto</label>
                    <textarea id="textoInput" class="form-control" rows="4" required></textarea>
                </div>
                <div class="form-group">
                    <label for="urlAcaoInput">URL de ação (opcional)</label>
                    <input type="text" id="urlAcaoInput" class="form-control" maxlength="255"
                           placeholder="modules/estoque/index.html">
                    <p class="text-muted msg-hint">Caminho interno aberto ao clicar na mensagem.</p>
                </div>
                <div class="form-group">
                    <label>Anexos (opcional)</label>
                    <label class="btn btn-outline msg-file-btn">
                        <i class="fas fa-paperclip"></i> Escolher arquivos
                        <input type="file" id="composeAnexos" multiple style="display:none;">
                    </label>
                    <div id="composeArquivos" class="msg-anexos-pendentes"></div>
                </div>
            </form>
            <footer class="msg-modal-footer">
                <button class="btn btn-secondary" id="cancelarModalBtn" type="button">Cancelar</button>
                <button class="btn btn-primary" id="enviarMensagemBtn" type="button">
                    <i class="fas fa-paper-plane"></i> Enviar
                </button>
            </footer>
        </div>
    </div>

    <script src="../../shared/config.js"></script>
    <script src="../../shared/app.js"></script>
    <script src="../../shared/apiService.js"></script>
    <script src="../../shared/baseController.js"></script>
    <script src="../../shared/notificationBridge.js"></script>
    <script src="../../shared/components/LoadingSpinner.js"></script>
    <script src="script.js"></script>
</body>
</html>
```

- [ ] **Step 2: Write `style.css`**

Create `apps/frontend-webapp/modules/mensagens/style.css`:

```css
/* Módulo Mensagens — GrindX (tokens do design system) */

.msg-toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: flex-end;
    justify-content: space-between;
    margin-bottom: 16px;
}

.msg-toolbar-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}

.msg-select-label {
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 0.85rem;
    color: var(--skin-text-muted, #6b7280);
}

.msg-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.msg-card {
    border: 1px solid var(--skin-border, rgba(255, 255, 255, 0.12));
    border-radius: 12px;
    padding: 14px 16px;
    background: var(--skin-surface, rgba(255, 255, 255, 0.06));
    cursor: pointer;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.msg-card:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.msg-card.nao-lida {
    border-left: 3px solid var(--skin-primary, #00c2e0);
}

.msg-card-head {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
}

.msg-categoria {
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 999px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.msg-categoria.SISTEMA { background: rgba(99, 102, 241, 0.18); color: var(--skin-primary, #818cf8); }
.msg-categoria.DIRETA  { background: rgba(0, 194, 224, 0.16); color: var(--skin-primary, #00c2e0); }
.msg-categoria.AVISO   { background: rgba(245, 158, 11, 0.18); color: #f59e0b; }

.msg-card-title {
    font-weight: 600;
    font-size: 0.95rem;
    margin: 0;
    flex: 1;
}

.msg-card-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    font-size: 0.78rem;
    color: var(--skin-text-muted, #9ca3af);
    margin-bottom: 4px;
}

.msg-card-texto {
    font-size: 0.85rem;
    color: var(--skin-text, #1f2937);
    margin: 0 0 6px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.msg-card-actions {
    display: flex;
    gap: 8px;
    margin-top: 8px;
}

.msg-card-replies {
    font-size: 0.75rem;
    color: var(--skin-text-muted, #9ca3af);
}

.msg-pagination {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 16px;
}

.msg-page-info {
    font-size: 0.85rem;
    color: var(--skin-text-muted, #9ca3af);
}

.msg-empty {
    text-align: center;
    padding: 40px 16px;
    color: var(--skin-text-muted, #9ca3af);
    font-size: 0.9rem;
}

.msg-thread-mensagens {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 16px;
}

.msg-thread-item {
    border: 1px solid var(--skin-border, rgba(255, 255, 255, 0.12));
    border-radius: 12px;
    padding: 12px 14px;
    background: var(--skin-surface, rgba(255, 255, 255, 0.06));
}

.msg-thread-item .msg-card-title { margin-bottom: 4px; }
.msg-thread-item .msg-card-texto { -webkit-line-clamp: unset; overflow: visible; }

.msg-thread-reply {
    border-top: 1px solid var(--skin-border, rgba(255, 255, 255, 0.12));
    padding-top: 12px;
}

.msg-thread-reply-actions {
    display: flex;
    gap: 8px;
    margin-top: 8px;
    align-items: center;
}

.msg-file-btn { cursor: pointer; }

.msg-anexos-pendentes {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 8px;
}

.msg-anexo-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.75rem;
    padding: 3px 8px;
    border-radius: 999px;
    background: var(--skin-surface, rgba(255, 255, 255, 0.08));
    border: 1px solid var(--skin-border, rgba(255, 255, 255, 0.12));
}

.msg-anexo-chip button {
    background: none;
    border: none;
    color: var(--skin-danger, #dc2626);
    cursor: pointer;
    font-size: 0.85rem;
    line-height: 1;
}

/* Modal */
.msg-modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.msg-modal {
    width: min(520px, 92vw);
    max-height: 88vh;
    display: flex;
    flex-direction: column;
    border-radius: 16px;
    background: var(--skin-bg, #0f172a);
    border: 1px solid var(--skin-border, rgba(255, 255, 255, 0.12));
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
}

.msg-modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid var(--skin-border, rgba(255, 255, 255, 0.12));
}

.msg-modal-body {
    padding: 16px 20px;
    overflow-y: auto;
}

.msg-modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    padding: 12px 20px;
    border-top: 1px solid var(--skin-border, rgba(255, 255, 255, 0.12));
}

.msg-hint {
    font-size: 0.75rem;
    margin-top: 4px;
}

.msg-thread-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
}

.msg-thread-header h2 {
    margin: 0;
    font-size: 1.1rem;
}
```

- [ ] **Step 3: Write `script.js`**

Create `apps/frontend-webapp/modules/mensagens/script.js`:

```js
/**
 * MENSAGENS MODULE — GrindX
 * Lista, envia e responde mensagens internas; marca como lida; arquiva; anexa arquivos.
 */

class MensagensController extends window.grindx.controllers.BaseController {
    constructor() {
        super();
        this.PAGE_SIZE = 20;
        this.page = 1;
        this.totalPages = 0;
        this.status = 'todas';
        this.ordem = 'decrescente';
        this.threadId = null;
        this.composeFiles = [];
        this.replyFiles = [];
        this.init();
    }

    async init() {
        if (!this.requireAuth('../../index.html')) return;
        this.setBadgeVersao();
        this.bindEvents();
        await this.carregarDestinatarios();
        await this.loadLista();
    }

    bindEvents() {
        document.getElementById('statusFilter').addEventListener('change', (e) => {
            this.status = e.target.value;
            this.page = 1;
            this.loadLista();
        });
        document.getElementById('ordemFilter').addEventListener('change', (e) => {
            this.ordem = e.target.value;
            this.page = 1;
            this.loadLista();
        });
        document.getElementById('listaPrev').addEventListener('click', () => this.changePage(-1));
        document.getElementById('listaNext').addEventListener('click', () => this.changePage(1));
        document.getElementById('novaMensagemBtn').addEventListener('click', () => this.abrirModal());
        document.getElementById('fecharModalBtn').addEventListener('click', () => this.fecharModal());
        document.getElementById('cancelarModalBtn').addEventListener('click', () => this.fecharModal());
        document.getElementById('enviarMensagemBtn').addEventListener('click', () => this.enviarMensagem());
        document.getElementById('voltarBtn').addEventListener('click', () => this.voltarLista());
        document.getElementById('enviarRespostaBtn').addEventListener('click', () => this.enviarResposta());
        document.getElementById('composeAnexos').addEventListener('change', (e) => {
            this.composeFiles = Array.from(e.target.files || []);
            this.renderArquivosPendentes('composeArquivos', this.composeFiles);
        });
        document.getElementById('respostaAnexos').addEventListener('change', (e) => {
            this.replyFiles = Array.from(e.target.files || []);
            this.renderArquivosPendentes('respostaArquivos', this.replyFiles);
        });
    }

    async carregarDestinatarios() {
        try {
            const data = await window.grindx.api.get('/usuarios', { page_size: 100 });
            const me = window.grindx.session.getUserProfile();
            const items = (data.items || []).filter((u) => String(u.id) !== String(me.id));
            const select = document.getElementById('destinatarioSelect');
            select.innerHTML = items.map((u) =>
                `<option value="${u.id}">${u.nome_completo || u.username}</option>`
            ).join('');
        } catch (err) {
            console.error('Erro ao carregar destinatários:', err);
        }
    }

    async loadLista() {
        try {
            const data = await window.grindx.api.get('/mensagens', {
                status: this.status,
                ordem: this.ordem,
                page: this.page,
                page_size: this.PAGE_SIZE
            });
            this.renderLista(data);
        } catch (err) {
            console.error('Erro ao carregar mensagens:', err);
            document.getElementById('listaMensagens').innerHTML =
                '<div class="msg-empty">Erro ao carregar mensagens.</div>';
        }
    }

    renderLista(data) {
        const container = document.getElementById('listaMensagens');
        const items = data.items || [];
        if (items.length === 0) {
            container.innerHTML = '<div class="msg-empty">Nenhuma mensagem encontrada.</div>';
        } else {
            container.innerHTML = items.map((m) => this.cardHtml(m)).join('');
            container.querySelectorAll('[data-abrir]').forEach((el) => {
                el.addEventListener('click', () => this.abrirThread(el.dataset.abrir));
            });
            container.querySelectorAll('[data-arquivar]').forEach((el) => {
                el.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.toggleArquivar(el.dataset.arquivar);
                });
            });
        }
        this.totalPages = data.total_pages || 0;
        this.updatePagination(data);
        if (window.grindx.mensagens) window.grindx.mensagens.refresh();
    }

    cardHtml(m) {
        const naoLida = this.temAtividadeNaoLida(m);
        const catClass = (m.categoria || 'DIRETA').toUpperCase();
        return `
            <article class="msg-card ${naoLida ? 'nao-lida' : ''}" data-abrir="${m.id}" tabindex="0" role="button"
                     aria-label="Abrir mensagem ${m.titulo}">
                <div class="msg-card-head">
                    <span class="msg-categoria ${catClass}">${catClass}</span>
                    <h3 class="msg-card-title">${this.escapeHtml(m.titulo)}</h3>
                </div>
                <div class="msg-card-meta">
                    <span>${m.remetente_nome || 'Sistema'}</span>
                    <span>${this.formatDate(m.criado_em)}</span>
                    ${m.quantidade_respostas > 0
                        ? `<span class="msg-card-replies"><i class="fas fa-reply"></i> ${m.quantidade_respostas}</span>` : ''}
                    ${m.anexos_count > 0
                        ? `<span class="msg-card-replies"><i class="fas fa-paperclip"></i> ${m.anexos_count}</span>` : ''}
                </div>
                <p class="msg-card-texto">${this.escapeHtml(m.texto)}</p>
                <div class="msg-card-actions">
                    ${m.arquivada_em
                        ? `<button class="btn btn-outline btn-sm" data-arquivar="${m.id}"><i class="fas fa-undo"></i> Restaurar</button>`
                        : `<button class="btn btn-outline btn-sm" data-arquivar="${m.id}"><i class="fas fa-archive"></i> Arquivar</button>`}
                </div>
            </article>
        `;
    }

    temAtividadeNaoLida(m) {
        return !m.lida_em;
    }

    updatePagination(data) {
        const info = document.getElementById('listaPageInfo');
        info.textContent = `Página ${data.page} de ${data.total_pages || 0}`;
        document.getElementById('listaPrev').disabled = data.page <= 1;
        document.getElementById('listaNext').disabled = data.page >= (data.total_pages || 0);
    }

    changePage(delta) {
        const next = this.page + delta;
        if (next < 1 || next > this.totalPages) return;
        this.page = next;
        this.loadLista();
    }

    async abrirThread(mensagemId) {
        this.threadId = mensagemId;
        try {
            const itens = await window.grindx.api.get(`/mensagens/${mensagemId}/thread`);
            this.renderThread(itens);
            await window.grindx.api.patch(`/mensagens/${mensagemId}/thread/lida`);
            if (window.grindx.notifyMensagens) window.grindx.notifyMensagens();
            const raiz = itens[0];
            this.mostrarBotaoAcao(raiz);
        } catch (err) {
            console.error('Erro ao abrir thread:', err);
        }
    }

    renderThread(itens) {
        document.getElementById('listaView').style.display = 'none';
        document.getElementById('threadView').style.display = 'block';
        document.getElementById('threadTitulo').textContent = itens[0] ? itens[0].titulo : '';
        const container = document.getElementById('threadMensagens');
        container.innerHTML = itens.map((m) => this.threadItemHtml(m)).join('');
        container.querySelectorAll('[data-download]').forEach((el) => {
            el.addEventListener('click', () => {
                const [mid, aid, nome] = el.dataset.download.split('::');
                this.downloadAnexo(mid, aid, nome);
            });
        });
        if (window.grindx.notifyMensagens) window.grindx.notifyMensagens();
    }

    threadItemHtml(m) {
        const catClass = (m.categoria || 'DIRETA').toUpperCase();
        const anexos = (m.anexos || []).map((a) =>
            `<span class="msg-anexo-chip">
                <i class="fas fa-paperclip"></i> ${this.escapeHtml(a.nome_arquivo_original)}
                <button type="button" data-download="${m.id}::${a.id}::${this.escapeHtml(a.nome_arquivo_original)}"
                        aria-label="Baixar ${this.escapeHtml(a.nome_arquivo_original)}">
                    <i class="fas fa-download"></i>
                </button>
             </span>`
        ).join('');
        return `
            <article class="msg-thread-item">
                <div class="msg-card-head">
                    <span class="msg-categoria ${catClass}">${catClass}</span>
                    <h3 class="msg-card-title">${this.escapeHtml(m.titulo)}</h3>
                </div>
                <div class="msg-card-meta">
                    <span>${m.remetente_nome || 'Sistema'}</span>
                    <span>${this.formatDate(m.criado_em)}</span>
                    ${m.id === Number(this.threadId) ? '<span class="msg-card-replies">(mensagem principal)</span>' : ''}
                </div>
                <p class="msg-card-texto">${this.escapeHtml(m.texto)}</p>
                ${anexos ? `<div class="msg-anexos-pendentes">${anexos}</div>` : ''}
            </article>
        `;
    }

    mostrarBotaoAcao(raiz) {
        const container = document.getElementById('threadMensagens');
        const existente = container.querySelector('.msg-acao-btn');
        if (existente) existente.remove();
        if (!raiz.url_acao) return;
        const btn = document.createElement('button');
        btn.className = 'btn btn-primary btn-sm msg-acao-btn';
        btn.innerHTML = '<i class="fas fa-external-link-alt"></i> Ir para a ação';
        btn.addEventListener('click', () => {
            if (window.grindx.navegarPara) window.grindx.navegarPara(raiz.url_acao);
        });
        container.appendChild(btn);
    }

    voltarLista() {
        document.getElementById('threadView').style.display = 'none';
        document.getElementById('listaView').style.display = 'block';
        this.threadId = null;
        this.loadLista();
    }

    async toggleArquivar(mensagemId) {
        try {
            const msg = await window.grindx.api.patch(`/mensagens/${mensagemId}/arquivar`, {
                arquivar: !this.estaArquivada(mensagemId)
            });
            if (msg && window.grindx.mensagens) window.grindx.mensagens.refresh();
            this.loadLista();
        } catch (err) {
            this.toastError(err);
        }
    }

    estaArquivada(mensagemId) {
        const card = document.querySelector(`[data-abrir="${mensagemId}"]`);
        return !!(card && card.textContent.indexOf('Restaurar') !== -1);
    }

    abrirModal() {
        document.getElementById('composeModal').style.display = 'flex';
        this.composeFiles = [];
        this.renderArquivosPendentes('composeArquivos', []);
        document.getElementById('composeForm').reset();
        this.aplicarPermissaoCategoria();
    }

    fecharModal() {
        document.getElementById('composeModal').style.display = 'none';
    }

    aplicarPermissaoCategoria() {
        const me = window.grindx.session.getUserProfile();
        const select = document.getElementById('categoriaSelect');
        if (me.role !== 'admin') {
            select.innerHTML = '<option value="DIRETA">Direta</option>';
        }
    }

    async enviarMensagem() {
        const destinatario_id = Number(document.getElementById('destinatarioSelect').value);
        const titulo = document.getElementById('tituloInput').value.trim();
        const texto = document.getElementById('textoInput').value.trim();
        const categoria = document.getElementById('categoriaSelect').value;
        const url_acao = document.getElementById('urlAcaoInput').value.trim() || null;

        if (!destinatario_id || !titulo || !texto) {
            this.toastWarning('Preencha destinatário, título e texto.');
            return;
        }
        try {
            const msg = await window.grindx.api.post('/mensagens', {
                destinatario_id, titulo, texto, categoria, url_acao
            });
            await this.uploadAnexos(msg.id, this.composeFiles);
            this.fecharModal();
            this.toastSuccess('Mensagem enviada!');
            if (window.grindx.notifyMensagens) window.grindx.notifyMensagens();
            if (this.status !== 'todas') {
                this.status = 'todas';
                document.getElementById('statusFilter').value = 'todas';
            }
            await this.loadLista();
        } catch (err) {
            this.toastError(err);
        }
    }

    async enviarResposta() {
        const texto = document.getElementById('respostaTexto').value.trim();
        if (!texto) {
            this.toastWarning('Escreva a resposta.');
            return;
        }
        try {
            const resp = await window.grindx.api.post(`/mensagens/${this.threadId}/respostas`, { texto });
            await this.uploadAnexos(resp.id, this.replyFiles);
            document.getElementById('respostaTexto').value = '';
            this.replyFiles = [];
            this.renderArquivosPendentes('respostaArquivos', []);
            if (window.grindx.notifyMensagens) window.grindx.notifyMensagens();
            await this.abrirThread(this.threadId);
        } catch (err) {
            this.toastError(err);
        }
    }

    async uploadAnexos(mensagemId, files) {
        for (const file of files) {
            const form = new FormData();
            form.append('file', file);
            const url = window.grindx.api.buildApiUrl(`/mensagens/${mensagemId}/anexos`);
            const resp = await fetch(url, {
                method: 'POST',
                headers: { Authorization: `Bearer ${this.token}` },
                body: form
            });
            if (!resp.ok) throw new Error(`Falha ao anexar ${file.name}`);
        }
    }

    async downloadAnexo(mensagemId, anexoId, nome) {
        try {
            const url = window.grindx.api.buildApiUrl(`/mensagens/${mensagemId}/anexos/${anexoId}/download`);
            const resp = await fetch(url, {
                headers: { Authorization: `Bearer ${this.token}` }
            });
            if (!resp.ok) throw new Error('Falha ao baixar anexo.');
            const blob = await resp.blob();
            const objUrl = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = objUrl;
            a.download = nome;
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(objUrl);
        } catch (err) {
            this.toastError(err);
        }
    }

    renderArquivosPendentes(containerId, files) {
        const container = document.getElementById(containerId);
        container.innerHTML = files.map((f, i) =>
            `<span class="msg-anexo-chip"><i class="fas fa-paperclip"></i> ${this.escapeHtml(f.name)}
                <button type="button" data-remove-pendente="${i}" aria-label="Remover anexo">&times;</button>
             </span>`
        ).join('') || '';
        container.querySelectorAll('[data-remove-pendente]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const idx = Number(btn.dataset.removePendente);
                if (containerId === 'composeArquivos') {
                    this.composeFiles.splice(idx, 1);
                } else {
                    this.replyFiles.splice(idx, 1);
                }
                this.renderArquivosPendentes(containerId, containerId === 'composeArquivos' ? this.composeFiles : this.replyFiles);
            });
        });
    }

    formatDate(value) {
        if (!value) return '—';
        const date = new Date(value);
        return isNaN(date.getTime()) ? '—' : date.toLocaleString('pt-BR');
    }

    escapeHtml(value) {
        return String(value == null ? '' : value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.mensagensController = new MensagensController();
});
```

- [ ] **Step 4: Syntax check**

Run (workdir `apps/frontend-webapp`):
```bash
node --check modules/mensagens/script.js
```
Expected: no output (OK)

- [ ] **Step 5: Commit**

```bash
git add modules/mensagens/index.html modules/mensagens/style.css modules/mensagens/script.js
git commit -m "feat(frontend): add mensagens module (list, threads, compose, attachments)"
```

---

## Task 10: Registrar módulo no seed

**Files:**
- Modify: `apps/api-postgres/seed.py` (add entry to `modulos_seed`)

- [ ] **Step 1: Add the module entry**

In `apps/api-postgres/seed.py`, inside `modulos_seed`, add (e.g., after the `home` entry):

```python
            {
                "aba": "Principal",
                "nome": "Mensagens",
                "slug": "mensagens",
                "url": "modules/mensagens/index.html",
                "icone": "fas fa-envelope",
            },
```

- [ ] **Step 2: Verify seed module imports and the dict schema**

Run (workdir `apps/api-postgres`):
```bash
python -c "import ast; ast.parse(open('seed.py', encoding='utf-8').read()); print('seed.py OK')"
```
Expected: `seed.py OK`

- [ ] **Step 3: Commit**

```bash
git add seed.py
git commit -m "feat(mensagens): register mensagens module in seed"
```

---

## Task 11: Docs sync

**Files:**
- Modify: `README.md`
- Modify: `docs/API.md`
- Modify: `docs/DATABASE.md`

- [ ] **Step 1: Update `docs/API.md`**

Add a section for the mensagens endpoints:

```markdown
## Mensagens Internas (`/v1/mensagens`)

| Método | Rota | Descrição |
|---|---|---|
| GET | `/v1/mensagens` | Lista mensagens raiz do destinatário (`status`, `ordem`, paginação) |
| GET | `/v1/mensagens/nao-lidas/count` | Contador de não lidas do usuário |
| POST | `/v1/mensagens` | Cria mensagem raiz (`SISTEMA`/`AVISO` exigem admin) |
| GET | `/v1/mensagens/{id}/thread` | Raiz + respostas da thread |
| POST | `/v1/mensagens/{id}/respostas` | Responde à thread (participantes) |
| PATCH | `/v1/mensagens/{id}/lida` | Marca mensagem como lida (destinatário) |
| PATCH | `/v1/mensagens/{id}/thread/lida` | Marca thread como lida (participantes) |
| PATCH | `/v1/mensagens/{id}/arquivar` | Arquiva/restaura thread (destinatário da raiz) |
| POST | `/v1/mensagens/{id}/anexos` | Anexa arquivo (remetente; max 10MB; allowlist) |
| GET | `/v1/mensagens/{id}/anexos` | Lista anexos (participantes) |
| GET | `/v1/mensagens/{id}/anexos/{anexo_id}/download` | Baixa anexo autenticado (participantes) |
```

- [ ] **Step 2: Update `docs/DATABASE.md`**

Document the new tables in schema `org`:

```markdown
### `org.mensagens`
- `id` BIGSERIAL PK; `resposta_a_id` FK autorreferente (CASCADE, thread); `remetente_id` FK `iam.usuarios.id` (SET NULL; NULL=sistema); `destinatario_id` FK (CASCADE); `titulo` VARCHAR(150); `texto` TEXT; `categoria` VARCHAR(20) CHECK SISTEMA/DIRETA/AVISO; `url_acao` VARCHAR(255); `lida_em`; `arquivada_em`; `criado_em`.
- Índices: `ix_mensagens_destinatario_id (destinatario_id, criado_em DESC)`; parcial `ix_mensagens_nao_lidas WHERE lida_em IS NULL`; `ix_mensagens_resposta_a`.

### `org.anexos_mensagem`
- `id`; `mensagem_id` FK `org.mensagens.id` (CASCADE); `nome_arquivo_original` VARCHAR(255); `caminho` VARCHAR(255) (relativo a `uploads/`); `content_type` VARCHAR(100); `tamanho_bytes` INTEGER; `criado_em`.
```

- [ ] **Step 3: Update `README.md`**

In the modules list / architecture section, add: "**Mensagens** (`modules/mensagens/`) — mensagens internas com threads, anexos e badge de não lidas no mascote; backend `app/mensagens/` (`/v1/mensagens`)."

- [ ] **Step 4: Commit**

```bash
git add README.md docs/API.md docs/DATABASE.md
git commit -m "docs: document mensagens endpoints and tables"
```

---

## Task 12: Pre-push verification

**Files:** none (commands only)

- [ ] **Step 1: Run backend tests**

Run (workdir `apps/api-postgres`):
```bash
python -m pytest tests/unit/test_mensagens_models.py tests/unit/test_mensagens_service.py tests/integration/test_mensagens_api.py -v
```
Expected: all PASS.

- [ ] **Step 2: Run frontend tests**

Run (workdir `apps/frontend-webapp`):
```bash
node --test tests/notificationBridge.test.js tests/mensagensWidget.test.js
```
Expected: all PASS.

- [ ] **Step 3: Run full monorepo test suite + format + lint**

From repo root:
```bash
make test-all
make format
make lint
```
Expected: tests pass; `ruff format` and `ruff check` clean.

---

## Self-Review Notes

- Spec coverage: DB (Task 1), models/schemas (2, 3), service rules incl. threads/archive/count (4), router + auth + anexos (5), bridge (6), mascot badge/balloon (7), dropdown + listener (8), module (9), seed (10), docs (11), verification (12).
- Type consistency: `MensagemResponse` fields match service dicts (both use `quantidade_respostas`, `ultima_resposta_em`, `anexos_count`, `anexos`); `CountResponse.count` used by count and `thread/lida` endpoints; `MensagensWidget` uses `refresh`/`markSeen`/`openRecados`/`count`.
- Placeholder scan: all code blocks complete; no TBD/TODO.
