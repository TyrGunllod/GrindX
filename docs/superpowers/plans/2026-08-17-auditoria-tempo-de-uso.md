# Auditoria de Alterações e Tempo de Uso Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Registrar toda escrita em banco (INSERT/UPDATE/DELETE) na api-postgres com usuário, ação, entidade e campos alterados; rastrear login/logout em tabela de sessões; expor módulo frontend "Auditoria" (admin) e fechar sessão no servidor no logout manual e por inatividade.

**Architecture:** Auditoria automática via listeners SQLAlchemy `before_flush` (captura diff + adiciona `AuditLog` na mesma transação). Contexto da requisição (`user_id`, `ip`) via `ContextVar` preenchida por `BaseHTTPMiddleware`. Sessões abertas/fechadas explicitamente por `AuditService` nos endpoints de auth. Visualização via `GET /v1/audit/logs` e `GET /v1/audit/sessoes` (admin) + módulo frontend.

**Tech Stack:** FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2, Starlette `BaseHTTPMiddleware`, `contextvars`, vanilla JS (node:test).

---

### Task 1: Models + Migração Alembic + Registro de Models

**Files:**
- Create: `apps/api-postgres/app/audit/models.py`
- Create: `apps/api-postgres/alembic/versions/022_add_audit_tables.py` (revision `f49af6b8a8d4`, down_revision `8ec10f792d4b`)
- Modify: `apps/api-postgres/app/models/__init__.py`
- Modify: `apps/api-postgres/alembic/env.py`
- Test: `apps/api-postgres/tests/unit/test_models_audit.py`

- [ ] **Step 1: Write the failing test**

Create `apps/api-postgres/tests/unit/test_models_audit.py`:

```python
"""Testes unitários para os modelos de auditoria."""
from sqlalchemy.orm import Session

from app.audit.models import AuditLog, Sessao


def test_create_audit_log(db_session: Session):
    log = AuditLog(
        user_id=1, entidade="Usuario", entidade_id=3,
        acao="update", campos_alterados=["email", "role"], ip="127.0.0.1",
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)
    assert log.id is not None
    assert log.campos_alterados == ["email", "role"]
    assert log.criado_em is not None


def test_create_sessao(db_session: Session):
    sessao = Sessao(user_id=1, ip="127.0.0.1")
    db_session.add(sessao)
    db_session.commit()
    db_session.refresh(sessao)
    assert sessao.id is not None
    assert sessao.login_at is not None
    assert sessao.logout_at is None
```

- [ ] **Step 2: Run test to verify it fails**
Run: `cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .venv\Scripts\python -m pytest tests/unit/test_models_audit.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'app.audit.models'`

- [ ] **Step 3: Write minimal implementation**

`apps/api-postgres/app/audit/models.py`:

```python
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.org.base import OrgBase


class AuditLog(OrgBase):
    __tablename__ = "audit_logs"

    __table_args__ = (
        Index("ix_audit_logs_entidade_id", "entidade", "entidade_id"),
        {"schema": "org"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("iam.usuarios.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    entidade: Mapped[str] = mapped_column(String(100), nullable=False)
    entidade_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    acao: Mapped[str] = mapped_column(String(20), nullable=False)
    campos_alterados: Mapped[list] = mapped_column(JSON, nullable=False)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, entidade='{self.entidade}', acao='{self.acao}')>"


class Sessao(OrgBase):
    __tablename__ = "sessoes"

    __table_args__ = ({"schema": "org"},)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("iam.usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    login_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    logout_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duracao_segundos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    logout_motivo: Mapped[str | None] = mapped_column(String(20), nullable=True)

    def __repr__(self) -> str:
        return f"<Sessao(id={self.id}, user_id={self.user_id}, login_at='{self.login_at}')>"
```

Create `apps/api-postgres/alembic/versions/022_add_audit_tables.py`:

```python
"""add audit_logs and sessoes tables

Revision ID: f49af6b8a8d4
Revises: 8ec10f792d4b
Create Date: 2026-08-17 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "f49af6b8a8d4"
down_revision: Union[str, None] = "8ec10f792d4b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("iam.usuarios.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("entidade", sa.String(100), nullable=False),
        sa.Column("entidade_id", sa.Integer(), nullable=True),
        sa.Column("acao", sa.String(20), nullable=False),
        sa.Column("campos_alterados", sa.JSON(), nullable=False),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Index("ix_audit_logs_entidade_id", "entidade", "entidade_id"),
        sa.Index("ix_audit_logs_user_id", "user_id"),
        sa.Index("ix_audit_logs_criado_em", "criado_em"),
        schema="org",
    )
    op.create_table(
        "sessoes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("iam.usuarios.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "login_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("logout_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duracao_segundos", sa.Integer(), nullable=True),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column("logout_motivo", sa.String(20), nullable=True),
        sa.Index("ix_sessoes_user_id", "user_id"),
        sa.Index("ix_sessoes_login_at", "login_at"),
        schema="org",
    )


def downgrade() -> None:
    op.drop_table("sessoes", schema="org")
    op.drop_table("audit_logs", schema="org")
```

- [ ] **Step 4: Register models + run test + verify migration**

Modify `apps/api-postgres/app/models/__init__.py` — add after the existing imports:

```python
from app.audit.models import AuditLog, Sessao  # noqa: F401
```

Modify `apps/api-postgres/alembic/env.py` — add after the existing model imports:

```python
from app.audit.models import AuditLog, Sessao  # noqa: F401
```

Run: `cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .venv\Scripts\python -m pytest tests/unit/test_models_audit.py -v`
Expected: PASS (2 tests). Os models ficam registrados no `IamBase.metadata` compartilhado (via `OrgBase`), então `alembic autogenerate` e `create_all` dos testes os incluem automaticamente.

- [ ] **Step 5: Commit**

```bash
git add apps/api-postgres/app/audit/models.py apps/api-postgres/alembic/versions/022_add_audit_tables.py apps/api-postgres/app/models/__init__.py apps/api-postgres/alembic/env.py apps/api-postgres/tests/unit/test_models_audit.py
git commit -m "feat(audit): add AuditLog and Sessao models with migration 022"
```

---

### Task 2: Contexto de Requisição (ContextVar + Middleware)

**Files:**
- Create: `apps/api-postgres/app/audit/context.py`
- Create: `apps/api-postgres/app/middleware/audit_context.py`
- Modify: `apps/api-postgres/app/main.py` (add_middleware AuditContextMiddleware)
- Test: `apps/api-postgres/tests/unit/test_audit_context.py`

