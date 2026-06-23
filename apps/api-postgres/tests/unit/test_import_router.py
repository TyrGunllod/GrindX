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
        """Quando module.json tem target_api='sqlserver', deve passar --target-api ao subprocesso."""
        from unittest.mock import patch

        import app.routers.import_router as import_router

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

        with patch.object(import_router, "subprocess") as mock_subprocess:
            mock_proc = mock_subprocess.Popen.return_value
            mock_proc.communicate.return_value = (
                '{"success": true, "steps": ["ok"]}',
                "",
            )
            mock_proc.returncode = 0

            response = client.post("/v1/import/custo?force=true", headers=auth_headers)

        call_args = mock_subprocess.Popen.call_args[0][0]
        assert response.status_code == 200, response.text
        assert "--target-api=sqlserver" in call_args

    def test_import_defaults_to_postgres(
        self, client, auth_headers, tmp_path, monkeypatch
    ):
        """Quando module.json nao tem target_api, nao deve passar --target-api."""
        from unittest.mock import patch

        import app.routers.import_router as import_router

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

        with patch.object(import_router, "subprocess") as mock_subprocess:
            mock_proc = mock_subprocess.Popen.return_value
            mock_proc.communicate.return_value = (
                '{"success": true, "steps": ["ok"]}',
                "",
            )
            mock_proc.returncode = 0

            response = client.post(
                "/v1/import/projetos?force=true", headers=auth_headers
            )

        call_args = mock_subprocess.Popen.call_args[0][0]
        assert response.status_code == 200, response.text
        assert "--target-api=sqlserver" not in call_args
        assert "--target-api=postgres" not in call_args
