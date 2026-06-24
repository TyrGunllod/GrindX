"""
Fixtures para testes do módulo {entity_name}.

Requer a variável de ambiente GRINDX_PACKAGES apontando para o diretório
packages/ do projeto GrindX (ex: D:\\_Projetos\\GrindX\\packages).
"""

import importlib.util
import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

GRINDX_PACKAGES = os.environ.get(
    "GRINDX_PACKAGES",
    str(Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent / "GrindX" / "packages"),
)
GRINDX_API = str(Path(GRINDX_PACKAGES).parent / "apps" / "api-postgres")
LOCAL_MODULES = str(Path(__file__).resolve().parent.parent.parent)

for p in [GRINDX_PACKAGES, GRINDX_API, LOCAL_MODULES]:
    if p not in sys.path:
        sys.path.insert(0, p)

import app  # noqa: E402
import app.modules  # noqa: E402

_local_pkg = Path(LOCAL_MODULES) / "{module_name}"
_spec = importlib.util.spec_from_file_location(
    "app.modules.{module_name}",
    str(_local_pkg / "__init__.py"),
    submodule_search_locations=[str(_local_pkg)],
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["app.modules.{module_name}"] = _mod
_spec.loader.exec_module(_mod)

from app.modules.iam.base import IamBase  # noqa: E402

_SCHEMA_TRANSLATE = {"iam": None, "portal": None, "catalogo": None, "org": None}
_all_metadata = IamBase.metadata


@pytest.fixture(scope="function")
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    with engine.execution_options(schema_translate_map=_SCHEMA_TRANSLATE).connect() as conn:
        _all_metadata.create_all(conn)

    TestingSession = sessionmaker(bind=engine.execution_options(schema_translate_map=_SCHEMA_TRANSLATE))
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        with engine.execution_options(schema_translate_map=_SCHEMA_TRANSLATE).connect() as conn:
            _all_metadata.drop_all(conn)


@pytest.fixture
def repository(db_session: Session):
    from app.modules.{module_name}.repositories.{module_name}_repository import {entity_name}Repository
    return {entity_name}Repository(db_session)


@pytest.fixture
def service(repository):
    from app.modules.{module_name}.services.{module_name}_service import {entity_name}Service
    return {entity_name}Service(repository)