- [ ] **Step 1: Write the failing test**

`apps/api-postgres/tests/unit/test_audit_context.py`:

```python
"""Testes unitários para o contexto de auditoria da requisição."""
from fastapi.testclient import TestClient

from app.audit.context import audit_ip, audit_user_id


def test_context_defaults_are_none():
    assert audit_user_id.get() is None
    assert audit_ip.get() is None


def test_context_cleared_after_request(client: TestClient):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert audit_user_id.get() is None
    assert audit_ip.get() is None
```

- [ ] **Step 2: Run test to verify it fails**
Run: `cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .venv\Scripts\python -m pytest tests/unit/test_audit_context.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.audit.context'`

- [ ] **Step 3: Write minimal implementation**

`apps/api-postgres/app/audit/context.py`:

```python
"""Contexto de auditoria da requisição atual (ContextVar)."""

from contextvars import ContextVar

audit_user_id: ContextVar[int | None] = ContextVar("audit_user_id", default=None)
audit_ip: ContextVar[str | None] = ContextVar("audit_ip", default=None)
```

`apps/api-postgres/app/middleware/audit_context.py`:

```python
"""Middleware que preenche o contexto de auditoria a partir do JWT (opcional)."""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.audit.context import audit_ip, audit_user_id


class AuditContextMiddleware(BaseHTTPMiddleware):
    """Extrai user_id do token (se houver) e IP e popula as ContextVar.

    Nunca lança por ausência de token — login/refresh são públicos.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        user_id: int | None = None
        ip: str | None = request.client.host if request.client else None

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from app.core.config import settings
                from shared.security.jwt import verificar_jwt

                payload = verificar_jwt(auth_header[7:], settings.SECRET_KEY)
                user_id = int(payload.sub)
            except Exception:
                user_id = None

        audit_user_id.set(user_id)
        audit_ip.set(ip)
        try:
            return await call_next(request)
        finally:
            audit_user_id.set(None)
            audit_ip.set(None)
```

Registrar no `main.py` (ao lado dos demais middlewares, após `RequestIdMiddleware`):

```python
from app.middleware.audit_context import AuditContextMiddleware

...
app.add_middleware(AuditContextMiddleware)
```

- [ ] **Step 4: Run test + full suite to verify passes**
Run: `cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .venv\Scripts\python -m pytest tests/unit/test_audit_context.py -v`
Expected: PASS. Depois rodar `make test-postgres` (regressão — middleware não deve quebrar rotas existentes).

- [ ] **Step 5: Commit**

```bash
git add apps/api-postgres/app/audit/context.py apps/api-postgres/app/middleware/audit_context.py apps/api-postgres/app/main.py apps/api-postgres/tests/unit/test_audit_context.py
git commit -m "feat(audit): add request audit context middleware (ContextVar)"
```

---

### Task 3: AuditService

**Files:**
- Create: `apps/api-postgres/app/audit/service.py`
- Test: `apps/api-postgres/tests/unit/test_audit_service.py`

- [ ] **Step 1: Write the failing test**

`apps/api-postgres/tests/unit/test_audit_service.py`:

```python
"""Testes unitários para o AuditService."""
import time

from sqlalchemy.orm import Session

from app.audit.service import AuditService
from app.models.usuario import Usuario
from shared.security.jwt import gerar_hash_senha


def _mkuser(db: Session) -> Usuario:
    u = Usuario(
        username="aud", email="aud@x.com", nome_completo="Aud",
        senha_hash=gerar_hash_senha("x"),
    )
    db.add(u)
    db.commit()
    return u


def test_registrar_audit(db_session: Session):
    svc = AuditService(db_session)
    log = svc.registrar_audit(
        user_id=1, entidade="Usuario", entidade_id=2, acao="update",
        campos_alterados=["email"], ip="10.0.0.1",
    )
    db_session.commit()
    db_session.refresh(log)
    assert log.id is not None


def test_abrir_e_fechar_sessao_calcula_duracao(db_session: Session):
    user = _mkuser(db_session)
    svc = AuditService(db_session)
    sessao = svc.abrir_sessao(user.id, ip="127.0.0.1")
    assert sessao.login_at is not None
    time.sleep(1.1)
    fechada = svc.fechar_sessao(user.id, motivo="logout")
    assert fechada.id == sessao.id
    assert fechada.logout_at is not None
    assert fechada.logout_motivo == "logout"
    assert fechada.duracao_segundos is not None and fechada.duracao_segundos >= 1


def test_fechar_sessao_sem_aberta_retorna_none(db_session: Session):
    user = _mkuser(db_session)
    assert AuditService(db_session).fechar_sessao(user.id) is None


def test_fechar_fecha_mais_recente(db_session: Session):
    user = _mkuser(db_session)
    svc = AuditService(db_session)
    s1 = svc.abrir_sessao(user.id)
    time.sleep(0.3)
    s2 = svc.abrir_sessao(user.id)
    fechada = svc.fechar_sessao(user.id)
    assert fechada.id == s2.id
    assert svc.fechar_sessao(user.id).id == s1.id
```

- [ ] **Step 2: Run test to verify it fails**
Run: `cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .venv\Scripts\python -m pytest tests/unit/test_audit_service.py -v`
Expected: FAIL — `ImportError: cannot import name 'AuditService'`

- [ ] **Step 3: Write minimal implementation**

`apps/api-postgres/app/audit/service.py`:

