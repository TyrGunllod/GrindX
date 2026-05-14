"""
Configuração da API SQL Server via variáveis de ambiente.

Usa pydantic-settings para validação e tipagem segura.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da API SQL Server carregadas do .env."""

    # --- Banco de Dados SQL Server ---
    DB_SERVER: str
    DB_DATABASE: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_DRIVER: str = "ODBC Driver 17 for SQL Server"

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
        """Constrói a URL de conexão baseada nas configurações.
        
        Se DB_DRIVER contiver 'ODBC', utiliza pyodbc. Caso contrário, pymssql.
        """
        import urllib.parse
        
        # URL encode do password (pode conter caracteres especiais como @)
        password = urllib.parse.quote_plus(self.DB_PASSWORD)
        
        if "ODBC" in self.DB_DRIVER:
            # Para pyodbc (Microsoft ODBC Driver)
            driver = urllib.parse.quote_plus(self.DB_DRIVER)
            return f"mssql+pyodbc://{self.DB_USERNAME}:{password}@{self.DB_SERVER}/{self.DB_DATABASE}?driver={driver}"
        
        # Fallback para pymssql (usa dois pontos para porta e não precisa de driver string)
        server = self.DB_SERVER.replace(",", ":")
        return f"mssql+pymssql://{self.DB_USERNAME}:{password}@{server}/{self.DB_DATABASE}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore", # Ignora variáveis extras no .env
    )


settings = Settings()
