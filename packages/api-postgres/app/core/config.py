"""
Configuração da aplicação via variáveis de ambiente.

Usa pydantic-settings para validação e tipagem segura.
Todas as variáveis são obrigatórias a menos que tenham valor padrão.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da API PostgreSQL carregadas do .env."""

    # --- Banco de Dados ---
    DATABASE_URL: str

    # --- JWT / Segurança ---
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- CORS ---
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # --- Aplicação ---
    APP_NAME: str = "ERP API Postgres"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # --- Rate Limiting ---
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    @property
    def allowed_origins_list(self) -> list[str]:
        """Retorna lista de origens CORS permitidas."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Instância singleton carregada uma única vez
settings = Settings()
