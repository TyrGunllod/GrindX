"""Tests for register_router(), register_alembic_import(), and register_dependency() in import_module.py."""

import textwrap
from unittest.mock import patch

import pytest

import scripts.import_module as import_module
from scripts.import_module import (
    _snake_to_pascal,
    register_alembic_import,
    register_dependency,
    register_router,
)

MAIN_PY_CONTENT = """\
from app.routers.health_router import router as health_router
from app.routers.usuario_router import router as usuario_router

app.include_router(health_router)
app.include_router(usuario_router)
"""

ALEMBIC_ENV_CONTENT = """\
from app.modules.iam.models.usuario import Usuario  # noqa: F401
from app.modules.org.models.empresa import Empresa  # noqa: F401
from app.modules.portal.models.portal import Aba, Modulo  # noqa: F401
"""

DEPENDENCIES_CONTENT = """\
from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth.service import AuthService
from app.database import get_db


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    \"\"\"Factory para o AuthService.\"\"\"
    return AuthService(db)


# --- Versões vinculadas das permissões ---


def require_role(*roles_permitidas: str):
    pass
"""


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
def import_mod():
    return import_module


def _mock_api_dir(
    tmp_path,
    module_name,
    router_files=None,
    repo_files=None,
    svc_files=None,
    model_files=None,
):
    """Create mock directory structure for a module."""
    api_dir = tmp_path / "apps" / "api-postgres"
    module_dir = api_dir / "app" / "modules" / module_name

    if router_files:
        routers_dir = module_dir / "routers"
        routers_dir.mkdir(parents=True)
        for name in router_files:
            (routers_dir / f"{name}.py").write_text(
                f"router = None  # {name}", encoding="utf-8"
            )

    if repo_files:
        repos_dir = module_dir / "repositories"
        repos_dir.mkdir(parents=True)
        for name in repo_files:
            entity = name.replace("_repository", "")
            (repos_dir / f"{name}.py").write_text(
                f"class {_snake_to_pascal(entity)}Repository: pass", encoding="utf-8"
            )

    if svc_files:
        svcs_dir = module_dir / "services"
        svcs_dir.mkdir(parents=True)
        for name in svc_files:
            entity = name.replace("_service", "")
            (svcs_dir / f"{name}.py").write_text(
                f"class {_snake_to_pascal(entity)}Service: pass", encoding="utf-8"
            )

    if model_files:
        models_dir = module_dir / "models"
        models_dir.mkdir(parents=True)
        for name in model_files:
            (models_dir / f"{name}.py").write_text(
                f"class {_snake_to_pascal(name)}: pass", encoding="utf-8"
            )

    return api_dir