```python
"""Serviço de auditoria e sessões de tempo de uso."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.audit.models import AuditLog, Sessao


class AuditService:
    """Registra audit logs e gerencia sessões (login/logout)."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def registrar_audit(
        self,
        *,
        user_id: int | None,
        entidade: str,
        entidade_id: int | None,
        acao: str,
        campos_alterados: list[str],
        ip: str | None,
    ) -> AuditLog:
        log = AuditLog(
            user_id=user_id,
            entidade=entidade,
            entidade_id=entidade_id,
            acao=acao,
            campos_alterados=campos_alterados,
            ip=ip,
        )
        self.db.add(log)
        return log

    def abrir_sessao(self, user_id: int, ip: str | None = None) -> Sessao:
        sessao = Sessao(user_id=user_id, ip=ip)
        self.db.add(sessao)
        self.db.commit()
        self.db.refresh(sessao)
        return sessao

    def fechar_sessao(self, user_id: int, motivo: str = "logout") -> Sessao | None:
        sessao = self.db.scalar(
            select(Sessao)
            .where(Sessao.user_id == user_id, Sessao.logout_at.is_(None))
            .order_by(Sessao.login_at.desc())
            .limit(1)
        )
        if sessao is None:
            return None
        agora = datetime.now(timezone.utc)
        login_at = sessao.login_at
        if login_at.tzinfo is None:
            login_at = login_at.replace(tzinfo=timezone.utc)
        sessao.logout_at = agora
        sessao.logout_motivo = motivo
        sessao.duracao_segundos = int((agora - login_at).total_seconds())
        self.db.commit()
        self.db.refresh(sessao)
        return sessao

    def listar_logs(
        self,
        page: int,
        page_size: int,
        user_id: int | None = None,
        entidade: str | None = None,
        acao: str | None = None,
        data_inicio: datetime | None = None,
        data_fim: datetime | None = None,
    ) -> tuple[list[AuditLog], int]:
        conds = []
        if user_id:
            conds.append(AuditLog.user_id == user_id)
        if entidade:
            conds.append(AuditLog.entidade == entidade)
        if acao:
            conds.append(AuditLog.acao == acao)
        if data_inicio:
            conds.append(AuditLog.criado_em >= data_inicio)
        if data_fim:
            conds.append(AuditLog.criado_em <= data_fim)

        total = self.db.scalar(select(func.count()).select_from(AuditLog).where(*conds)) or 0
        items = list(
            self.db.scalars(
                select(AuditLog)
                .where(*conds)
                .order_by(AuditLog.criado_em.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return items, total

    def listar_sessoes(
        self,
        page: int,
        page_size: int,
        user_id: int | None = None,
        data_inicio: datetime | None = None,
        data_fim: datetime | None = None,
    ) -> tuple[list[Sessao], int]:
        conds = []
        if user_id:
            conds.append(Sessao.user_id == user_id)
        if data_inicio:
            conds.append(Sessao.login_at >= data_inicio)
        if data_fim:
            conds.append(Sessao.login_at <= data_fim)

        total = self.db.scalar(select(func.count()).select_from(Sessao).where(*conds)) or 0
        items = list(
            self.db.scalars(
                select(Sessao)
                .where(*conds)
                .order_by(Sessao.login_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return items, total
```

- [ ] **Step 4: Run test to verify it passes**
Run: `cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .venv\Scripts\python -m pytest tests/unit/test_audit_service.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add apps/api-postgres/app/audit/service.py apps/api-postgres/tests/unit/test_audit_service.py
git commit -m "feat(audit): add AuditService (logs e sessões)"
```

---

### Task 4: Listeners SQLAlchemy (auditoria automática)

> **Decisão de implementação (desvio técnico da spec §3.2):** a captura do diff E a adição do `AuditLog` acontecem em `before_flush`. Adicionar em `after_flush` adiaria a escrita para o próximo flush/commit (SQLAlchemy não re-flush dentro de `after_flush`), quebrando o requisito "mesma transação". A captura no `before_flush` é obrigatória porque o `after_flush` zera `attr.history`.

**Files:**
- Create: `apps/api-postgres/app/audit/listeners.py`
- Modify: `apps/api-postgres/app/main.py` (import side-effect para registrar listeners)
- Test: `apps/api-postgres/tests/unit/test_audit_listeners.py`

- [ ] **Step 1: Write the failing test**

`apps/api-postgres/tests/unit/test_audit_listeners.py`:

```python
"""Testes unitários para os listeners de auditoria automática."""
from sqlalchemy.orm import Session

from app.audit.context import audit_ip, audit_user_id
from app.audit.models import AuditLog, Sessao
from app.modules.org.models.theme_history import ThemeHistory
from app.models.usuario import Usuario
from shared.security.jwt import gerar_hash_senha


def _mkuser(db: Session, username: str = "lis") -> Usuario:
    u = Usuario(
        username=username, email=f"{username}@x.com", nome_completo="L",
        senha_hash=gerar_hash_senha("x"),
    )
    db.add(u)
    db.commit()
    return u


def test_insert_gera_log_com_contexto(db_session: Session):
    audit_user_id.set(7)
    audit_ip.set("10.1.1.1")
    _mkuser(db_session, "ins")
    audit_user_id.set(None)
    audit_ip.set(None)

    logs = db_session.query(AuditLog).filter(AuditLog.entidade == "Usuario").all()
    assert len(logs) == 1
    log = logs[0]
    assert log.acao == "insert"
    assert log.user_id == 7
    assert log.ip == "10.1.1.1"
    assert "senha_hash" in log.campos_alterados
    assert "criado_em" not in log.campos_alterados


def test_update_gera_apenas_campos_alterados(db_session: Session):
    user = _mkuser(db_session, "upd")
    audit_user_id.set(9)
    user.nome_completo = "Novo Nome"
    user.role = "admin"
    db_session.commit()
    audit_user_id.set(None)

    logs = db_session.query(AuditLog).filter(
        AuditLog.entidade == "Usuario", AuditLog.acao == "update"
    ).all()
    assert len(logs) == 1
    assert set(logs[0].campos_alterados) == {"nome_completo", "role"}


def test_delete_gera_log(db_session: Session):
    user = _mkuser(db_session, "del")
    db_session.delete(user)
    db_session.commit()

    logs = db_session.query(AuditLog).filter(
        AuditLog.entidade == "Usuario", AuditLog.acao == "delete"
    ).all()
    assert len(logs) == 1
    assert logs[0].entidade_id == user.id


def test_exclui_entidades_de_auditoria(db_session: Session):
    user = _mkuser(db_session, "exc")
    db_session.add(Sessao(user_id=user.id))
    db_session.add(
        ThemeHistory(theme_id=1, company_id=1, action="created", theme_snapshot={})
    )
    db_session.commit()

    assert db_session.query(AuditLog).filter(AuditLog.entidade == "Sessao").count() == 0
    assert db_session.query(AuditLog).filter(AuditLog.entidade == "AuditLog").count() == 0
    assert db_session.query(AuditLog).filter(AuditLog.entidade == "ThemeHistory").count() == 0
```

- [ ] **Step 2: Run test to verify it fails**
Run: `cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .venv\Scripts\python -m pytest tests/unit/test_audit_listeners.py -v`
Expected: FAIL — os asserts de `AuditLog` recebem lista vazia.

