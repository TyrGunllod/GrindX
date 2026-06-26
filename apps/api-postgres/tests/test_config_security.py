"""
Testes de segurança para configuração da aplicação.

Valida:
- SECRET_KEY: rejeita chaves com entropia Shannon baixa
- CORS: em produção, rejeita wildcard e exige lista explícita
"""

import secrets

import pytest


class TestSecretKeyEntropy:
    """Testes para validação de entropia Shannon no SECRET_KEY."""

    def test_secret_key_rejects_low_entropy(self):
        """Chave com todos os caracteres iguais (entropia ~0) deve ser rejeitada."""
        from app.core.config import Settings

        with pytest.raises(ValueError, match="entropia muito baixa"):
            Settings(SECRET_KEY="a" * 32)

    def test_secret_key_accepts_high_entropy(self):
        """Chave gerada por secrets.token_urlsafe(32) deve passar (entropia ~5.8)."""
        from app.core.config import Settings

        key = secrets.token_urlsafe(32)
        settings = Settings(SECRET_KEY=key)
        assert settings.SECRET_KEY == key

    def test_secret_key_rejects_short_key(self):
        """Chave com menos de 32 caracteres deve ser rejeitada."""
        from app.core.config import Settings

        with pytest.raises(ValueError, match="32 caracteres"):
            Settings(SECRET_KEY="short")


class TestCorsConfiguration:
    """Testes para validação de CORS em modo produção."""

    def test_cors_production_rejects_wildcard(self):
        """Em produção, CORS_ORIGINS='*' deve ser rejeitado."""
        from app.core.config import Settings

        settings = Settings(
            SECRET_KEY=secrets.token_urlsafe(32),
            ENVIRONMENT="production",
            CORS_ORIGINS="*",
        )
        with pytest.raises(ValueError, match="não pode ser '\\*'"):
            _ = settings.allowed_origins_list

    def test_cors_production_requires_origins(self):
        """Em produção, CORS_ORIGINS vazio deve levantar erro."""
        from app.core.config import Settings

        settings = Settings(
            SECRET_KEY=secrets.token_urlsafe(32),
            ENVIRONMENT="production",
            CORS_ORIGINS="",
        )
        with pytest.raises(ValueError, match="obrigatório em produção"):
            _ = settings.allowed_origins_list

    def test_cors_production_accepts_explicit_origins(self):
        """Em produção, origens explícitas devem ser aceitas normalmente."""
        from app.core.config import Settings

        settings = Settings(
            SECRET_KEY=secrets.token_urlsafe(32),
            ENVIRONMENT="production",
            CORS_ORIGINS="https://app.grindx.com",
        )
        assert settings.allowed_origins_list == ["https://app.grindx.com"]

    def test_cors_dev_allows_empty(self):
        """Em desenvolvimento, CORS_ORIGINS vazio retorna localhost defaults."""
        from app.core.config import Settings

        settings = Settings(
            SECRET_KEY=secrets.token_urlsafe(32),
            ENVIRONMENT="development",
            CORS_ORIGINS="",
        )
        origins = settings.allowed_origins_list
        assert "http://localhost:3000" in origins
        assert "http://localhost:8101" in origins
        assert "http://127.0.0.1:8101" in origins

    def test_cors_dev_network_ip(self):
        """DEV_NETWORK_IP deve adicionar origem extra."""
        from app.core.config import Settings

        settings = Settings(
            SECRET_KEY=secrets.token_urlsafe(32),
            ENVIRONMENT="development",
            CORS_ORIGINS="",
            DEV_NETWORK_IP="192.168.0.62",
        )
        origins = settings.allowed_origins_list
        assert "http://192.168.0.62:8101" in origins
