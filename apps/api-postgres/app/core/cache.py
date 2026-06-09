"""
Camada de cache in-memory usando cachetools TTLCache.

Fornece caches thread-safe para queries frequentes:
- Temas ativos por empresa
- Módulos do portal (abas)
- Dados de usuários

TTL de 15 minutos (900 segundos) para balancear performance e frescor.
"""

import threading

from cachetools import TTLCache

# === Instâncias de Cache ===
# maxsize=100 limita entradas para prevenir crescimento ilimitado de memória
# ttl=900 = 15 minutos em segundos

_theme_cache: TTLCache = TTLCache(maxsize=100, ttl=900)
_portal_cache: TTLCache = TTLCache(maxsize=100, ttl=900)
_user_cache: TTLCache = TTLCache(maxsize=100, ttl=900)

# === Locks para thread safety ===
_theme_lock = threading.Lock()
_portal_lock = threading.Lock()
_user_lock = threading.Lock()


def get_or_set(cache: TTLCache, lock: threading.Lock, key: str, fetch_fn) -> object:
    """Obtém valor do cache ou executa fetch_fn e armazena o resultado.

    Args:
        cache: Instância do TTLCache.
        lock: Lock thread-safe para o cache.
        key: Chave de busca no cache.
        fetch_fn: Função callable para buscar o valor em caso de miss.

    Returns:
        Valor do cache (hit) ou resultado de fetch_fn (miss).
    """
    with lock:
        if key in cache:
            return cache[key]

    # Fora do lock para não bloquear outras threads durante a query
    value = fetch_fn()

    with lock:
        cache[key] = value

    return value


def invalidate(cache: TTLCache, lock: threading.Lock, key: str) -> None:
    """Remove uma chave específica do cache.

    Args:
        cache: Instância do TTLCache.
        lock: Lock thread-safe para o cache.
        key: Chave a ser removida.
    """
    with lock:
        cache.pop(key, None)


def clear_all() -> None:
    """Limpa todos os caches. Útil para testes e reset de estado."""
    _theme_cache.clear()
    _portal_cache.clear()
    _user_cache.clear()
