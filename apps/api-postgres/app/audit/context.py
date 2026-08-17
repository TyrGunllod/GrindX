"""Contexto de auditoria da requisição atual (ContextVar)."""

from contextvars import ContextVar

audit_user_id: ContextVar[int | None] = ContextVar("audit_user_id", default=None)
audit_ip: ContextVar[str | None] = ContextVar("audit_ip", default=None)
