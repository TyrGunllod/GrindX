"""
Configuração da API SQL Server via variáveis de ambiente.

Usa pydantic-settings para validação e tipagem segura.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da API SQL Server carregadas do .env."""

    # --- Banco de Dados (somente leitura) ---
    DATABASE_URL: str

    # --- JWT / Segurança (mesma chave da api-postgres para validação) ---
    SECRET_KEY: str

    # --- CORS ---
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # --- Aplicação ---
    APP_NAME: str = "ERP API SQL Server"
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


settings = Settings()
