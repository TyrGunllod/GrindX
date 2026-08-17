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
                from shared.security.jwt import verificar_jwt

                from app.core.config import settings

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
