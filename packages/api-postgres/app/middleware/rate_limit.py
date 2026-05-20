"""
Middleware de rate limiting customizado.

Implementação em memória com janela deslizante por IP.
Limita requisições por IP dentro de uma janela de tempo configurável.

Nota: Em produção com múltiplos workers, considere usar Redis
para armazenamento distribuído dos contadores.
"""

import time
from collections import defaultdict

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = structlog.get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiter por IP com janela deslizante em memória.

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
        # Armazena timestamps de requisições por IP
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        """Extrai o IP real do cliente, considerando proxies."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _clean_old_requests(self, client_ip: str, now: float) -> None:
        """Remove timestamps fora da janela atual."""
        cutoff = now - self.window_seconds
        self._requests[client_ip] = [
            ts for ts in self._requests[client_ip] if ts > cutoff
        ]

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Paths excluídos do rate limiting
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        now = time.time()

        # Limpa requisições expiradas
        self._clean_old_requests(client_ip, now)

        # Verifica limite
        if len(self._requests[client_ip]) >= self.max_requests:
            logger.warning(
                "Rate limit excedido",
                client_ip=client_ip,
                requests_count=len(self._requests[client_ip]),
            )
            retry_after = int(
                self.window_seconds - (now - self._requests[client_ip][0])
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "RATE_LIMIT_EXCEDIDO",
                    "message": "Muitas requisições. Tente novamente em breve.",
                    "status_code": 429,
                },
                headers={
                    "Retry-After": str(max(retry_after, 1)),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                },
            )

        # Registra requisição
        self._requests[client_ip].append(now)
        remaining = self.max_requests - len(self._requests[client_ip])

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