- [ ] **Step 3: Write minimal implementation**

`apps/api-postgres/app/audit/listeners.py`:

```python
"""Auditoria automática de escritas via listeners SQLAlchemy.

Captura e persiste AuditLog na MESMA transação (before_flush):
- diff lido aqui está íntegro (after_flush zera attr.history)
- AuditLog adicionados em before_flush são incluídos no próprio flush
"""

from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

from app.audit.context import audit_ip, audit_user_id
from app.audit.models import AuditLog, Sessao
from app.modules.org.models.theme_history import ThemeHistory

# Classes cujas escritas NÃO geram audit log (histórico próprio / auto-gerados)
_EXCLUIDAS = {"AuditLog", "Sessao", "ThemeHistory"}
_IGNORAR_CAMPOS = {"criado_em", "atualizado_em"}


def _is_auditable(obj) -> bool:
    cls = type(obj)
    if cls.__name__ in _EXCLUIDAS:
        return False
    table = getattr(cls, "__table__", None)
    return table is not None and len(table.primary_key.columns) > 0


def _column_names(obj) -> list[str]:
    return [c.key for c in obj.__table__.columns if c.key not in _IGNORAR_CAMPOS]


def _entidade_id(obj) -> int | None:
    pk = [c for c in obj.__table__.primary_key.columns]
    if not pk:
        return None
    val = getattr(obj, pk[0].key, None)
    if val is None:
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


@event.listens_for(Session, "before_flush")
def _captura_e_persiste_audit(session, flush_context, instances) -> None:
    ctx_user = audit_user_id.get()
    ctx_ip = audit_ip.get()

    for obj in session.new:
        if _is_auditable(obj):
            session.add(
                AuditLog(
                    user_id=ctx_user, entidade=type(obj).__name__,
                    entidade_id=_entidade_id(obj), acao="insert",
                    campos_alterados=_column_names(obj), ip=ctx_ip,
                )
            )
    for obj in session.dirty:
        if _is_auditable(obj):
            state = inspect(obj)
            campos = [
                a.key
                for a in state.attrs
                if a.key not in _IGNORAR_CAMPOS and a.history.has_changes()
            ]
            if campos:
                session.add(
                    AuditLog(
                        user_id=ctx_user, entidade=type(obj).__name__,
                        entidade_id=_entidade_id(obj), acao="update",
                        campos_alterados=campos, ip=ctx_ip,
                    )
                )
    for obj in session.deleted:
        if _is_auditable(obj):
            session.add(
                AuditLog(
                    user_id=ctx_user, entidade=type(obj).__name__,
                    entidade_id=_entidade_id(obj), acao="delete",
                    campos_alterados=_column_names(obj), ip=ctx_ip,
                )
            )
```

Registrar os listeners no `main.py` (import for side-effect) — adicionar após imports de routers:

```python
import app.audit.listeners  # noqa: F401  (registra before_flush)
```

- [ ] **Step 4: Run test to verify it passes**
Run: `cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .venv\Scripts\python -m pytest tests/unit/test_audit_listeners.py -v`
Expected: PASS. Depois `make test-postgres` (regressão — listener não pode quebrar seed/tests existentes; `ThemeHistory` e `Sessao` excluídos evitam duplicação).

- [ ] **Step 5: Commit**

```bash
git add apps/api-postgres/app/audit/listeners.py apps/api-postgres/app/main.py apps/api-postgres/tests/unit/test_audit_listeners.py
git commit -m "feat(audit): automatic before_flush auditing (same transaction)"
```

---

### Task 5: Schemas + Endpoints `/v1/audit/*` + Logout no Auth

**Files:**
- Create: `apps/api-postgres/app/schemas/audit.py`
- Create: `apps/api-postgres/app/routers/audit_router.py`
- Modify: `apps/api-postgres/app/auth/router.py` (login abre sessão; `POST /v1/auth/logout`)
- Modify: `apps/api-postgres/app/main.py` (include_router audit_router)
- Modify: `apps/api-postgres/tests/conftest.py` (import models de auditoria)
- Modify: `apps/api-postgres/tests/integration/test_indexes.py` (asserts de índices)
- Test: `apps/api-postgres/tests/integration/test_audit_integracao.py`

- [ ] **Step 1: Write the failing test**

Adicionar aos imports de `apps/api-postgres/tests/conftest.py` (após `from app.main import app`):

```python
from app.audit.models import AuditLog, Sessao  # noqa: F401
```

`apps/api-postgres/tests/integration/test_audit_integracao.py`:

