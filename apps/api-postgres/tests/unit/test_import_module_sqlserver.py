"""Tests for sqlserver module import support in import_module.py."""

import json

import scripts.import_module as import_module


def test_validate_manifest_accepts_manifest_without_target_api(tmp_path):
    """module.json sem target_api deve ser aceito (compatibilidade reversa)."""
    manifest = {
        "module_name": "test_mod",
        "entity_name": "Test",
        "schema_name": "org",
        "route_prefix": "/v1/test",
        "menu_label": "Teste",
        "frontend_url": "modules/test/index.html",
    }
    manifest_path = tmp_path / "module.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    result = import_module.validate_manifest(tmp_path)
    assert result["module_name"] == "test_mod"
    assert "target_api" not in result


def test_validate_manifest_sqlserver_target_api(tmp_path):
    """module.json com target_api='sqlserver' deve ser aceito."""
    manifest = {
        "module_name": "custo",
        "entity_name": "CustoProduto",
        "schema_name": "org",
        "route_prefix": "/v1/produtos/custos",
        "menu_label": "Custos",
        "target_api": "sqlserver",
        "frontend_tabs": [{"name": "Custos", "url": "modules/custos/index.html"}],
    }
    manifest_path = tmp_path / "module.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    result = import_module.validate_manifest(tmp_path)
    assert result["target_api"] == "sqlserver"


def test_get_sqlserver_api_dir_default():
    """_get_sqlserver_api_dir() deve retornar o path relativo ao monorepo root."""
    d = import_module._get_sqlserver_api_dir()
    assert d.name == "api-sqlserver"
    assert d.parent.name == "apps"


MAIN_PY_SQLSERVER_CONTENT = """\
from app.routers.health_router import router as health_router

app.include_router(health_router)
"""


def test_register_router_sqlserver_adds_import_and_include(tmp_path):
    """Deve adicionar import do router e app.include_router() no main.py do sqlserver."""
    manifest = {
        "module_name": "custo",
        "entity_name": "CustoProduto",
        "schema_name": "org",
        "route_prefix": "/v1/produtos/custos",
        "menu_label": "Custos",
        "target_api": "sqlserver",
        "frontend_tabs": [{"name": "Custos", "url": "modules/custos/index.html"}],
    }

    modules_dir = tmp_path / "app" / "modules" / "custo" / "routers"
    modules_dir.mkdir(parents=True)
    (modules_dir / "__init__.py").write_text("", encoding="utf-8")
    router_file = modules_dir / "custo_produto_router.py"
    router_file.write_text("# router code", encoding="utf-8")

    main_py = tmp_path / "main.py"
    main_py.write_text(MAIN_PY_SQLSERVER_CONTENT, encoding="utf-8")

    import_module.register_router_sqlserver(manifest, force=True, main_py=main_py)
    content = main_py.read_text(encoding="utf-8")
    assert "from app.modules.custo.routers.custo_produto_router import router as custo_produto_router" in content
    assert "app.include_router(custo_produto_router)" in content


def test_register_router_sqlserver_idempotent(tmp_path):
    """Chamar duas vezes nao deve duplicar entradas."""
    manifest = {
        "module_name": "custo",
        "entity_name": "CustoProduto",
        "schema_name": "org",
        "route_prefix": "/v1/produtos/custos",
        "menu_label": "Custos",
        "target_api": "sqlserver",
        "frontend_tabs": [{"name": "Custos", "url": "modules/custos/index.html"}],
    }

    modules_dir = tmp_path / "app" / "modules" / "custo" / "routers"
    modules_dir.mkdir(parents=True)
    (modules_dir / "__init__.py").write_text("", encoding="utf-8")
    (modules_dir / "custo_produto_router.py").write_text("#", encoding="utf-8")

    main_py = tmp_path / "main.py"
    main_py.write_text(MAIN_PY_SQLSERVER_CONTENT, encoding="utf-8")

    import_module.register_router_sqlserver(manifest, force=True, main_py=main_py)
    import_module.register_router_sqlserver(manifest, force=True, main_py=main_py)
    content = main_py.read_text(encoding="utf-8")
    assert (
        content.count(
            "from app.modules.custo.routers.custo_produto_router import router as custo_produto_router"
        )
        == 1
    )
    assert content.count("app.include_router(custo_produto_router)") == 1


def test_register_router_sqlserver_no_router_dir(tmp_path):
    """Sem diretorio de routers, nao deve modificar main.py."""
    manifest = {
        "module_name": "mod_sem_router",
        "entity_name": "Mod",
        "schema_name": "org",
        "route_prefix": "/v1/mod",
        "menu_label": "Mod",
        "target_api": "sqlserver",
        "frontend_tabs": [{"name": "Mod", "url": "modules/mod/index.html"}],
    }
    main_py = tmp_path / "main.py"
    main_py.write_text(MAIN_PY_SQLSERVER_CONTENT, encoding="utf-8")
    original = main_py.read_text(encoding="utf-8")
    import_module.register_router_sqlserver(manifest, force=True, main_py=main_py)
    assert main_py.read_text(encoding="utf-8") == original
