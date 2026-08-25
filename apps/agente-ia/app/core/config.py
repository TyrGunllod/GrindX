"""
Configuração da API do Agente de IA via variáveis de ambiente.

Usa pydantic-settings para validação e tipagem segura.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

# Constante de modulo para compatibilidade com semantic-release version_variable
APP_VERSION = "0.1.0"


class Settings(BaseSettings):
    """Configurações da API do Agente de IA carregadas do .env."""

    # --- Banco de Dados (PostgreSQL do GrindX + pgvector) ---
    DATABASE_URL: str = ""
    AGENT_SCHEMA: str = "agente"
    AGENT_TABLE: str = "chunks"

    # --- LLM (geração, via DeepSeek) ---
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.deepseek.com"
    LLM_MODEL: str = "deepseek-chat"
    LLM_TIMEOUT_SECONDS: int = 60

    # --- Embeddings (modelo local) ---
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIM: int = 384
    # Em planos sem memória suficiente (ex.: Render free 512MB), desative os
    # embeddings e use a busca por palavras-chave (sem carregar modelo).
    EMBEDDINGS_ENABLED: bool = True

    # --- Recuperação (RAG) ---
    SIMILARITY_THRESHOLD: float = 0.35
    TOP_K: int = 5

    # --- CORS ---
    CORS_ORIGINS: str = ""

    # --- IP da rede local para acesso externo em dev ---
    DEV_NETWORK_IP: str = ""

    # --- Aplicação ---
    APP_NAME: str = "GrindX Agente IA"
    APP_VERSION: str = APP_VERSION
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # --- Logs JSONL ---
    LOGS_DIR: str = ""

    @property
    def is_production(self) -> bool:
        """Retorna True se o ambiente é produção."""
        return self.ENVIRONMENT == "production"

    @property
    def allowed_origins_list(self) -> list[str]:
        """Retorna lista de origens CORS permitidas."""
        if self.is_production:
            if not self.CORS_ORIGINS.strip():
                raise ValueError(
                    "CORS_ORIGINS obrigatório em produção. "
                    "Defina origins explícitos (ex: https://app.grindx.com)"
                )
            if "*" in self.CORS_ORIGINS:
                raise ValueError("CORS_ORIGINS não pode ser '*' em produção")

        clean_value = (
            self.CORS_ORIGINS.replace("[", "")
            .replace("]", "")
            .replace('"', "")
            .replace("'", "")
        )
        parsed = [origin.strip() for origin in clean_value.split(",") if origin.strip()]

        if not self.is_production:
            origins = [
                "http://localhost:8101",
                "http://127.0.0.1:8101",
                "https://localhost:8443",
                "https://127.0.0.1:8443",
            ]
            if self.DEV_NETWORK_IP:
                origins.append(f"http://{self.DEV_NETWORK_IP}:8101")
                origins.append(f"https://{self.DEV_NETWORK_IP}:8443")
            return list(dict.fromkeys(parsed + origins))

        return parsed

    @property
    def csp_connect_srcs(self) -> list[str]:
        """URLs permitidas no CSP connect-src."""
        return ["'self'", "http://localhost:8003", "https://localhost:8003"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