```python
"""Testes de integração dos endpoints de auditoria e logout."""
import time

import pytest
from fastapi.testclient import TestClient
from shared.security.jwt import gerar_hash_senha
from sqlalchemy.orm import Session

from app.audit.models import Sessao
from app.models.empresa import Empresa
from app.models.usuario import Usuario


@pytest.fixture
def empresa(db_session: Session) -> Empresa:
    emp = Empresa(nome="Aud Corp", dominio="aud.com")
    db_session.add(emp)
    db_session.commit()
    return emp


@pytest.fixture
def admin_user(db_session: Session, empresa: Empresa) -> Usuario:
    u = Usuario(
        username="audadmin", email="audadmin@x.com", nome_completo="Aud Admin",
        senha_hash=gerar_hash_senha("senha123"), role="admin", empresa_id=empresa.id,
    )
    db_session.add(u)
    db_session.commit()
    return u


@pytest.fixture
def op_user(db_session: Session, empresa: Empresa) -> Usuario:
    u = Usuario(
        username="audop", email="audop@x.com", nome_completo="Aud Op",
        senha_hash=gerar_hash_senha("senha123"), role="operador", empresa_id=empresa.id,
    )
    db_session.add(u)
    db_session.commit()
    return u


def _login(client: TestClient, username: str) -> dict:
    r = client.post("/v1/auth/token", json={"username": username, "password": "senha123"})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_login_cria_sessao(client: TestClient, admin_user: Usuario, db_session: Session):
    _login(client, "audadmin")
    sessoes = db_session.query(Sessao).filter(Sessao.user_id == admin_user.id).all()
    assert len(sessoes) == 1
    assert sessoes[0].logout_at is None


def test_logout_fecha_sessao(client: TestClient, admin_user: Usuario, db_session: Session):
    headers = _login(client, "audadmin")
    r = client.post("/v1/auth/logout", json={"motivo": "logout"}, headers=headers)
    assert r.status_code == 200
    sessao = db_session.query(Sessao).filter(Sessao.user_id == admin_user.id).first()
    assert sessao.logout_at is not None
    assert sessao.logout_motivo == "logout"
    assert sessao.duracao_segundos is not None


def test_logout_motivo_invalido(client: TestClient, admin_user: Usuario):
    headers = _login(client, "audadmin")
    r = client.post("/v1/auth/logout", json={"motivo": "outro"}, headers=headers)
    assert r.status_code == 400


def test_logout_requer_auth(client: TestClient):
    r = client.post("/v1/auth/logout", json={"motivo": "logout"})
    assert r.status_code == 401


def test_escrita_gera_log_com_user(
    client: TestClient, admin_user: Usuario, db_session: Session, empresa: Empresa
):
    from app.audit.models import AuditLog

    headers = _login(client, "audadmin")
    client.post(
        "/v1/themes",
        json={"name": "Logged", "icon_library": "fontawesome"},
        headers=headers,
    )
    logs = db_session.query(AuditLog).filter(AuditLog.entidade == "CompanyTheme").all()
    assert len(logs) == 1
    assert logs[0].acao == "insert"
    assert logs[0].user_id == admin_user.id


def test_audit_logs_endpoint_rbac(
    client: TestClient, admin_user: Usuario, op_user: Usuario, db_session: Session
):
    admin_h = _login(client, "audadmin")
    op_h = _login(client, "audop")

    assert client.get("/v1/audit/logs", headers=admin_h).status_code == 200
    assert client.get("/v1/audit/logs", headers=op_h).status_code == 403
    assert client.get("/v1/audit/logs").status_code == 401
    assert client.get("/v1/audit/sessoes", headers=admin_h).status_code == 200


def test_audit_logs_filtros_e_paginacao(
    client: TestClient, admin_user: Usuario, db_session: Session, empresa: Empresa
):
    headers = _login(client, "audadmin")
    for i in range(3):
        client.post(
            "/v1/themes",
            json={"name": f"F{i}", "icon_library": "fontawesome"},
            headers=headers,
        )

    resp = client.get(
        "/v1/audit/logs",
        params={"entidade": "CompanyTheme", "page_size": 2},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["total_pages"] == 2


def test_audit_sessoes_filtros(client: TestClient, admin_user: Usuario, db_session: Session):
    _login(client, "audadmin")
    resp = client.get(
        "/v1/audit/sessoes",
        params={"user_id": admin_user.id},
        headers=_login(client, "audadmin"),
    )
    assert resp.status_code == 200
    assert resp.json()["total"] >= 2
```

- [ ] **Step 2: Run test to verify it fails**
Run: `cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .venv\Scripts\python -m pytest tests/integration/test_audit_integracao.py -v`
Expected: FAIL — rotas `/v1/audit/*` 404 e `/v1/auth/logout` 404/405.

- [ ] **Step 3: Write minimal implementation**

`apps/api-postgres/app/schemas/audit.py`:

```python
"""Schemas de resposta para auditoria e sessões."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    entidade: str
    entidade_id: int | None
    acao: str
    campos_alterados: list[str]
    ip: str | None
    criado_em: datetime


class SessaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    login_at: datetime
    logout_at: datetime | None
    duracao_segundos: int | None
    ip: str | None
    logout_motivo: str | None
```

`apps/api-postgres/app/routers/audit_router.py`:

```python
"""Endpoints de auditoria (somente admin)."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from shared.schemas.auth import TokenPayload
from shared.schemas.base import PaginatedResponse
from sqlalchemy.orm import Session

from app.audit.service import AuditService
from app.auth.dependencies import require_role_or_higher
from app.database import get_db
from app.schemas.audit import AuditLogResponse, SessaoResponse

router = APIRouter(prefix="/v1/audit", tags=["Auditoria"])


@router.get("/logs", response_model=PaginatedResponse[AuditLogResponse])
def listar_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    entidade: Optional[str] = Query(None),
    acao: Optional[str] = Query(None),
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _: TokenPayload = Depends(require_role_or_higher("admin")),
):
    service = AuditService(db)
    items, total = service.listar_logs(
        page, page_size, user_id=user_id, entidade=entidade,
        acao=acao, data_inicio=data_inicio, data_fim=data_fim,
    )
    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/sessoes", response_model=PaginatedResponse[SessaoResponse])
def listar_sessoes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _: TokenPayload = Depends(require_role_or_higher("admin")),
):
    service = AuditService(db)
    items, total = service.listar_sessoes(
        page, page_size, user_id=user_id, data_inicio=data_inicio, data_fim=data_fim,
    )
    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )
```

`apps/api-postgres/app/main.py` — add import e router:

```python
from app.routers.audit_router import router as audit_router

...
app.include_router(audit_router)
```

Modify `apps/api-postgres/app/auth/router.py`:

Imports novos (topo do arquivo):

```python
from pydantic import BaseModel

from app.audit.service import AuditService
from app.core.config import settings
from shared.security.jwt import verificar_jwt
```

Login — adicionar `db: Session = Depends(get_db)` ao parâmetro e, logo após `result = auth_service.autenticar(...)`:

```python
        result = auth_service.autenticar(dados.username, dados.password)
        payload = verificar_jwt(result.access_token, settings.SECRET_KEY)
        AuditService(db).abrir_sessao(int(payload.sub), client_ip)
```

Novo endpoint (antes de `forgot_password`):

```python
class LogoutRequest(BaseModel):
    motivo: str = "logout"


@router.post(
    "/logout",
    summary="Encerrar sessão atual",
    description="Fecha a sessão aberta mais recente do usuário autenticado.",
)
def logout(
    dados: LogoutRequest,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if dados.motivo not in {"logout", "inativo", "expirado"}:
        raise HTTPException(status_code=400, detail="Motivo de logout inválido.")
    AuditService(db).fechar_sessao(int(current_user.sub), motivo=dados.motivo)
    return {"message": "Logout realizado com sucesso."}
```

- [ ] **Step 4: Run tests to verify they pass**
Run: `cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .venv\Scripts\python -m pytest tests/integration/test_audit_integracao.py tests/integration/test_autenticacao_integrada.py -v`
Expected: PASS (novos + regressão de auth). Depois `make test-postgres`.

- [ ] **Step 5: Add index assertions to test_indexes.py**

