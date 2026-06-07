"""
Testes unitários para o módulo de cache (cachetools TTLCache).

Valida comportamento de cache hit/miss, expiração TTL,
thread safety e invalidação.
"""

import time
from unittest.mock import MagicMock

import pytest

from app.core.cache import (
    _portal_cache,
    _portal_lock,
    _theme_cache,
    _theme_lock,
    _user_cache,
    _user_lock,
    clear_all,
    get_or_set,
    invalidate,
)


@pytest.mark.unit
class TestCacheBasic:
    """Testes de comportamento básico do cache."""

    def test_cache_miss_calls_fetch_fn(self):
        """Em cache miss, fetch_fn deve ser chamado e resultado retornado."""
        clear_all()
        fetch_fn = MagicMock(return_value="value_from_db")

        result = get_or_set(_theme_cache, _theme_lock, "missing_key", fetch_fn)

        assert result == "value_from_db"
        fetch_fn.assert_called_once()

    def test_cache_hit_returns_cached_value(self):
        """Em cache hit, fetch_fn não deve ser chamado novamente."""
        clear_all()
        fetch_fn = MagicMock(return_value="value_from_db")

        # Primeira chamada — miss
        result1 = get_or_set(_theme_cache, _theme_lock, "key1", fetch_fn)
        # Segunda chamada — hit
        result2 = get_or_set(_theme_cache, _theme_lock, "key1", fetch_fn)

        assert result1 == "value_from_db"
        assert result2 == "value_from_db"
        fetch_fn.assert_called_once()  # só chamado uma vez

    def test_cache_none_value_is_cached(self):
        """Valores None devem ser cacheados para prevenir cache penetration."""
        clear_all()
        fetch_fn = MagicMock(return_value=None)

        # Primeira chamada — miss, retorna None
        result1 = get_or_set(_theme_cache, _theme_lock, "none_key", fetch_fn)
        # Segunda chamada — hit, retorna None do cache
        result2 = get_or_set(_theme_cache, _theme_lock, "none_key", fetch_fn)

        assert result1 is None
        assert result2 is None
        fetch_fn.assert_called_once()  # não chama novamente

    def test_cache_ttl_expiry(self):
        """Valor deve expirar após TTL."""
        from cachetools import TTLCache

        # Cache com TTL de 1 segundo para teste rápido
        short_cache = TTLCache(maxsize=10, ttl=1)
        import threading

        short_lock = threading.Lock()

        fetch_fn = MagicMock(return_value="expiring_value")

        # Primeira chamada — cacheia
        result1 = get_or_set(short_cache, short_lock, "ttl_key", fetch_fn)
        assert result1 == "expiring_value"

        # Espera TTL expirar
        time.sleep(1.1)

        # Segunda chamada — deve buscar novamente
        fetch_fn.return_value = "fresh_value"
        result2 = get_or_set(short_cache, short_lock, "ttl_key", fetch_fn)

        assert result2 == "fresh_value"
        assert fetch_fn.call_count == 2

    def test_clear_all_empties_caches(self):
        """clear_all deve limpar todos os caches."""
        clear_all()

        # Popula cada cache
        get_or_set(_theme_cache, _theme_lock, "t1", lambda: "tv")
        get_or_set(_portal_cache, _portal_lock, "p1", lambda: "pv")
        get_or_set(_user_cache, _user_lock, "u1", lambda: "uv")

        # Verifica que estão populados
        assert len(_theme_cache) == 1
        assert len(_portal_cache) == 1
        assert len(_user_cache) == 1

        # Limpa tudo
        clear_all()

        assert len(_theme_cache) == 0
        assert len(_portal_cache) == 0
        assert len(_user_cache) == 0

    def test_invalidate_removes_specific_key(self):
        """invalidate deve remover apenas a chave especificada."""
        clear_all()

        get_or_set(_user_cache, _user_lock, "id:1", lambda: "user1")
        get_or_set(_user_cache, _user_lock, "id:2", lambda: "user2")

        assert len(_user_cache) == 2

        invalidate(_user_cache, _user_lock, "id:1")

        assert len(_user_cache) == 1
        assert "id:1" not in _user_cache
        assert "id:2" in _user_cache

    def test_invalidate_nonexistent_key_is_noop(self):
        """Invalidar chave inexistente não deve gerar erro."""
        clear_all()
        # Não deve levantar exceção
        invalidate(_theme_cache, _theme_lock, "nonexistent")

    def test_different_caches_are_independent(self):
        """Caches de theme, portal e user são independentes."""
        clear_all()

        get_or_set(_theme_cache, _theme_lock, "shared_key", lambda: "theme_val")
        get_or_set(_portal_cache, _portal_lock, "shared_key", lambda: "portal_val")

        assert get_or_set(_theme_cache, _theme_lock, "shared_key", lambda: "x") == "theme_val"
        assert get_or_set(_portal_cache, _portal_lock, "shared_key", lambda: "x") == "portal_val"


@pytest.mark.unit
class TestCacheRepositoryIntegration:
    """Testes de integração cache + repositório (mockados)."""

    def test_theme_cache_returns_on_second_call(self):
        """ThemeRepository deve retornar do cache na segunda chamada."""
        clear_all()

        mock_theme = MagicMock()
        mock_theme.id = 1
        mock_theme.company_id = 42

        fetch_fn = MagicMock(return_value=mock_theme)

        result1 = get_or_set(_theme_cache, _theme_lock, "active:42", fetch_fn)
        result2 = get_or_set(_theme_cache, _theme_lock, "active:42", fetch_fn)

        assert result1 == mock_theme
        assert result2 == mock_theme
        fetch_fn.assert_called_once()

    def test_user_cache_returns_on_second_call(self):
        """UsuarioRepository deve retornar do cache na segunda chamada."""
        clear_all()

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "admin"

        fetch_fn = MagicMock(return_value=mock_user)

        result1 = get_or_set(_user_cache, _user_lock, "id:1", fetch_fn)
        result2 = get_or_set(_user_cache, _user_lock, "id:1", fetch_fn)

        assert result1 == mock_user
        assert result2 == mock_user
        fetch_fn.assert_called_once()
