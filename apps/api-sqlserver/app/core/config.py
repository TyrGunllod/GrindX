"""
Configuração da API SQL Server via variáveis de ambiente.

Usa pydantic-settings para validação e tipagem segura.
"""

import math
from collections import Counter

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Constante de modulo para compatibilidade com semantic-release version_variable
APP_VERSION = "1.48.0"


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
    CORS_ORIGINS: str = ""

    # --- IP da rede local para acesso externo em dev ---
    DEV_NETWORK_IP: str = ""

    # --- Aplicação ---
    APP_NAME: str = "ERP API SQL Server"
    APP_VERSION: str = APP_VERSION
    DEBUG: bool = False
    ENABLE_CACHE: bool = False
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

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
            origins = [
                "http://localhost:3000",
                "http://localhost:8101",
                "http://127.0.0.1:8101",
            ]
            if self.DEV_NETWORK_IP:
                origins.append(f"http://{self.DEV_NETWORK_IP}:8101")
            return origins

        return parsed

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

    @property
    def csp_connect_srcs(self) -> list[str]:
        """URLs permitidas no CSP connect-src."""
        srcs = [
            "'self'",
            "http://localhost:8001",
            "http://localhost:8002",
            "https://localhost:8002",
        ]
        if self.DEV_NETWORK_IP:
            srcs.append(f"http://{self.DEV_NETWORK_IP}:8001")
            srcs.append(f"http://{self.DEV_NETWORK_IP}:8002")
            srcs.append(f"https://{self.DEV_NETWORK_IP}:8002")
        return srcs

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignora variáveis extras no .env
    )


settings = Settings()