Modify `apps/api-postgres/tests/integration/test_indexes.py` — add import e função:

```python
from app.audit.models import AuditLog, Sessao


@pytest.mark.integration
def test_audit_indexes_exist_on_models(db_session):
    audit_indexes = {idx.name for idx in AuditLog.__table__.indexes}
    sessao_indexes = {idx.name for idx in Sessao.__table__.indexes}
    assert "ix_audit_logs_entidade_id" in audit_indexes
    assert "ix_audit_logs_user_id" in audit_indexes
    assert "ix_audit_logs_criado_em" in audit_indexes
    assert "ix_sessoes_user_id" in sessao_indexes
    assert "ix_sessoes_login_at" in sessao_indexes
```

Run: `cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .venv\Scripts\python -m pytest tests/integration/test_indexes.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add apps/api-postgres/app/schemas/audit.py apps/api-postgres/app/routers/audit_router.py apps/api-postgres/app/auth/router.py apps/api-postgres/app/main.py apps/api-postgres/tests/conftest.py apps/api-postgres/tests/integration/test_audit_integracao.py apps/api-postgres/tests/integration/test_indexes.py
git commit -m "feat(audit): add /v1/audit endpoints (admin), server-side logout, session on login"
```

---

### Task 6: Frontend — Logout server-side (manual e inatividade)

**Files:**
- Create: `apps/frontend-webapp/shared/serverLogout.js`
- Modify: `apps/frontend-webapp/dashboard.html` (incluir script, ordem padrão)
- Modify: `apps/frontend-webapp/dashboard.js` (`logout()` e `performLogout(motivo)`, wiring inatividade)
- Modify: `apps/frontend-webapp/tests/inactivity.test.js` (teste extra)
- Test: `apps/frontend-webapp/tests/serverLogout.test.js` (novo)

- [ ] **Step 1: Write the failing tests**

`apps/frontend-webapp/tests/serverLogout.test.js`:

```js
'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');

const { serverLogout } = require('../shared/serverLogout.js');

test('chama POST /auth/logout com motivo e tolera falha', async () => {
    let called = null;
    const api = {
        post: async (endpoint, body) => { called = { endpoint, body }; return { ok: true }; }
    };
    const result = await serverLogout(api, { motivo: 'logout' });
    assert.deepEqual(called, { endpoint: '/auth/logout', body: { motivo: 'logout' } });
    assert.ok(result);
});

test('motivo inativo é enviado', async () => {
    let body = null;
    const api = { post: async (_e, b) => { body = b; } };
    await serverLogout(api, { motivo: 'inativo' });
    assert.deepEqual(body, { motivo: 'inativo' });
});

test('falha de rede não rejeita (fire-and-forget)', async () => {
    const api = { post: async () => { throw new Error('offline'); } };
    const result = await serverLogout(api, { motivo: 'logout' });
    assert.equal(result, null);
});
```

`apps/frontend-webapp/tests/inactivity.test.js` — add:

```js
test('handleLogout com onLogout não limpa sessão (delega ao handler)', () => {
    const win = fakeWindow();
    win.self = {};
    win.top = {};
    let cleared = false;
    let handlerCalled = false;
    const tracker = new InactivityTracker({
        window: win,
        document: fakeDoc(),
        autoInit: false,
        session: { clear: () => { cleared = true; } },
        onLogout: () => { handlerCalled = true; }
    });
    tracker.handleLogout();
    assert.equal(handlerCalled, true);
    assert.equal(cleared, false);
    assert.equal(win.location.href, '');
});
```

- [ ] **Step 2: Run tests to verify they fail**
Run: `cd apps/frontend-webapp && node --test tests/serverLogout.test.js tests/inactivity.test.js`
Expected: FAIL — `Cannot find module '../shared/serverLogout.js'`.

- [ ] **Step 3: Write minimal implementation**

`apps/frontend-webapp/shared/serverLogout.js`:

```js
/**
 * Shared server-side logout — GrindX
 *
 * Chama POST /v1/auth/logout (fire-and-forget, tolerante a falha).
 * Uso em testes: require('../shared/serverLogout.js').
 */

(function initServerLogout(globalScope) {
    const serverLogout = (apiClient, { motivo = 'logout' } = {}) => {
        return Promise.resolve(apiClient.post('/auth/logout', { motivo }))
            .catch(() => null);
    };

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = { serverLogout };
    }

    if (globalScope && globalScope.document) {
        globalScope.grindx = globalScope.grindx || {};
        globalScope.grindx.serverLogout = serverLogout;
    }
})(typeof window !== 'undefined' ? window : (typeof globalThis !== 'undefined' ? globalThis : this));
```

Modify `apps/frontend-webapp/dashboard.html` — add `<script src="shared/serverLogout.js"></script>` após `shared/apiService.js`. Ler o arquivo para achar o ponto exato (ordem: config.js → app.js → inactivity.js → apiService.js → **serverLogout.js** → baseController.js → ...).

Modify `apps/frontend-webapp/dashboard.js`:

`logout()` (linha 631):

```js
    logout() {
        this.performLogout('logout');
    }

    performLogout(motivo) {
        window.grindx.serverLogout(window.grindx.api, { motivo })
            .finally(() => {
                window.grindx.session.clear();
                window.location.href = 'index.html';
            });
    }
```

No final de `setupEvents()` (após a linha do `logoutBtnTopbar`), conectar inatividade:

```js
            const tracker = window.grindx.inactivityTracker;
            if (tracker) {
                tracker.onLogout = () => this.performLogout('inativo');
            }
```

- [ ] **Step 4: Run tests to verify they pass**
Run: `cd apps/frontend-webapp && node --test tests/serverLogout.test.js tests/inactivity.test.js`
Expected: PASS (todos, incluindo os antigos).

- [ ] **Step 5: Commit**

```bash
git add apps/frontend-webapp/shared/serverLogout.js apps/frontend-webapp/dashboard.html apps/frontend-webapp/dashboard.js apps/frontend-webapp/tests/serverLogout.test.js apps/frontend-webapp/tests/inactivity.test.js
git commit -m "feat(audit): server-side logout on manual and inactivity logout"
```

---

### Task 7: Módulo frontend "Auditoria"

