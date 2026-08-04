"""Tests for the import router endpoints."""

import json
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient


class TestScanEndpoint:
    def test_scan_sem_pasta_import_retorna_vazio(
        self, client: TestClient, auth_headers: dict, monkeypatch
    ):
        """When import/ dir doesn't exist, scan returns empty list."""
        from pathlib import Path

        monkeypatch.setattr(
            "app.routers.import_router._get_import_dir",
            lambda: Path("C:\\nonexistent_import_dir_grindx_test"),
        )
        response = client.get("/v1/import/scan", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["modules"] == []

    def test_scan_sem_manifest_ignora_zip(
        self, client: TestClient, auth_headers: dict, tmp_path: Path, monkeypatch
    ):
        """Zips without module.json are ignored."""
        zip_path = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("some_file.txt", "content")

        monkeypatch.setattr(
            "app.routers.import_router._get_import_dir", lambda: tmp_path
        )
        response = client.get("/v1/import/scan", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["modules"] == []

    def test_scan_com_manifest_retorna_modulo(
        self, client: TestClient, auth_headers: dict, tmp_path: Path, monkeypatch
    ):
        """Zip with valid module.json is returned in scan."""
        manifest = {
            "module_name": "projetos",
            "entity_name": "Projeto",
            "version": "1.0.0",
            "schema_name": "org",
            "menu_label": "Projetos",
        }
        zip_path = tmp_path / "projetos.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("module.json", json.dumps(manifest))

        monkeypatch.setattr(
            "app.routers.import_router._get_import_dir", lambda: tmp_path
        )
        response = client.get("/v1/import/scan", headers=auth_headers)
        assert response.status_code == 200
        modules = response.json()["modules"]
        assert len(modules) == 1
        assert modules[0]["module_name"] == "projetos"
        assert modules[0]["ja_importado"] is False

    def test_scan_requer_autenticacao(self, client: TestClient):
        """Unauthenticated requests get 401."""
        response = client.get("/v1/import/scan")
        assert response.status_code == 401


class TestImportEndpoint:
    def test_import_zip_inexistente_retorna_404(
        self, client: TestClient, auth_headers: dict
    ):
        """Importing non-existent module returns 404."""
        response = client.post("/v1/import/modulo_inexistente", headers=auth_headers)
        assert response.status_code == 404

    def test_import_zip_sem_manifest_retorna_422(
        self, client: TestClient, auth_headers: dict, tmp_path: Path, monkeypatch
    ):
        """Zip without module.json returns 422."""
        zip_path = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("random.txt", "content")

        monkeypatch.setattr(
            "app.routers.import_router._get_import_dir", lambda: tmp_path
        )
        response = client.post("/v1/import/test", headers=auth_headers)
        assert response.status_code == 422

    def test_import_requer_autenticacao(self, client: TestClient):
        """Unauthenticated import requests get 401."""
        response = client.post("/v1/import/test")
        assert response.status_code == 401


def _criar_zip_manifest(tmp_path: Path, module_name: str, manifest: dict) -> Path:
    """Helper to create a zip with module.json at tmp_path."""
    zip_path = tmp_path / f"{module_name}.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("module.json", json.dumps(manifest))
    return zip_path


class TestImportSqlServer:
    def test_import_passes_target_api_to_subprocess(
        self, client, auth_headers, tmp_path, monkeypatch
    ):
        """Quando module.json tem target_api='sqlserver', deve importar com target sqlserver."""
        from unittest.mock import patch

        _criar_zip_manifest(
            tmp_path,
            "custo",
            {
                "module_name": "custo",
                "entity_name": "CustoProduto",
                "target_api": "sqlserver",
                "schema_name": "custo",
                "route_prefix": "/v1/produtos/custos",
                "menu_label": "Custos",
                "frontend_tabs": [
                    {"name": "Custos", "url": "modules/custos/index.html"}
                ],
            },
        )

        monkeypatch.setattr(
            "app.routers.import_router._get_import_dir", lambda: tmp_path
        )

        with patch("scripts.import_module.import_module") as mock_import:
            mock_import.return_value = {"success": True, "steps": ["ok"]}
            response = client.post("/v1/import/custo?force=true", headers=auth_headers)

        assert response.status_code == 200, response.text
        _, _, call_kwargs = mock_import.mock_calls[0]
        assert call_kwargs["target_api"] == "sqlserver"

    def test_import_defaults_to_postgres(
        self, client, auth_headers, tmp_path, monkeypatch
    ):
        """Quando module.json nao tem target_api, deve importar com target postgres."""
        from unittest.mock import patch

        _criar_zip_manifest(
            tmp_path,
            "projetos",
            {
                "module_name": "projetos",
                "entity_name": "Projeto",
                "schema_name": "org",
                "route_prefix": "/v1/projetos",
                "menu_label": "Projetos",
                "frontend_tabs": [
                    {"name": "Projetos", "url": "modules/projetos/index.html"}
                ],
            },
        )

        monkeypatch.setattr(
            "app.routers.import_router._get_import_dir", lambda: tmp_path
        )

        with patch("scripts.import_module.import_module") as mock_import:
            mock_import.return_value = {"success": True, "steps": ["ok"]}
            response = client.post(
                "/v1/import/projetos?force=true", headers=auth_headers
            )

        assert response.status_code == 200, response.text
        _, _, call_kwargs = mock_import.mock_calls[0]
        assert call_kwargs["target_api"] == "postgres"


class TestImportFrontendOnly:
    def test_import_frontend_only_nao_agenda_migracoes(
        self, client, auth_headers, tmp_path, monkeypatch
    ):
        from unittest.mock import patch

        _criar_zip_manifest(
            tmp_path,
            "pop_viz",
            {
                "module_name": "pop_viz",
                "entity_name": "PopViz",
                "frontend_only": True,
                "menu_label": "Visualizador POP",
                "frontend_tabs": [
                    {
                        "name": "Visualizador POP",
                        "url": "modules/pop_viz/index.html",
                    }
                ],
            },
        )
        monkeypatch.setattr(
            "app.routers.import_router._get_import_dir", lambda: tmp_path
        )

        with (
            patch("scripts.import_module.import_module") as mock_import,
            patch("app.routers.import_router._run_migrations_background") as mock_bg,
        ):
            mock_import.return_value = {"success": True, "steps": ["ok"]}
            response = client.post(
                "/v1/import/pop_viz?force=true", headers=auth_headers
            )

        assert response.status_code == 200, response.text
        steps = response.json()["steps"]
        assert "Módulo frontend-only importado — sem migrações" in steps
        assert "Migrações agendadas em segundo plano" not in steps
        mock_bg.assert_not_called()

    def test_scan_frontend_only_importado_como_ja_importado(
        self, client, auth_headers, tmp_path, monkeypatch
    ):
        import pathlib

        _criar_zip_manifest(
            tmp_path,
            "pop_viz",
            {
                "module_name": "pop_viz",
                "entity_name": "PopViz",
                "frontend_only": True,
                "menu_label": "Visualizador POP",
            },
        )
        monkeypatch.setattr(
            "app.routers.import_router._get_import_dir", lambda: tmp_path
        )

        phantom_backend = (
            tmp_path / "apps" / "api-postgres" / "app" / "modules" / "pop_viz"
        )
        phantom_backend.mkdir(parents=True)
        (phantom_backend / "module.json").write_text(
            json.dumps({"module_name": "pop_viz", "frontend_only": True}),
            encoding="utf-8",
        )
        frontend_mod = tmp_path / "apps" / "frontend-webapp" / "modules" / "pop_viz"
        frontend_mod.mkdir(parents=True)
        (frontend_mod / "index.html").write_text("<html></html>", encoding="utf-8")

        real_resolve = pathlib.Path.resolve

        def _fake_resolve(path_obj, strict=False):
            if "import_router.py" in str(path_obj):
                return pathlib.Path(
                    tmp_path
                    / "apps"
                    / "api-postgres"
                    / "app"
                    / "routers"
                    / "import_router.py"
                )
            return real_resolve(path_obj, strict=strict)

        monkeypatch.setattr(pathlib.Path, "resolve", _fake_resolve)

        response = client.get("/v1/import/scan", headers=auth_headers)
        assert response.status_code == 200
        modules = response.json()["modules"]
        found = [m for m in modules if m["slug"] == "pop_viz"]
        assert len(found) == 1
        assert found[0]["ja_importado"] is True
        assert found[0]["pode_remover"] is True

    def test_scan_frontend_only_instalados_pode_remover_segundo_phantom_dir(
        self, client, auth_headers, tmp_path, monkeypatch
    ):
        import pathlib

        monkeypatch.setattr(
            "app.routers.import_router._get_import_dir", lambda: tmp_path
        )
        real_resolve = pathlib.Path.resolve

        def _fake_resolve(path_obj, strict=False):
            if "import_router.py" in str(path_obj):
                return pathlib.Path(
                    tmp_path
                    / "apps"
                    / "api-postgres"
                    / "app"
                    / "routers"
                    / "import_router.py"
                )
            return real_resolve(path_obj, strict=strict)

        monkeypatch.setattr(pathlib.Path, "resolve", _fake_resolve)

        def _add_frontend_only_dir():
            frontend_mod = tmp_path / "apps" / "frontend-webapp" / "modules" / "pop_viz"
            frontend_mod.mkdir(parents=True, exist_ok=True)
            (frontend_mod / "index.html").write_text("<html></html>", encoding="utf-8")

        def _scan_instalados():
            response = client.get("/v1/import/scan", headers=auth_headers)
            assert response.status_code == 200
            instalados = response.json()["instalados"]
            found = [m for m in instalados if m["slug"] == "pop_viz"]
            return found[0] if found else None

        _add_frontend_only_dir()
        entry = _scan_instalados()
        assert entry is None or entry["pode_remover"] is False

        phantom_backend = (
            tmp_path / "apps" / "api-postgres" / "app" / "modules" / "pop_viz"
        )
        phantom_backend.mkdir(parents=True, exist_ok=True)
        (phantom_backend / "module.json").write_text(
            json.dumps({"module_name": "pop_viz", "frontend_only": True}),
            encoding="utf-8",
        )

        entry = _scan_instalados()
        assert entry is not None
        assert entry["pode_remover"] is True
        assert entry["ja_importado"] is True
