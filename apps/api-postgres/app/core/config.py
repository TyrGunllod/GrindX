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
APP_VERSION = "1.32.1"


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

    # --- IP da rede local para acesso externo em dev ---
    DEV_NETWORK_IP: str = ""

    # --- Aplicação ---
    APP_NAME: str = "ERP API Postgres"
    APP_VERSION: str = APP_VERSION
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # --- Proxy ---
    PROXY_MODE: bool = False

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

    # --- Skins Snapshot Directory ---
    SKINS_DIR: str = ""

    @property
    def import_dir_path(self) -> str:
        """Resolved import directory path."""
        if self.IMPORT_DIR:
            return self.IMPORT_DIR
        return str(
            Path(__file__).resolve().parent.parent.parent.parent.parent / "import"
        )

    @property
    def skins_dir_path(self) -> str:
        """Resolved skins snapshot directory path."""
        if self.SKINS_DIR:
            return self.SKINS_DIR
        return str(
            Path(__file__).resolve().parent.parent.parent.parent.parent
            / "apps"
            / "frontend-webapp"
            / "skins"
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

        # Em dev, garante que origins de desenvolvimento estejam sempre presentes
        if not self.is_production:
            dev_origins = [
                "http://localhost:3000",
                "http://localhost:8101",
                "http://127.0.0.1:8101",
            ]
            if self.DEV_NETWORK_IP:
                dev_origins.append(f"http://{self.DEV_NETWORK_IP}:8101")
            # Mescla com o que veio do CORS_ORIGINS (evita duplicatas)
            merged = list(dict.fromkeys(parsed + dev_origins))
            return merged

        return parsed

    @property
    def csp_connect_srcs(self) -> list[str]:
        """URLs permitidas no CSP connect-src."""
        if self.PROXY_MODE:
            return ["'self'"]
        srcs = ["'self'", "http://localhost:8001", "http://localhost:8002"]
        if self.DEV_NETWORK_IP:
            srcs.append(f"http://{self.DEV_NETWORK_IP}:8001")
            srcs.append(f"http://{self.DEV_NETWORK_IP}:8002")
        return srcs

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Instância singleton carregada uma única vez
settings = Settings()
