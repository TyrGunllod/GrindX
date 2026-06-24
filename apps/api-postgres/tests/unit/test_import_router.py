"""Tests for the import router endpoints."""

import json
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient


class TestScanEndpoint:
    def test_scan_sem_pasta_import_retorna_vazio(
        self, client: TestClient, auth_headers: dict
    ):
        """When import/ dir doesn't exist, scan returns empty list."""
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
