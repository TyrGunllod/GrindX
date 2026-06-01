"""Tests for register_router(), register_alembic_import(), and register_dependency() in import_module.py."""

import tempfile
import textwrap
from pathlib import Path

import pytest

import scripts.import_module as import_module
from scripts.import_module import (
    register_alembic_import,
    register_dependency,
    register_router,
)


MAIN_PY_CONTENT = '''\
from app.routers.health_router import router as health_router
from app.routers.usuario_router import router as usuario_router

app.include_router(health_router)
app.include_router(usuario_router)
'''

ALEMBIC_ENV_CONTENT = '''\
from app.modules.iam.models.usuario import Usuario  # noqa: F401
from app.modules.org.models.empresa import Empresa  # noqa: F401
from app.modules.portal.models.portal import Aba, Modulo  # noqa: F401
'''

DEPENDENCIES_CONTENT = '''\
from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth.service import AuthService
from app.database import get_db


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Factory para o AuthService."""
    return AuthService(db)


# --- Versões vinculadas das permissões ---


def require_role(*roles_permitidas: str):
    pass
'''


@pytest.fixture
def main_py(tmp_path):
    f = tmp_path / "main.py"
    f.write_text(MAIN_PY_CONTENT, encoding="utf-8")
    return f


@pytest.fixture
def env_py(tmp_path):
    f = tmp_path / "env.py"
    f.write_text(ALEMBIC_ENV_CONTENT, encoding="utf-8")
    return f


@pytest.fixture
def deps_py(tmp_path):
    f = tmp_path / "dependencies.py"
    f.write_text(DEPENDENCIES_CONTENT, encoding="utf-8")
    return f


@pytest.fixture
def import_module():
    import scripts.import_module as mod

    return mod


class TestRegisterRouter:
    def test_generates_correct_import_path(self, main_py):
        manifest = {"module_name": "projetos"}
        register_router(manifest, force=False, main_py=main_py)

        content = main_py.read_text(encoding="utf-8")
        assert (
            "from app.modules.projetos.routers.projetos_router import router as projetos_router"
            in content
        )
        assert "app.include_router(projetos_router)" in content

    def test_generates_correct_import_path_different_module(self, main_py):
        manifest = {"module_name": "financeiro"}
        register_router(manifest, force=False, main_py=main_py)

        content = main_py.read_text(encoding="utf-8")
        assert (
            "from app.modules.financeiro.routers.financeiro_router import router as financeiro_router"
            in content
        )
        assert "app.include_router(financeiro_router)" in content

    def test_old_style_import_path_not_generated(self, main_py):
        manifest = {"module_name": "projetos"}
        register_router(manifest, force=False, main_py=main_py)

        content = main_py.read_text(encoding="utf-8")
        assert (
            "from app.routers.projetos_router import router as projetos_router"
            not in content
        )

    def test_inserts_after_last_router_import(self, main_py):
        manifest = {"module_name": "projetos"}
        register_router(manifest, force=False, main_py=main_py)

        lines = main_py.read_text(encoding="utf-8").splitlines()
        import_lines = [i for i, l in enumerate(lines) if "from app." in l and "import router as" in l]
        assert import_lines[-1] == 2
        assert "from app.modules.projetos" in lines[2]

    def test_inserts_include_router_after_last_one(self, main_py):
        manifest = {"module_name": "projetos"}
        register_router(manifest, force=False, main_py=main_py)

        lines = main_py.read_text(encoding="utf-8").splitlines()
        include_lines = [i for i, l in enumerate(lines) if "app.include_router(" in l]
        assert "app.include_router(projetos_router)" in lines[include_lines[-1]]

    def test_idempotent_when_already_registered(self, main_py):
        manifest = {"module_name": "projetos"}
        register_router(manifest, force=False, main_py=main_py)
        register_router(manifest, force=False, main_py=main_py)

        content = main_py.read_text(encoding="utf-8")
        assert content.count("from app.modules.projetos.routers.projetos_router import router as projetos_router") == 1
        assert content.count("app.include_router(projetos_router)") == 1

    def test_raises_when_partial_and_not_force(self, main_py):
        manifest = {"module_name": "projetos"}
        main_py.write_text(
            MAIN_PY_CONTENT
            + "from app.modules.projetos.routers.projetos_router import router as projetos_router\n",
            encoding="utf-8",
        )
        with pytest.raises(FileExistsError, match="parcialmente"):
            register_router(manifest, force=False, main_py=main_py)

    def test_force_overwrites_partial(self, main_py):
        manifest = {"module_name": "projetos"}
        main_py.write_text(
            MAIN_PY_CONTENT
            + "from app.modules.projetos.routers.projetos_router import router as projetos_router\n",
            encoding="utf-8",
        )
        register_router(manifest, force=True, main_py=main_py)

        content = main_py.read_text(encoding="utf-8")
        assert "app.include_router(projetos_router)" in content

    def test_levanta_erro_se_main_py_sem_imports(self, tmp_path):
        """Se main.py não tem imports de router, levanta erro."""
        main_py = tmp_path / "main.py"
        main_py.write_text("# empty main.py\n", encoding="utf-8")

        manifest = {"module_name": "projeto"}
        with pytest.raises(RuntimeError, match="Não foi possível encontrar"):
            register_router(manifest, main_py=main_py, force=False)

    def test_matches_new_style_imports_for_position(self, tmp_path):
        """When main.py already has a new-style module import, find the last one."""
        content = (
            "from app.routers.health_router import router as health_router\n"
            "from app.modules.iam.routers.iam_router import router as iam_router\n"
            "from app.modules.org.routers.org_router import router as org_router\n"
            "\n"
            "app.include_router(health_router)\n"
            "app.include_router(iam_router)\n"
            "app.include_router(org_router)\n"
        )
        main_py = tmp_path / "main.py"
        main_py.write_text(content, encoding="utf-8")

        manifest = {"module_name": "projetos"}
        register_router(manifest, force=False, main_py=main_py)

        result = main_py.read_text(encoding="utf-8")
        lines = result.splitlines()
        import_lines = [i for i, l in enumerate(lines) if "from app." in l and "import router as" in l]
        assert "from app.modules.projetos.routers" in lines[import_lines[-1]]


