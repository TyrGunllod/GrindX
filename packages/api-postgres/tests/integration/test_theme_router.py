"""Testes de integração para o router de temas."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.empresa import Empresa
from app.models.theme import CompanyTheme
from app.models.usuario import Usuario
from shared.security.jwt import gerar_hash_senha


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
    activate_resp = client.post(f"/v1/themes/{theme_id}/activate", headers=admin_auth_headers)
    assert activate_resp.status_code == 200
    assert activate_resp.json()["is_active"] is True

    # Buscar tema ativo
    get_resp = client.get("/v1/themes/active", headers=admin_auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Test Active"
    assert get_resp.json()["colors"]["--skin-primary"] == "#ff0000"


def test_list_themes(client: TestClient, admin_auth_headers: dict):
    """Testa listagem de temas."""
    client.post("/v1/themes", json={"name": "T1", "icon_library": "fontawesome"}, headers=admin_auth_headers)
    client.post("/v1/themes", json={"name": "T2", "icon_library": "fontawesome"}, headers=admin_auth_headers)

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
