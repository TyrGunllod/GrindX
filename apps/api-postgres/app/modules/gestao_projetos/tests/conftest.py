import importlib.util
import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import Column, Integer, String, Table, create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

GRINDX_PACKAGES = os.environ.get(
    "GRINDX_PACKAGES",
    str(Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent.parent / "GrindX" / "packages"),
)
GRINDX_API = str(Path(GRINDX_PACKAGES).parent / "apps" / "api-postgres")
LOCAL_MODULES = str(Path(__file__).resolve().parent.parent.parent)

for p in [GRINDX_PACKAGES, GRINDX_API, LOCAL_MODULES]:
    if p not in sys.path:
        sys.path.insert(0, p)

import app  # noqa: E402
import app.modules  # noqa: E402

_local_pkg = Path(LOCAL_MODULES) / "gestao_projetos"
_spec = importlib.util.spec_from_file_location(
    "app.modules.gestao_projetos",
    str(_local_pkg / "__init__.py"),
    submodule_search_locations=[str(_local_pkg)],
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["app.modules.gestao_projetos"] = _mod
_spec.loader.exec_module(_mod)

from app.modules.iam.base import IamBase  # noqa: E402

Table(
    "usuarios",
    IamBase.metadata,
    Column("id", Integer, primary_key=True),
    Column("nome", String(200)),
    Column("nome_completo", String(200)),
    schema="iam",
)

from app.modules.gestao_projetos.models.projeto import Projeto  # noqa: E402, F401
from app.modules.gestao_projetos.models.tarefa import Tarefa  # noqa: E402, F401
from app.modules.gestao_projetos.models.registro_tarefa import RegistroTarefa  # noqa: E402, F401
from app.modules.gestao_projetos.models.recurso import Recurso  # noqa: E402, F401

_SCHEMA_TRANSLATE = {"iam": None, "portal": None, "catalogo": None, "org": None}
_all_metadata = IamBase.metadata

_CREATE_TABLES_SQL = [
    "CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, nome VARCHAR(200), nome_completo VARCHAR(200))",
    "CREATE TABLE IF NOT EXISTS projetos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome VARCHAR(200) NOT NULL, descricao TEXT, status VARCHAR(20) DEFAULT 'planning' NOT NULL, data_inicio DATE NOT NULL, data_fim DATE NOT NULL, cor VARCHAR(7) DEFAULT '#3b82f6' NOT NULL, gerente_id INTEGER REFERENCES usuarios(id), ativo BOOLEAN DEFAULT 1 NOT NULL, criado_em DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL)",
    "CREATE TABLE IF NOT EXISTS recursos (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES usuarios(id), projeto_id INTEGER NOT NULL, cargo_contexto VARCHAR(100), cor VARCHAR(7) DEFAULT '#3b82f6' NOT NULL, alocado BOOLEAN DEFAULT 1 NOT NULL, criado_em DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, UNIQUE(user_id, projeto_id))",
    "CREATE TABLE IF NOT EXISTS tarefas (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo VARCHAR(255) NOT NULL, descricao TEXT, status VARCHAR(20) DEFAULT 'todo' NOT NULL, prioridade VARCHAR(10) DEFAULT 'medium' NOT NULL, data_inicio DATE NOT NULL, data_fim DATE NOT NULL, progresso INTEGER DEFAULT 0 NOT NULL, projeto_id INTEGER REFERENCES projetos(id) ON DELETE CASCADE, responsavel_id INTEGER REFERENCES recursos(id) ON DELETE SET NULL, ativo BOOLEAN DEFAULT 1 NOT NULL, criado_em DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL)",
    "CREATE TABLE IF NOT EXISTS registros_tarefas (id INTEGER PRIMARY KEY AUTOINCREMENT, tarefa_id INTEGER NOT NULL REFERENCES tarefas(id) ON DELETE CASCADE, tipo VARCHAR(20) DEFAULT 'log' NOT NULL, conteudo TEXT NOT NULL, autor_id INTEGER REFERENCES recursos(id) ON DELETE SET NULL, ativo BOOLEAN DEFAULT 1 NOT NULL, criado_em DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL)",
]


@pytest.fixture(scope="function")
def db_session() -> Session:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    with engine.execution_options(schema_translate_map=_SCHEMA_TRANSLATE).connect() as conn:
        for sql in _CREATE_TABLES_SQL:
            conn.execute(text(sql))
        conn.execute(text("INSERT INTO usuarios (id, nome, nome_completo) VALUES (1, 'Admin', 'Admin User')"))
        conn.execute(text("INSERT INTO usuarios (id, nome, nome_completo) VALUES (2, 'User2', 'User Two')"))
        conn.execute(text("INSERT INTO usuarios (id, nome, nome_completo) VALUES (3, 'User3', 'User Three')"))
        conn.commit()

    TestingSession = sessionmaker(
        bind=engine.execution_options(schema_translate_map=_SCHEMA_TRANSLATE),
        autocommit=False,
        autoflush=False,
    )
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        with engine.execution_options(schema_translate_map=_SCHEMA_TRANSLATE).connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS registros_tarefas"))
            conn.execute(text("DROP TABLE IF EXISTS tarefas"))
            conn.execute(text("DROP TABLE IF EXISTS recursos"))
            conn.execute(text("DROP TABLE IF EXISTS projetos"))
            conn.execute(text("DROP TABLE IF EXISTS usuarios"))
            conn.commit()


@pytest.fixture
def projeto_repository(db_session: Session):
    from app.modules.gestao_projetos.repositories.projeto_repository import ProjetoRepository
    return ProjetoRepository(db_session)


@pytest.fixture
def tarefa_repository(db_session: Session):
    from app.modules.gestao_projetos.repositories.tarefa_repository import TarefaRepository
    return TarefaRepository(db_session)


@pytest.fixture
def registro_repository(db_session: Session):
    from app.modules.gestao_projetos.repositories.registro_repository import RegistroRepository
    return RegistroRepository(db_session)


@pytest.fixture
def recurso_repository(db_session: Session):
    from app.modules.gestao_projetos.repositories.recurso_repository import RecursoRepository
    return RecursoRepository(db_session)


@pytest.fixture
def projeto_service(projeto_repository):
    from app.modules.gestao_projetos.services.projeto_service import ProjetoService
    return ProjetoService(projeto_repository)


@pytest.fixture
def tarefa_service(tarefa_repository):
    from app.modules.gestao_projetos.services.tarefa_service import TarefaService
    return TarefaService(tarefa_repository)


@pytest.fixture
def registro_service(registro_repository):
    from app.modules.gestao_projetos.services.registro_service import RegistroService
    return RegistroService(registro_repository)


@pytest.fixture
def recurso_service(recurso_repository):
    from app.modules.gestao_projetos.services.recurso_service import RecursoService
    return RecursoService(recurso_repository)


@pytest.fixture
def repository(projeto_repository):
    return projeto_repository


@pytest.fixture
def service(projeto_service):
    return projeto_service
