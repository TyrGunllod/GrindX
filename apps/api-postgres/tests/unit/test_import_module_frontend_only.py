"""Tests for frontend-only module support in import_module.py."""

import json

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