class TestRegisterRouter:
    def test_generates_correct_import_path(self, main_py, tmp_path):
        _mock_api_dir(tmp_path, "projetos", router_files=["projetos_router"])
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "projetos"}
            register_router(manifest, force=False, main_py=main_py)

        content = main_py.read_text(encoding="utf-8")
        assert (
            "from app.modules.projetos.routers.projetos_router import router as projetos_router"
            in content
        )
        assert "app.include_router(projetos_router)" in content

    def test_generates_correct_import_path_different_module(self, main_py, tmp_path):
        _mock_api_dir(tmp_path, "financeiro", router_files=["financeiro_router"])
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "financeiro"}
            register_router(manifest, force=False, main_py=main_py)

        content = main_py.read_text(encoding="utf-8")
        assert (
            "from app.modules.financeiro.routers.financeiro_router import router as financeiro_router"
            in content
        )
        assert "app.include_router(financeiro_router)" in content

    def test_multiple_routers(self, main_py, tmp_path):
        _mock_api_dir(
            tmp_path, "projetos", router_files=["projeto_router", "tarefa_router"]
        )
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "projetos"}
            register_router(manifest, force=False, main_py=main_py)

        content = main_py.read_text(encoding="utf-8")
        assert (
            "from app.modules.projetos.routers.projeto_router import router as projeto_router"
            in content
        )
        assert (
            "from app.modules.projetos.routers.tarefa_router import router as tarefa_router"
            in content
        )
        assert "app.include_router(projeto_router)" in content
        assert "app.include_router(tarefa_router)" in content

    def test_no_routers_dir_returns_early(self, main_py, tmp_path):
        _mock_api_dir(tmp_path, "projetos")
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "projetos"}
            register_router(manifest, force=False, main_py=main_py)

        content = main_py.read_text(encoding="utf-8")
        assert content == MAIN_PY_CONTENT

    def test_inserts_after_last_router_import(self, main_py, tmp_path):
        _mock_api_dir(tmp_path, "projetos", router_files=["projetos_router"])
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "projetos"}
            register_router(manifest, force=False, main_py=main_py)

        lines = main_py.read_text(encoding="utf-8").splitlines()
        import_lines = [
            i
            for i, line in enumerate(lines)
            if "from app." in line and "import router as" in line
        ]
        assert import_lines[-1] == 2
        assert "from app.modules.projetos" in lines[2]

    def test_inserts_include_router_after_last_one(self, main_py, tmp_path):
        _mock_api_dir(tmp_path, "projetos", router_files=["projetos_router"])
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "projetos"}
            register_router(manifest, force=False, main_py=main_py)

        lines = main_py.read_text(encoding="utf-8").splitlines()
        include_lines = [
            i for i, line in enumerate(lines) if "app.include_router(" in line
        ]
        assert "app.include_router(projetos_router)" in lines[include_lines[-1]]

    def test_idempotent_when_already_registered(self, main_py, tmp_path):
        _mock_api_dir(tmp_path, "projetos", router_files=["projetos_router"])
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "projetos"}
            register_router(manifest, force=False, main_py=main_py)
            register_router(manifest, force=False, main_py=main_py)

        content = main_py.read_text(encoding="utf-8")
        assert (
            content.count(
                "from app.modules.projetos.routers.projetos_router import router as projetos_router"
            )
            == 1
        )
        assert content.count("app.include_router(projetos_router)") == 1

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

        _mock_api_dir(tmp_path, "projetos", router_files=["projetos_router"])
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "projetos"}
            register_router(manifest, force=False, main_py=main_py)

        result = main_py.read_text(encoding="utf-8")
        lines = result.splitlines()
        import_lines = [
            i
            for i, line in enumerate(lines)
            if "from app." in line and "import router as" in line
        ]
        assert "from app.modules.projetos.routers" in lines[import_lines[-1]]


class TestRegisterAlembicImport:
    def test_adds_import_after_portal_marker(self, env_py, tmp_path):
        _mock_api_dir(tmp_path, "projetos", model_files=["projetos"])
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "projetos"}
            register_alembic_import(manifest, force=False, env_py=env_py)

        content = env_py.read_text(encoding="utf-8")
        assert "from app.modules.projetos.models.projetos import" in content

    def test_import_after_portal_line(self, env_py, tmp_path):
        _mock_api_dir(tmp_path, "projetos", model_files=["projetos"])
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "projetos"}
            register_alembic_import(manifest, force=False, env_py=env_py)

        lines = env_py.read_text(encoding="utf-8").splitlines()
        portal_idx = None
        projetos_idx = None
        for i, line in enumerate(lines):
            if "from app.modules.portal" in line:
                portal_idx = i
            if "from app.modules.projetos" in line:
                projetos_idx = i
        assert portal_idx is not None
        assert projetos_idx is not None
        assert projetos_idx == portal_idx + 1

    def test_idempotent_when_already_registered(self, env_py, tmp_path):
        _mock_api_dir(tmp_path, "projetos", model_files=["projetos"])
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "projetos"}
            register_alembic_import(manifest, force=False, env_py=env_py)
            register_alembic_import(manifest, force=False, env_py=env_py)

        content = env_py.read_text(encoding="utf-8")
        assert content.count("from app.modules.projetos.models.projetos") == 1

    def test_correct_import_for_different_module(self, env_py, tmp_path):
        _mock_api_dir(tmp_path, "financeiro", model_files=["lancamento"])
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "financeiro"}
            register_alembic_import(manifest, force=False, env_py=env_py)

        content = env_py.read_text(encoding="utf-8")
        assert "from app.modules.financeiro.models.lancamento import" in content

    def test_multiple_models(self, env_py, tmp_path):
        _mock_api_dir(
            tmp_path, "projetos", model_files=["projeto", "tarefa", "recurso"]
        )
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "projetos"}
            register_alembic_import(manifest, force=False, env_py=env_py)

        content = env_py.read_text(encoding="utf-8")
        assert "from app.modules.projetos.models.projeto import" in content
        assert "from app.modules.projetos.models.tarefa import" in content
        assert "from app.modules.projetos.models.recurso import" in content

    def test_no_models_dir_returns_early(self, env_py, tmp_path):
        _mock_api_dir(tmp_path, "projetos")
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "projetos"}
            register_alembic_import(manifest, force=False, env_py=env_py)

        content = env_py.read_text(encoding="utf-8")
        assert content == ALEMBIC_ENV_CONTENT


