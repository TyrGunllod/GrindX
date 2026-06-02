"""
Alembic environment configuration.

Configura como o Alembic deve detectar mudanças nos modelos
e como executar migrações.
"""

import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

# Adiciona o diretório raiz ao sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.modules.iam.base import IamBase

# Importar todos os models para o autogenerate detectar
from app.modules.iam.models.usuario import Usuario, UsuarioModulo  # noqa: F401
from app.modules.org.models.empresa import Empresa  # noqa: F401
from app.modules.org.models.theme import CompanyTheme  # noqa: F401
from app.modules.org.models.theme_history import ThemeHistory  # noqa: F401
from app.modules.portal.models.portal import Aba, Modulo  # noqa: F401
from app.modules.gestao_projetos.models.gestao_projetos import GestaoProjetos  # noqa: F401

# this is the Alembic Config object, which provides
# the values of the [alembic] section of the .ini
# file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the sqlalchemy.url from app settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = IamBase.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        include_schemas=True,
        version_table_schema="public",
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema="public",
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