class TestRegisterAlembicImport:
    def test_adds_import_after_portal_marker(self, env_py):
        manifest = {"module_name": "projetos", "entity_name": "Projeto"}
        register_alembic_import(manifest, force=False, env_py=env_py)

        content = env_py.read_text(encoding="utf-8")
        assert (
            "from app.modules.projetos.models.projetos import Projeto  # noqa: F401"
            in content
        )

    def test_import_after_portal_line(self, env_py):
        manifest = {"module_name": "projetos", "entity_name": "Projeto"}
        register_alembic_import(manifest, force=False, env_py=env_py)

        lines = env_py.read_text(encoding="utf-8").splitlines()
        portal_idx = None
        projetos_idx = None
        for i, l in enumerate(lines):
            if "from app.modules.portal" in l:
                portal_idx = i
            if "from app.modules.projetos" in l:
                projetos_idx = i
        assert portal_idx is not None
        assert projetos_idx is not None
        assert projetos_idx == portal_idx + 1

    def test_idempotent_when_already_registered(self, env_py):
        manifest = {"module_name": "projetos", "entity_name": "Projeto"}
        register_alembic_import(manifest, force=False, env_py=env_py)
        register_alembic_import(manifest, force=False, env_py=env_py)

        content = env_py.read_text(encoding="utf-8")
        assert content.count("from app.modules.projetos.models.projetos import Projeto") == 1

    def test_correct_import_for_different_module(self, env_py):
        manifest = {"module_name": "financeiro", "entity_name": "Lancamento"}
        register_alembic_import(manifest, force=False, env_py=env_py)

        content = env_py.read_text(encoding="utf-8")
        assert (
            "from app.modules.financeiro.models.financeiro import Lancamento  # noqa: F401"
            in content
        )