class TestRegisterDependency:
    def test_adds_factory_before_marker(self, deps_py, tmp_path):
        _mock_api_dir(
            tmp_path,
            "projetos",
            repo_files=["projetos_repository"],
            svc_files=["projetos_service"],
        )
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "projetos"}
            register_dependency(manifest, force=False, deps_py=deps_py)

        content = deps_py.read_text(encoding="utf-8")
        # When module_name == entity, factory is get_{module}_service (not get_{module}_{entity}_service)
        assert "def get_projetos_service" in content
        assert "# --- Versões vinculadas das permissões ---" in content

        marker_idx = content.index("# --- Versões vinculadas das permissões ---")
        factory_idx = content.index("def get_projetos_service")
        assert factory_idx < marker_idx

    def test_generates_correct_imports(self, deps_py, tmp_path):
        _mock_api_dir(
            tmp_path,
            "projetos",
            repo_files=["projetos_repository"],
            svc_files=["projetos_service"],
        )
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "projetos"}
            register_dependency(manifest, force=False, deps_py=deps_py)

        content = deps_py.read_text(encoding="utf-8")
        assert (
            "from app.modules.projetos.repositories.projetos_repository import ProjetosRepository"
            in content
        )
        assert (
            "from app.modules.projetos.services.projetos_service import ProjetosService"
            in content
        )

    def test_generates_correct_factory_body(self, deps_py, tmp_path):
        _mock_api_dir(
            tmp_path,
            "projetos",
            repo_files=["projetos_repository"],
            svc_files=["projetos_service"],
        )
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "projetos"}
            register_dependency(manifest, force=False, deps_py=deps_py)

        content = deps_py.read_text(encoding="utf-8")
        assert "repository = ProjetosRepository(db)" in content
        assert "return ProjetosService(repository)" in content

    def test_idempotent_when_already_registered(self, deps_py, tmp_path):
        _mock_api_dir(
            tmp_path,
            "projetos",
            repo_files=["projetos_repository"],
            svc_files=["projetos_service"],
        )
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "projetos"}
            register_dependency(manifest, force=False, deps_py=deps_py)
            register_dependency(manifest, force=False, deps_py=deps_py)

        content = deps_py.read_text(encoding="utf-8")
        # When module_name == entity, factory is get_{module}_service
        assert content.count("def get_projetos_service") == 1

    def test_different_module(self, deps_py, tmp_path):
        _mock_api_dir(
            tmp_path,
            "financeiro",
            repo_files=["lancamento_repository"],
            svc_files=["lancamento_service"],
        )
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "financeiro"}
            register_dependency(manifest, force=False, deps_py=deps_py)

        content = deps_py.read_text(encoding="utf-8")
        assert (
            "from app.modules.financeiro.repositories.lancamento_repository import LancamentoRepository"
            in content
        )
        assert (
            "from app.modules.financeiro.services.lancamento_service import LancamentoService"
            in content
        )

    def test_no_repos_dir_returns_early(self, deps_py, tmp_path):
        _mock_api_dir(tmp_path, "projetos")
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "projetos"}
            register_dependency(manifest, force=False, deps_py=deps_py)

        content = deps_py.read_text(encoding="utf-8")
        assert content == DEPENDENCIES_CONTENT

    def test_raises_when_no_marker(self, tmp_path):
        deps_py = tmp_path / "dependencies.py"
        deps_py.write_text("# empty\n", encoding="utf-8")

        _mock_api_dir(
            tmp_path,
            "projetos",
            repo_files=["projetos_repository"],
            svc_files=["projetos_service"],
        )
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "projetos"}
            register_dependency(manifest, force=False, deps_py=deps_py)

        content = deps_py.read_text(encoding="utf-8")
        assert content == "# empty\n"

    def test_factory_inserted_before_marker_in_real_file(self, deps_py, tmp_path):
        """Verify the factory is positioned correctly relative to marker."""
        _mock_api_dir(
            tmp_path,
            "projetos",
            repo_files=["projetos_repository"],
            svc_files=["projetos_service"],
        )
        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {"module_name": "projetos"}
            register_dependency(manifest, force=False, deps_py=deps_py)

        lines = deps_py.read_text(encoding="utf-8").splitlines()
        marker_idx = None
        factory_idx = None
        for i, line in enumerate(lines):
            if "# --- Versões vinculadas das permissões ---" in line:
                marker_idx = i
            if "def get_projetos_" in line:
                factory_idx = i

        assert marker_idx is not None
        assert factory_idx is not None
        assert factory_idx < marker_idx


