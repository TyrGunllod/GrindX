"""Utilitários de rede — extração do IP real do cliente."""


def get_client_ip(request) -> str | None:
    """Extrai o IP real do cliente, respeitando o header X-Forwarded-For.

    O nginx (frontend) repassa o IP original via X-Forwarded-For; sem o header
    (ex.: acesso direto em dev), usa o IP do peer da conexão (request.client.host).

    Args:
        request: Request do Starlette/FastAPI.

    Returns:
        IP do cliente, ou None se não houver informação disponível.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip() or None
    return request.client.host if request.client else None
