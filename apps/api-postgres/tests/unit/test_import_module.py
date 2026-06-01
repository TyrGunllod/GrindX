"""Tests for register_router() and register_alembic_import() in import_module.py."""

import tempfile
from pathlib import Path

import pytest

from scripts.import_module import register_alembic_import, register_router


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
