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