**Files:**
- Create: `apps/frontend-webapp/modules/auditoria/index.html`
- Create: `apps/frontend-webapp/modules/auditoria/script.js`
- Create: `apps/frontend-webapp/modules/auditoria/style.css`
- Create: `apps/frontend-webapp/modules/auditoria/module.json`
- Modify: `apps/api-postgres/seed.py` (registrar módulo em `modulos_seed`)

- [ ] **Step 1: Write module.json**

`apps/frontend-webapp/modules/auditoria/module.json`:

```json
{
  "module_name": "auditoria",
  "entity_name": "AuditLog",
  "menu_label": "Auditoria",
  "schema_name": "org",
  "route_prefix": "/v1/audit",
  "role_minima": "admin",
  "frontend_tabs": [
    { "name": "Alterações", "endpoint": "/logs" },
    { "name": "Tempo de uso", "endpoint": "/sessoes" }
  ]
}
```

- [ ] **Step 2: Write index.html**

Ordem de scripts padrão: `config.js → app.js → inactivity.js → apiService.js → baseController.js → DataTable.js → LoadingSpinner.js → script.js`.

`apps/frontend-webapp/modules/auditoria/index.html`:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GrindX — Auditoria</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="../../shared/core.css">
    <link rel="stylesheet" href="style.css">
</head>
<body class="module-page">
    <div class="container animate-in">
        <header class="page-header mb-8">
            <div>
                <h1>Auditoria</h1>
                <p class="text-muted">Alterações em banco e tempo de uso dos usuários.</p>
            </div>
        </header>

        <div class="audit-tabs" role="tablist">
            <button class="audit-tab is-active" id="tab-alteracoes" role="tab">Alterações</button>
            <button class="audit-tab" id="tab-tempo" role="tab">Tempo de uso</button>
        </div>

        <div class="audit-filters">
            <input type="text" id="filterUser" class="form-control" placeholder="ID do usuário">
            <input type="text" id="filterEntidade" class="form-control" placeholder="Entidade">
            <select id="filterAcao" class="form-control">
                <option value="">Ação (todas)</option>
                <option value="insert">insert</option>
                <option value="update">update</option>
                <option value="delete">delete</option>
            </select>
            <input type="datetime-local" id="filterInicio" class="form-control">
            <input type="datetime-local" id="filterFim" class="form-control">
            <button class="btn btn-primary" id="btnFiltrar"><i class="fas fa-filter"></i> Filtrar</button>
        </div>

        <div class="audit-card">
            <table class="table">
                <thead>
                    <tr>
                        <th>Data/Hora</th>
                        <th>Usuário</th>
                        <th>Entidade</th>
                        <th>Ação</th>
                        <th>Campos alterados</th>
                        <th>IP</th>
                    </tr>
                </thead>
                <tbody id="logsBody"></tbody>
            </table>
            <div class="audit-pagination" id="logsPagination"></div>
        </div>

        <div class="audit-card" id="tempoCard" hidden>
            <table class="table">
                <thead>
                    <tr>
                        <th>Login</th>
                        <th>Logout</th>
                        <th>Duração</th>
                        <th>Motivo</th>
                        <th>IP</th>
                    </tr>
                </thead>
                <tbody id="sessoesBody"></tbody>
            </table>
            <div class="audit-pagination" id="sessoesPagination"></div>
        </div>
    </div>

    <script src="../../shared/config.js"></script>
    <script src="../../shared/app.js"></script>
    <script src="../../shared/inactivity.js"></script>
    <script src="../../shared/apiService.js"></script>
    <script src="../../shared/baseController.js"></script>
    <script src="../../shared/components/DataTable.js"></script>
    <script src="../../shared/components/LoadingSpinner.js"></script>
    <script src="script.js"></script>
</body>
</html>
```

- [ ] **Step 3: Write script.js**

`apps/frontend-webapp/modules/auditoria/script.js`:

```js
/**
 * Módulo de Auditoria — abas Alterações e Tempo de uso (somente admin).
 */

class AuditoriaController extends window.grindx.controllers.BaseController {
    constructor() {
        super();
        this.pageLogs = 1;
        this.pageSessoes = 1;
        this.PAGE_SIZE = 20;
        this.init();
    }

    async init() {
        if (!this.requireAuth('../../index.html')) return;
        this.bindEvents();
        this.logsTable = new window.grindx.components.DataTable('logsBody', {
            columns: [
                { key: 'criado_em', render: (v) => new Date(v).toLocaleString('pt-BR') },
                { key: 'user_id', render: (v, item) => v || '—' },
                { key: 'entidade' },
                { key: 'acao', render: (v) => `<span class="badge badge-${v}">${v}</span>` },
                { key: 'campos_alterados', render: (v) => Array.isArray(v) ? v.join(', ') : '' },
                { key: 'ip', render: (v) => v || '—' }
            ]
        });
        this.sessoesTable = new window.grindx.components.DataTable('sessoesBody', {
            columns: [
                { key: 'login_at', render: (v) => new Date(v).toLocaleString('pt-BR') },
                { key: 'logout_at', render: (v) => v ? new Date(v).toLocaleString('pt-BR') : '—' },
                { key: 'duracao_segundos', render: (v) => v == null ? '—' : this._formatDuration(v) },
                { key: 'logout_motivo', render: (v) => v || '—' },
                { key: 'ip', render: (v) => v || '—' }
            ]
        });
        await this.loadLogs();
    }

    bindEvents() {
        document.getElementById('tab-alteracoes').onclick = () => this.switchTab('alteracoes');
        document.getElementById('tab-tempo').onclick = () => this.switchTab('tempo');
        document.getElementById('btnFiltrar').onclick = () => {
            this.pageLogs = 1;
            this.loadLogs();
        };
    }

    switchTab(tab) {
        const alt = tab === 'alteracoes';
        document.getElementById('tab-alteracoes').classList.toggle('is-active', alt);
        document.getElementById('tab-tempo').classList.toggle('is-active', !alt);
        document.querySelector('.audit-filters').style.display = alt ? 'flex' : 'none';
        document.querySelector('.audit-card').hidden = !alt;
        document.getElementById('tempoCard').hidden = alt;
        if (!alt) this.loadSessoes();
    }

    _filtros() {
        const val = (id) => document.getElementById(id).value.trim();
        const params = { page: this.pageLogs, page_size: this.PAGE_SIZE };
        if (val('filterUser')) params.user_id = val('filterUser');
        if (val('filterEntidade')) params.entidade = val('filterEntidade');
        if (val('filterAcao')) params.acao = val('filterAcao');
        if (val('filterInicio')) params.data_inicio = new Date(val('filterInicio')).toISOString();
        if (val('filterFim')) params.data_fim = new Date(val('filterFim')).toISOString();
        return params;
    }