class TestImportFlow:
    def test_fluxo_completo_register_router_e_dependency(self, import_mod, tmp_path):
        """Simula o fluxo: register_router + register_dependency + register_alembic_import."""
        main_py = tmp_path / "main.py"
        main_py.write_text(
            textwrap.dedent("""\
            from app.routers.health_router import router as health_router
            app.include_router(health_router)
        """),
            encoding="utf-8",
        )

        deps_py = tmp_path / "dependencies.py"
        deps_py.write_text(
            textwrap.dedent("""\
            # --- Versões vinculadas das permissões ---
        """),
            encoding="utf-8",
        )

        env_py = tmp_path / "env.py"
        env_py.write_text(
            textwrap.dedent("""\
            from app.modules.portal.models.portal import Aba, Modulo  # noqa: F401
        """),
            encoding="utf-8",
        )

        _mock_api_dir(
            tmp_path,
            "projeto",
            router_files=["projeto_router"],
            repo_files=["projeto_repository"],
            svc_files=["projeto_service"],
            model_files=["projeto"],
        )

        with patch("scripts.import_module._get_monorepo_root", return_value=tmp_path):
            manifest = {
                "module_name": "projeto",
                "entity_name": "Projeto",
            }

            # 1. Register router
            import_mod.register_router(manifest, main_py=main_py, force=False)
            content_main = main_py.read_text()
            assert (
                "from app.modules.projeto.routers.projeto_router import router as projeto_router"
                in content_main
            )
            assert "app.include_router(projeto_router)" in content_main

            # 2. Register dependency
            import_mod.register_dependency(manifest, force=False, deps_py=deps_py)
            content_deps = deps_py.read_text()
            # When module_name == entity, factory is get_{module}_service
            assert "def get_projeto_service(" in content_deps

            # 3. Register alembic import
            import_mod.register_alembic_import(manifest, force=False, env_py=env_py)
            content_env = env_py.read_text()
            assert "from app.modules.projeto.models.projeto import" in content_env
