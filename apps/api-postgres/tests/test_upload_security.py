"""
Testes de segurança para uploads com validação de magic bytes.

Valida que arquivos com extensões falsas são rejeitados,
e que arquivos válidos passam a validação.
"""

import io
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from shared.security.jwt import gerar_hash_senha

from app.models.usuario import Usuario


@pytest.fixture
def auth_headers_with_company(client: TestClient, db_session):
    """Cria um usuário admin com empresa vinculada e retorna headers de auth."""
    usuario = Usuario(
        username="admin_upload",
        email="admin_upload@example.com",
        nome_completo="Admin Upload",
        senha_hash=gerar_hash_senha("senha123"),
        role="admin",
        empresa_id=1,  # Mock company_id
    )
    db_session.add(usuario)
    db_session.commit()

    response = client.post(
        "/v1/auth/token",
        json={"username": "admin_upload", "password": "senha123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# Complete ThemeResponse mock
_MOCK_THEME = {
    "id": 1,
    "company_id": 1,
    "name": "Test Theme",
    "is_active": True,
    "colors": {},
    "fonts": {},
    "icon_library": "fontawesome",
    "logo_url": "/uploads/logos/test.png",
    "logo_short_url": None,
    "tokens": {},
    "company_name": None,
    "copyright_text": None,
}


class TestUploadMagicBytes:
    """Testa validação de magic bytes em uploads."""

    def test_txt_renamed_to_png_rejected(
        self, client: TestClient, auth_headers_with_company
    ):
        """Arquivo .txt renomeado para .png deve retornar HTTP 400."""
        # Create a plain text file with .png extension
        fake_png = io.BytesIO(b"this is not an image")
        fake_png.name = "fake.png"

        # Mock theme service to return a valid theme
        with patch("app.routers.theme_router.ThemeService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.get_theme_by_id.return_value = {"company_id": 1}

            response = client.post(
                "/v1/themes/1/logo",
                files={"file": ("fake.png", fake_png, "image/png")},
                headers=auth_headers_with_company,
            )

        assert response.status_code == 400
        detail = response.json()["detail"].lower()
        # Plain text can't be detected by filetype → "could not detect"
        # OR if it gets detected as something else → "doesn't match"
        assert "não corresponde" in detail or "detectar" in detail

    def test_valid_png_accepted(self, client: TestClient, auth_headers_with_company):
        """Arquivo PNG válido deve passar na validação de magic bytes."""
        # Create minimal valid PNG (signature + IHDR chunk)
        png_signature = b"\x89PNG\r\n\x1a\n"
        # Minimal IHDR chunk
        ihdr_data = b"\x00\x00\x00\x01"  # width=1
        ihdr_data += b"\x00\x00\x00\x01"  # height=1
        ihdr_data += b"\x08"  # bit depth
        ihdr_data += b"\x02"  # color type (RGB)
        ihdr_data += b"\x00"  # compression
        ihdr_data += b"\x00"  # filter
        ihdr_data += b"\x00"  # interlace
        ihdr_length = b"\x00\x00\x00\x0d"  # 13 bytes
        ihdr_type = b"IHDR"
        ihdr_crc = b"\x00\x00\x00\x00"

        png_bytes = png_signature + ihdr_length + ihdr_type + ihdr_data + ihdr_crc

        valid_png = io.BytesIO(png_bytes)
        valid_png.name = "logo.png"

        # Mock theme service to return a valid theme
        with patch("app.routers.theme_router.ThemeService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.get_theme_by_id.return_value = {"company_id": 1}
            mock_service.update_theme.return_value = _MOCK_THEME

            response = client.post(
                "/v1/themes/1/logo",
                files={"file": ("logo.png", valid_png, "image/png")},
                headers=auth_headers_with_company,
            )

        # Should succeed (not 400 for magic bytes)
        assert response.status_code == 200

    def test_corrupted_file_rejected(
        self, client: TestClient, auth_headers_with_company
    ):
        """Arquivo vazio/corrompido deve retornar HTTP 400."""
        # Create empty file
        empty_file = io.BytesIO(b"")
        empty_file.name = "empty.ttf"

        response = client.post(
            "/v1/themes/fonts/upload",
            files={"file": ("empty.ttf", empty_file, "font/sfnt")},
            headers=auth_headers_with_company,
        )

        assert response.status_code == 400
        assert (
            "corrompido" in response.json()["detail"].lower()
            or "detectar" in response.json()["detail"].lower()
        )

    def test_font_with_wrong_extension_rejected(
        self, client: TestClient, auth_headers_with_company
    ):
        """Arquivo .ttf com magic bytes de PNG deve retornar HTTP 400."""
        # Create PNG bytes with .ttf extension
        png_signature = b"\x89PNG\r\n\x1a\n"
        fake_font = io.BytesIO(png_signature + b"\x00" * 100)
        fake_font.name = "fake.ttf"

        response = client.post(
            "/v1/themes/fonts/upload",
            files={"file": ("fake.ttf", fake_font, "font/sfnt")},
            headers=auth_headers_with_company,
        )

        assert response.status_code == 400
        assert "não corresponde" in response.json()["detail"].lower()