    async loadLogs() {
        try {
            const data = await window.grindx.api.get('/audit/logs', this._filtros());
            if (!data.items.length) {
                this.logsTable.renderEmpty('Nenhum log encontrado.');
            } else {
                this.logsTable.render(data.items);
            }
            this._renderPagination('logsPagination', data, () => this.loadLogs());
        } catch (err) {
            window.grindx.components.LoadingSpinner.toast(
                window.grindx.components.LoadingSpinner.toUserMessage(err), 'error'
            );
        }
    }

    async loadSessoes() {
        const params = { page: this.pageSessoes, page_size: this.PAGE_SIZE };
        const u = document.getElementById('filterUser').value.trim();
        if (u) params.user_id = u;
        try {
            const data = await window.grindx.api.get('/audit/sessoes', params);
            if (!data.items.length) {
                this.sessoesTable.renderEmpty('Nenhuma sessão encontrada.');
            } else {
                this.sessoesTable.render(data.items);
            }
            this._renderPagination('sessoesPagination', data, () => this.loadSessoes());
        } catch (err) {
            window.grindx.components.LoadingSpinner.toast(
                window.grindx.components.LoadingSpinner.toUserMessage(err), 'error'
            );
        }
    }

    _renderPagination(containerId, data, reload) {
        const el = document.getElementById(containerId);
        el.innerHTML = '';
        if (data.total_pages <= 1) return;
        const btn = (label, disabled, fn, primary = false) => {
            const b = document.createElement('button');
            b.className = `btn btn-sm ${primary ? 'btn-primary' : 'btn-secondary'}`;
            b.disabled = disabled;
            b.textContent = label;
            b.onclick = fn;
            el.appendChild(b);
        };
        btn('Anterior', data.page <= 1, () => { this.pageLogs--; reload(); });
        btn(`Página ${data.page} de ${data.total_pages}`, true, null, true);
        btn('Próxima', data.page >= data.total_pages, () => { this.pageLogs++; reload(); });
    }

    _formatDuration(seg) {
        const s = seg % 60;
        const m = Math.floor(seg / 60) % 60;
        const h = Math.floor(seg / 3600);
        return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }
}

document.addEventListener('DOMContentLoaded', () => new AuditoriaController());
```

- [ ] **Step 4: Write style.css (somente `var(--...)`)**

`apps/frontend-webapp/modules/auditoria/style.css`:

```css
.audit-tabs { display: flex; gap: var(--space-2, 0.5rem); margin-bottom: var(--space-4, 1rem); }
.audit-tab {
    padding: var(--space-3, 0.75rem) var(--space-4, 1rem);
    background: var(--skin-bg-card, #fff);
    border: 1px solid var(--skin-border-color, #e2e8f0);
    border-radius: var(--skin-radius-md, 0.5rem);
    color: var(--skin-text-muted, #94a3b8);
    cursor: pointer;
}
.audit-tab.is-active { background: var(--skin-primary, #0cb9d4); color: var(--skin-bg-main, #f8fafc); }
.audit-filters { display: flex; flex-wrap: wrap; gap: var(--space-3, 0.75rem); margin-bottom: var(--space-4, 1rem); }
.audit-filters .form-control { width: auto; }
.audit-card { background: var(--skin-bg-card, #fff); border: 1px solid var(--skin-border-color, #e2e8f0); border-radius: var(--skin-radius-lg, 0.75rem); padding: var(--space-4, 1rem); }
.badge { padding: 2px 8px; border-radius: var(--skin-radius-sm, 0.25rem); font-size: 0.75rem; }
.badge-insert { background: rgba(22,163,74,0.15); color: var(--skin-success, #16a34a); }
.badge-update { background: rgba(202,138,4,0.15); color: var(--skin-warning, #ca8a04); }
.badge-delete { background: rgba(220,38,38,0.15); color: var(--skin-danger, #dc2626); }
.audit-pagination { display: flex; gap: var(--space-2, 0.5rem); margin-top: var(--space-4, 1rem); justify-content: flex-end; }
```

- [ ] **Step 5: Registrar módulo no seed**

Modify `apps/api-postgres/seed.py` — add ao `modulos_seed` (dentro da lista, após "Importar Módulos"):

```python
            {
                "aba": "Gestão",
                "nome": "Auditoria",
                "slug": "auditoria",
                "url": "modules/auditoria/index.html",
                "icone": "fas fa-history",
                "role_minima": "admin",
            },
```

- [ ] **Step 6: Verify**
- Rodar `cd apps/frontend-webapp && node --test tests/` (todos os testes JS passam).
- Rodar `cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .venv\Scripts\python -m pytest tests/ -v --tb=short` (PASS).

- [ ] **Step 7: Commit**

```bash
git add apps/frontend-webapp/modules/auditoria apps/api-postgres/seed.py
git commit -m "feat(audit): add Auditoria frontend module (admin)"
```

---

### Task 8: Docs Sync + Pre-push final

**Files:**
- Modify: `README.md`
- Modify: `docs/API.md`
- Modify: `docs/DATABASE.md`
- Modify: `docs/SETUP.md` (se necessário — migração nova)
- Modify: `docs/README.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: Update docs**
  - `README.md`: novo módulo Auditoria (admin), recursos de auditoria/tempo de uso.
  - `docs/API.md`: `POST /v1/auth/logout`, `GET /v1/audit/logs`, `GET /v1/audit/sessoes` (query params, RBAC admin).
  - `docs/DATABASE.md`: tabelas `org.audit_logs` (índices, JSON `campos_alterados`, FK `iam.usuarios`) e `org.sessoes` (FK, motivos `logout|inativo|expirado`).
  - `docs/README.md` e `AGENTS.md`: menção ao módulo Auditoria e à auditoria automática.

- [ ] **Step 2: Pre-push obrigatório (ordem AGENTS.md)**

```bash
make test-all
ruff format packages/ apps/
ruff check --fix .
ruff check .
```

Expected: todos passam sem erros; format sem diffs.

- [ ] **Step 3: Commit**

```bash
git add README.md docs/API.md docs/DATABASE.md docs/SETUP.md docs/README.md AGENTS.md
git commit -m "docs(audit): document auditoria module, sessions and endpoints"
```