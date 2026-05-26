"""Testes de integração para o router de temas."""

import pytest
from fastapi.testclient import TestClient
from shared.security.jwt import gerar_hash_senha
from sqlalchemy.orm import Session

from app.models.empresa import Empresa
from app.models.theme import CompanyTheme
from app.models.usuario import Usuario


@pytest.fixture
def empresa(db_session: Session) -> Empresa:
    emp = Empresa(nome="Test Corp", dominio="test.com")
    db_session.add(emp)
    db_session.commit()
    return emp


@pytest.fixture
def admin_user(db_session: Session, empresa: Empresa) -> Usuario:
    user = Usuario(
        username="admintheme",
        email="admin@theme.com",
        nome_completo="Admin Theme",
        senha_hash=gerar_hash_senha("senha123"),
        role="admin",
        empresa_id=empresa.id,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def admin_auth_headers(client: TestClient, admin_user: Usuario) -> dict:
    response = client.post(
        "/v1/auth/token",
        json={"username": "admintheme", "password": "senha123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_active_theme_no_theme(client: TestClient, admin_auth_headers: dict):
    """Testa que retorna 404 quando não há tema ativo."""
    response = client.get("/v1/themes/active", headers=admin_auth_headers)
    assert response.status_code == 404


def test_create_and_get_active_theme(client: TestClient, admin_auth_headers: dict):
    """Testa criação e busca do tema ativo."""
    # Criar tema
    create_resp = client.post(
        "/v1/themes",
        json={
            "name": "Test Active",
            "colors": {"--skin-primary": "#ff0000"},
            "icon_library": "fontawesome",
        },
        headers=admin_auth_headers,
    )
    assert create_resp.status_code == 201
    theme_id = create_resp.json()["id"]

    # Ativar tema
    activate_resp = client.post(
        f"/v1/themes/{theme_id}/activate", headers=admin_auth_headers
    )
    assert activate_resp.status_code == 200
    assert activate_resp.json()["is_active"] is True

    # Buscar tema ativo
    get_resp = client.get("/v1/themes/active", headers=admin_auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Test Active"
    assert get_resp.json()["colors"]["--skin-primary"] == "#ff0000"


def test_list_themes(client: TestClient, admin_auth_headers: dict):
    """Testa listagem de temas."""
    client.post(
        "/v1/themes",
        json={"name": "T1", "icon_library": "fontawesome"},
        headers=admin_auth_headers,
    )
    client.post(
        "/v1/themes",
        json={"name": "T2", "icon_library": "fontawesome"},
        headers=admin_auth_headers,
    )

    response = client.get("/v1/themes", headers=admin_auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_delete_active_theme_fails(client: TestClient, admin_auth_headers: dict):
    """Testa que não pode deletar tema ativo."""
    create_resp = client.post(
        "/v1/themes",
        json={"name": "Delete Test", "icon_library": "fontawesome"},
        headers=admin_auth_headers,
    )
    theme_id = create_resp.json()["id"]

    # Ativar
    client.post(f"/v1/themes/{theme_id}/activate", headers=admin_auth_headers)

    # Tentar deletar
    delete_resp = client.delete(f"/v1/themes/{theme_id}", headers=admin_auth_headers)
    assert delete_resp.status_code == 409


def test_delete_inactive_theme_succeeds(client: TestClient, admin_auth_headers: dict):
    """Testa que pode deletar tema inativo."""
    create_resp = client.post(
        "/v1/themes",
        json={"name": "Delete Inactive", "icon_library": "fontawesome"},
        headers=admin_auth_headers,
    )
    theme_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/v1/themes/{theme_id}", headers=admin_auth_headers)
    assert delete_resp.status_code == 204


# --- Task 3: History endpoint tests ---


def test_get_theme_history(
    client: TestClient, admin_auth_headers: dict, empresa: Empresa, db_session
):
    """Testa busca do histórico de um tema."""
    from unittest.mock import MagicMock, patch

    from app.models.theme_history import ThemeHistory

    theme = CompanyTheme(
        company_id=empresa.id, name="History Theme", icon_library="fontawesome"
    )
    db_session.add(theme)
    db_session.commit()

    h1 = ThemeHistory(
        theme_id=theme.id,
        company_id=empresa.id,
        action="created",
        theme_snapshot={"name": "History Theme"},
    )
    h2 = ThemeHistory(
        theme_id=theme.id,
        company_id=empresa.id,
        action="updated",
        theme_snapshot={"name": "Updated Name"},
        changes={"name": {"from": "History Theme", "to": "Updated Name"}},
    )
    db_session.add_all([h1, h2])
    db_session.commit()

    mock_session = MagicMock(wraps=db_session)
    mock_session.close = MagicMock()

    with patch("app.database.SessionLocal", return_value=mock_session):
        resp = client.get(f"/v1/themes/{theme.id}/history", headers=admin_auth_headers)

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    actions = [h["action"] for h in data]
    assert "created" in actions
    assert "updated" in actions


def test_get_theme_history_theme_not_found(
    client: TestClient, admin_auth_headers: dict
):
    """Testa que retorna 404 para histórico de tema inexistente."""
    resp = client.get("/v1/themes/99999/history", headers=admin_auth_headers)
    assert resp.status_code == 404


# --- Task 4: Logo upload test ---


def test_upload_logo(
    client: TestClient, admin_auth_headers: dict, empresa: Empresa, db_session
):
    """Testa upload de logo para um tema."""

    theme = CompanyTheme(
        company_id=empresa.id, name="Logo Test", icon_library="fontawesome"
    )
    db_session.add(theme)
    db_session.commit()

    import io

    file_content = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"fake png content" * 100)

    resp = client.post(
        f"/v1/themes/{theme.id}/logo",
        files={"file": ("test-logo.png", file_content, "image/png")},
        headers=admin_auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "logo_url" in data
    assert data["logo_url"] is not None
    assert "test-logo" in data["logo_url"] or "uploads/logos" in data["logo_url"]

    db_session.refresh(theme)
    assert theme.logo_url is not None


# --- Task 5: Template tests ---


def test_list_templates(client: TestClient, admin_auth_headers: dict):
    """Testa listagem de templates disponíveis."""
    resp = client.get("/v1/themes/templates", headers=admin_auth_headers)
    assert resp.status_code == 200
    templates = resp.json()
    assert len(templates) >= 5
    slugs = [t["slug"] for t in templates]
    assert "corporate-blue" in slugs
    assert "dark-minimal" in slugs
    assert "warm-earth" in slugs
    assert "forest-green" in slugs
    assert "sunset-orange" in slugs


def test_create_from_template(client: TestClient, admin_auth_headers: dict):
    """Testa criação de tema a partir de template."""
    resp = client.post(
        "/v1/themes/from-template",
        json={"template_slug": "corporate-blue", "name": "My Blue Theme"},
        headers=admin_auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My Blue Theme"
    assert data["colors"]["--skin-primary"] == "#2563eb"
