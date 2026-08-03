"""Tests for frontend-only module support in import_module.py."""

import json
from unittest.mock import patch

import pytest

import scripts.import_module as import_module


def _write_manifest(tmp_path, **overrides):
    manifest = {
        "module_name": "pop_viz",
        "entity_name": "PopViz",
        "menu_label": "Visualizador POP",
        "frontend_tabs": [
            {"name": "Visualizador POP", "url": "modules/pop_viz/index.html"}
        ],
    }
    manifest.update(overrides)
    (tmp_path / "module.json").write_text(json.dumps(manifest), encoding="utf-8")


def test_validate_manifest_accepts_frontend_only_without_schema_route(tmp_path):
    _write_manifest(tmp_path, frontend_only=True)

    result = import_module.validate_manifest(tmp_path)

    assert result["module_name"] == "pop_viz"
    assert result["frontend_only"] is True


def test_validate_manifest_rejects_without_flag_and_without_schema_route(tmp_path):
    _write_manifest(tmp_path)

    with pytest.raises(ValueError) as exc:
        import_module.validate_manifest(tmp_path)

    message = str(exc.value)
    assert "schema_name" in message
    assert "route_prefix" in message


@patch("scripts.import_module._get_monorepo_root")
@patch("scripts.import_module.validate_manifest")
@patch("scripts.import_module.copy_backend")
@patch("scripts.import_module.copy_frontend")
@patch("scripts.import_module.copy_migration")
@patch("scripts.import_module.register_router")
@patch("scripts.import_module.register_dependency")
@patch("scripts.import_module.register_alembic_import")
@patch("scripts.import_module.register_menu")
@patch("scripts.import_module.run_migrations")
def test_import_module_frontend_only_nao_roda_migrations(
    mock_run_migrations,
    mock_register_menu,
    mock_register_alembic_import,
    mock_register_dependency,
    mock_register_router,
    mock_copy_migration,
    mock_copy_frontend,
    mock_copy_backend,
    mock_validate_manifest,
    mock_get_monorepo_root,
    tmp_path,
):
    """Fluxo frontend-only deve pular run_migrations mesmo com skip_migrations=False."""
    mock_get_monorepo_root.return_value = tmp_path
    mock_validate_manifest.return_value = {
        "module_name": "pop_viz",
        "frontend_only": True,
    }

    import_dir = tmp_path / "import_src"
    import_dir.mkdir()

    result = import_module.import_module(
        "pop_viz", import_dir, force=True, dry_run=False, skip_migrations=False
    )

    assert result["success"] is True
    mock_run_migrations.assert_not_called()
    assert any("sem migrações" in step for step in result["steps"])
