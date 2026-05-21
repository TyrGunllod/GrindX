"""
Configuração da API SQL Server via variáveis de ambiente.

Usa pydantic-settings para validação e tipagem segura.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da API SQL Server carregadas do .env."""

    # --- Banco de Dados SQL Server ---
    DB_SERVER: str = ""
    DB_DATABASE: str = ""
    DB_USERNAME: str = ""
    DB_PASSWORD: str = ""
    DB_DRIVER: str = "ODBC Driver 17 for SQL Server"

    # --- Override direto da URL (para testes com SQLite) ---
    DB_URL_OVERRIDE: str = ""

    # --- JWT / Segurança (mesma chave da api-postgres para validação) ---
    SECRET_KEY: str = "your-secret-key-here"  # Recomenda-se definir no .env

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["*"]

    # --- Aplicação ---
    APP_NAME: str = "ERP API SQL Server"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENABLE_CACHE: bool = False
    LOG_LEVEL: str = "INFO"

    # --- Rate Limiting ---
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    @property
    def DATABASE_URL(self) -> str:
        """Retorna DB_URL_OVERRIDE se definido, senão constrói a URL."""
        if self.DB_URL_OVERRIDE:
            return self.DB_URL_OVERRIDE

        import urllib.parse

        if not self.DB_SERVER:
            return "sqlite:///:memory:"

        password = urllib.parse.quote_plus(self.DB_PASSWORD)

        if "ODBC" in self.DB_DRIVER:
            driver = urllib.parse.quote_plus(self.DB_DRIVER)
            return f"mssql+pyodbc://{self.DB_USERNAME}:{password}@{self.DB_SERVER}/{self.DB_DATABASE}?driver={driver}"

        server = self.DB_SERVER.replace(",", ":")
        return (
            f"mssql+pymssql://{self.DB_USERNAME}:{password}@{server}/{self.DB_DATABASE}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignora variáveis extras no .env
    )


settings = Settings()
