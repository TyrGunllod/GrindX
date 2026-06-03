"""
Middleware de rate limiting com SlowAPI (limits library).

Dual key strategy:
- Endpoints autenticados: rate limit por user_id (extraído do JWT)
- Endpoints não-autenticados: rate limit por IP

Usa limits library (SlowAPI internals) para janela deslizante em memória.

Nota: Em produção com múltiplos workers, considere usar Redis
para armazenamento distribuído dos contadores.
"""

import time

import structlog
from jose import JWTError, jwt
from limits import parse
from limits.storage import MemoryStorage
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = structlog.get_logger(__name__)

# Singleton storage compartilhado entre todas as instâncias do middleware
_storage = MemoryStorage()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiter com janela deslizante usando limits library.

    Dual key strategy:
    - Endpoints autenticados: rate limit por user_id (extraído do JWT)
    - Endpoints não-autenticados: rate limit por IP

    Dois usuários do mesmo IP recebem rate limits independentes.

    Args:
        app: Aplicação ASGI.
        max_requests: Número máximo de requisições por janela.
        window_seconds: Tamanho da janela em segundos.
        exclude_paths: Paths que não sofrem rate limiting (ex: /health).
    """

    def __init__(
        self,
        app,
        max_requests: int = 100,
        window_seconds: int = 60,
        exclude_paths: list[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.exclude_paths = exclude_paths or ["/health"]
        self._limit = parse(f"{max_requests}/{window_seconds}second")
        self._secret_key: str | None = None  # Lazy-loaded

    def _get_secret_key(self) -> str | None:
        """Lazy-load SECRET_KEY from settings."""
        if self._secret_key is None:
            try:
                from app.core.config import settings

                self._secret_key = settings.SECRET_KEY
            except Exception:
                self._secret_key = ""
        return self._secret_key

    def _get_client_ip(self, request: Request) -> str:
        """Extrai o IP real do cliente, considerando proxies."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _get_user_id_from_token(self, request: Request) -> str | None:
        """Tenta extrair user_id do token JWT no header Authorization."""
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header[7:]
        secret = self._get_secret_key()
        if not secret:
            return None

        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except JWTError:
            pass  # Token inválido — fallback para IP
        return None

    def _get_rate_limit_key(self, request: Request) -> str:
        """Retorna a chave de rate limiting.

        - Usuário autenticado: 'user:{user_id}' (rate limit independente por conta)
        - Usuário não autenticado: 'ip:{client_ip}' (rate limit por IP)
        """
        user_key = self._get_user_id_from_token(request)
        if user_key:
            return user_key
        return f"ip:{self._get_client_ip(request)}"

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Paths excluídos do rate limiting
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        key = self._get_rate_limit_key(request)

        # Tenta adquirir entrada — retorna False se limite excedido
        allowed = _storage.acquire_entry(
            key, self._limit.amount, self._limit.get_expiry()
        )

        if not allowed:
            logger.warning(
                "Rate limit excedido",
                key=key,
                path=request.url.path,
            )
            # Calcula retry-after a partir da janela deslizante
            window_start, _count = _storage.get_moving_window(
                key, self._limit.amount, self._limit.get_expiry()
            )
            retry_after = max(
                1,
                int(self._limit.get_expiry() - (time.time() - window_start)),
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "RATE_LIMIT_EXCEDIDO",
                    "message": "Muitas requisições. Tente novamente em breve.",
                    "status_code": 429,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                },
            )

        # Obtém contagem atual para headers
        _window_start, count = _storage.get_moving_window(
            key, self._limit.amount, self._limit.get_expiry()
        )
        remaining = max(0, self.max_requests - count)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
