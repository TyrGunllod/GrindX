"""Listeners SQLAlchemy para auditoria automática de escritas no banco.

Registra um AuditLog na mesma transação para cada INSERT/UPDATE/DELETE,
utilizando o contexto da requisição (user_id/IP) preenchido pelo middleware.
"""

from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

from app.audit.context import audit_ip, audit_user_id
from app.audit.models import AuditLog, Sessao
from app.modules.org.models.theme_history import ThemeHistory

_MODELOS_EXCLUIDOS = (AuditLog, Sessao, ThemeHistory)


def _campos_alterados(obj, acao: str) -> list[str]:
    """Retorna os nomes das colunas alteradas do objeto."""
    if acao == "delete":
        return []

    campos: list[str] = []
    for col in obj.__table__.columns:
        if col.primary_key:
            continue
        attr = inspect(obj).attrs[col.key]
        hist = attr.history
        if hist.added or (acao == "update" and hist.deleted):
            campos.append(col.key)
    return campos


def _entidade_id(obj):
    return obj.id if getattr(obj, "id", None) is not None else None


@event.listens_for(Session, "before_flush")
def auditar_flush(session: Session, flush_context, instances) -> None:
    """Adiciona AuditLog para cada escrita na mesma transação."""
    user_id = audit_user_id.get()
    ip = audit_ip.get()

    for obj in session.new:
        if isinstance(obj, _MODELOS_EXCLUIDOS):
            continue
        session.add(
            AuditLog(
                user_id=user_id,
                entidade=obj.__class__.__name__,
                entidade_id=_entidade_id(obj),
                acao="insert",
                campos_alterados=_campos_alterados(obj, "insert"),
                ip=ip,
            )
        )

    for obj in session.dirty:
        if isinstance(obj, _MODELOS_EXCLUIDOS):
            continue
        if not session.is_modified(obj, include_collections=False):
            continue
        session.add(
            AuditLog(
                user_id=user_id,
                entidade=obj.__class__.__name__,
                entidade_id=_entidade_id(obj),
                acao="update",
                campos_alterados=_campos_alterados(obj, "update"),
                ip=ip,
            )
        )

    for obj in session.deleted:
        if isinstance(obj, _MODELOS_EXCLUIDOS):
            continue
        session.add(
            AuditLog(
                user_id=user_id,
                entidade=obj.__class__.__name__,
                entidade_id=_entidade_id(obj),
                acao="delete",
                campos_alterados=[],
                ip=ip,
            )
        )
