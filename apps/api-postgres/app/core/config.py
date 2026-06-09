"""
Configuração da aplicação via variáveis de ambiente.

Usa pydantic-settings para validação e tipagem segura.
Todas as variáveis são obrigatórias a menos que tenham valor padrão.
"""

import math
from collections import Counter
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Constante de modulo para compatibilidade com semantic-release version_variable
APP_VERSION = "1.18.0"


class Settings(BaseSettings):
    """Configurações da API PostgreSQL carregadas do .env."""

    # --- Banco de Dados ---
    DATABASE_URL: str

    # --- JWT / Segurança ---
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @field_validator("SECRET_KEY")
    @classmethod
    def validar_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError(
                "SECRET_KEY deve ter pelo menos 32 caracteres. "
                'Gere uma com: python -c "import secrets; print(secrets.token_hex(32))"'
            )
        # Validação de entropia Shannon — rejeita chaves com baixa aleatoriedade
        freq = Counter(v)
        length = len(v)
        entropy = -sum(
            (count / length) * math.log2(count / length) for count in freq.values()
        )
        if entropy < 3.5:
            raise ValueError(
                f"SECRET_KEY tem entropia muito baixa ({entropy:.2f} bits/caractere). "
                'Use uma chave aleatória: python -c "import secrets; print(secrets.token_hex(32))"'
            )
        return v

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:3000"

    # --- Aplicação ---
    APP_NAME: str = "ERP API Postgres"
    APP_VERSION: str = APP_VERSION
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # --- SMTP / Email ---
    SMTP_HOST: str = "127.0.0.1"
    SMTP_PORT: int = 2525
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SMTP_USE_TLS: bool = False
    EMAIL_FROM: str = "admin@grindx.local"
    EMAIL_FROM_NAME: str = "GrindX Administrador"

    # --- Import de Módulos ---
    IMPORT_DIR: str = ""

    @property
    def import_dir_path(self) -> str:
        """Resolved import directory path."""
        if self.IMPORT_DIR:
            return self.IMPORT_DIR
        return str(
            Path(__file__).resolve().parent.parent.parent.parent.parent / "import"
        )

    # --- Rate Limiting ---
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    @property
    def is_production(self) -> bool:
        """Retorna True se o ambiente é produção."""
        return self.ENVIRONMENT == "production"

    @property
    def allowed_origins_list(self) -> list[str]:
        """Retorna lista de origens CORS permitidas."""
        # Em produção, CORS_ORIGINS é obrigatório e não pode ser "*"
        if self.is_production:
            if not self.CORS_ORIGINS.strip():
                raise ValueError(
                    "CORS_ORIGINS obrigatório em produção. "
                    "Defina origins explícitos (ex: https://app.grindx.com)"
                )
            if "*" in self.CORS_ORIGINS:
                raise ValueError("CORS_ORIGINS não pode ser '*' em produção")

        # Parse das origens
        clean_value = (
            self.CORS_ORIGINS.replace("[", "")
            .replace("]", "")
            .replace('"', "")
            .replace("'", "")
        )
        parsed = [origin.strip() for origin in clean_value.split(",") if origin.strip()]

        # Em dev com CORS_ORIGINS vazio, retorna localhost defaults
        if not self.is_production and not parsed:
            return [
                "http://localhost:3000",
                "http://localhost:5500",
                "http://127.0.0.1:5500",
            ]

        return parsed

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Instância singleton carregada uma única vez
settings = Settings()