class TestRegisterDependency:
    def test_adds_factory_before_marker(self, deps_py):
        manifest = {"module_name": "projetos", "entity_name": "Projeto"}
        register_dependency(manifest, force=False, deps_py=deps_py)

        content = deps_py.read_text(encoding="utf-8")
        assert "def get_projetos_service(db: Session = Depends(get_db)) -> ProjetoService:" in content
        assert "# --- Versões vinculadas das permissões ---" in content

        marker_idx = content.index("# --- Versões vinculadas das permissões ---")
        factory_idx = content.index("def get_projetos_service")
        assert factory_idx < marker_idx

    def test_generates_correct_imports(self, deps_py):
        manifest = {"module_name": "projetos", "entity_name": "Projeto"}
        register_dependency(manifest, force=False, deps_py=deps_py)

        content = deps_py.read_text(encoding="utf-8")
        assert "from app.modules.projetos.repositories.projetos_repository import ProjetoRepository" in content
        assert "from app.modules.projetos.services.projetos_service import ProjetoService" in content

    def test_generates_correct_factory_body(self, deps_py):
        manifest = {"module_name": "projetos", "entity_name": "Projeto"}
        register_dependency(manifest, force=False, deps_py=deps_py)

        content = deps_py.read_text(encoding="utf-8")
        assert "repository = ProjetoRepository(db)" in content
        assert "return ProjetoService(repository)" in content

    def test_idempotent_when_already_registered(self, deps_py):
        manifest = {"module_name": "projetos", "entity_name": "Projeto"}
        register_dependency(manifest, force=False, deps_py=deps_py)
        register_dependency(manifest, force=False, deps_py=deps_py)

        content = deps_py.read_text(encoding="utf-8")
        assert content.count("def get_projetos_service") == 1

    def test_different_module(self, deps_py):
        manifest = {"module_name": "financeiro", "entity_name": "Lancamento"}
        register_dependency(manifest, force=False, deps_py=deps_py)

        content = deps_py.read_text(encoding="utf-8")
        assert "from app.modules.financeiro.repositories.financeiro_repository import LancamentoRepository" in content
        assert "from app.modules.financeiro.services.financeiro_service import LancamentoService" in content
        assert "def get_financeiro_service(db: Session = Depends(get_db)) -> LancamentoService:" in content

    def test_raises_when_partial_and_not_force(self, deps_py):
        manifest = {"module_name": "projetos", "entity_name": "Projeto"}
        deps_py.write_text(
            DEPENDENCIES_CONTENT
            + "def get_projetos_service(db: Session = Depends(get_db)) -> ProjetoService:\n",
            encoding="utf-8",
        )
        with pytest.raises(FileExistsError, match="parcialmente"):
            register_dependency(manifest, force=False, deps_py=deps_py)

    def test_force_overwrites_partial(self, deps_py):
        manifest = {"module_name": "projetos", "entity_name": "Projeto"}
        deps_py.write_text(
            DEPENDENCIES_CONTENT
            + "def get_projetos_service(db: Session = Depends(get_db)) -> ProjetoService:\n",
            encoding="utf-8",
        )
        register_dependency(manifest, force=True, deps_py=deps_py)

        content = deps_py.read_text(encoding="utf-8")
        assert "repository = ProjetoRepository(db)" in content

    def test_raises_when_no_marker(self, tmp_path):
        deps_py = tmp_path / "dependencies.py"
        deps_py.write_text("# empty\n", encoding="utf-8")

        manifest = {"module_name": "projetos", "entity_name": "Projeto"}
        with pytest.raises(RuntimeError, match="Marker .* não encontrado"):
            register_dependency(manifest, force=False, deps_py=deps_py)

    def test_factory_inserted_before_marker_in_real_file(self, deps_py):
        """Verify the factory is positioned correctly relative to marker."""
        manifest = {"module_name": "projetos", "entity_name": "Projeto"}
        register_dependency(manifest, force=False, deps_py=deps_py)

        lines = deps_py.read_text(encoding="utf-8").splitlines()
        marker_idx = None
        factory_idx = None
        for i, line in enumerate(lines):
            if "# --- Versões vinculadas das permissões ---" in line:
                marker_idx = i
            if "def get_projetos_service" in line:
                factory_idx = i

        assert marker_idx is not None
        assert factory_idx is not None
        assert factory_idx < marker_idx


class TestImportFlow:
    def test_fluxo_completo_register_router_e_dependency(self, import_module, tmp_path):
        """Simula o fluxo: register_router + register_dependency + register_alembic_import."""
        main_py = tmp_path / "main.py"
        main_py.write_text(textwrap.dedent("""\
            from app.routers.health_router import router as health_router
            app.include_router(health_router)
        """), encoding="utf-8")

        deps_py = tmp_path / "dependencies.py"
        deps_py.write_text(textwrap.dedent("""\
            # --- Versões vinculadas das permissões ---
        """), encoding="utf-8")

        env_py = tmp_path / "env.py"
        env_py.write_text(textwrap.dedent("""\
            from app.modules.portal.models.portal import Aba, Modulo  # noqa: F401
        """), encoding="utf-8")

        manifest = {
            "module_name": "projeto",
            "entity_name": "Projeto",
        }

        # 1. Register router
        import_module.register_router(manifest, main_py=main_py, force=False)
        content_main = main_py.read_text()
        assert "from app.modules.projeto.routers.projeto_router import router as projeto_router" in content_main
        assert "app.include_router(projeto_router)" in content_main

        # 2. Register dependency
        import_module.register_dependency(manifest, force=False, deps_py=deps_py)
        content_deps = deps_py.read_text()
        assert "def get_projeto_service(" in content_deps

        # 3. Register alembic import
        import_module.register_alembic_import(manifest, force=False, env_py=env_py)
        content_env = env_py.read_text()
        assert "from app.modules.projeto.models.projeto import Projeto  # noqa: F401" in content_env
