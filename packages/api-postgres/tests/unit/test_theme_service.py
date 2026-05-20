"""Testes unitários para ThemeService."""

import pytest
from sqlalchemy.orm import Session

from app.models.empresa import Empresa
from app.models.theme import CompanyTheme
from app.repositories.theme_repository import ThemeRepository
from app.services.theme_service import ThemeService
from shared.exceptions.base import NotFoundError, ConflictError


@pytest.fixture
def theme_service(db_session: Session) -> ThemeService:
    repo = ThemeRepository(db_session)
    return ThemeService(repo)


@pytest.fixture
def empresa(db_session: Session) -> Empresa:
    emp = Empresa(nome="Test Corp", dominio="test.com")
    db_session.add(emp)
    db_session.commit()
    return emp


def test_get_active_theme_returns_none_if_no_theme(theme_service: ThemeService, empresa: Empresa):
    """Testa que retorna None quando não há tema ativo."""
    result = theme_service.get_active_theme(empresa.id)
    assert result is None


def test_get_active_theme(theme_service: ThemeService, empresa: Empresa):
    """Testa busca do tema ativo."""
    theme = CompanyTheme(
        company_id=empresa.id,
        name="Test Theme",
        is_active=True,
        colors={"--skin-primary": "#00ff00"},
        icon_library="fontawesome",
    )
    theme_service.repo.db.add(theme)
    theme_service.repo.db.commit()

    result = theme_service.get_active_theme(empresa.id)
    assert result is not None
    assert result["name"] == "Test Theme"
    assert result["colors"]["--skin-primary"] == "#00ff00"


def test_create_theme(theme_service: ThemeService, empresa: Empresa):
    """Testa criação de tema."""
    result = theme_service.create_theme(
        company_id=empresa.id,
        name="New Theme",
        colors={"--skin-primary": "#123456"},
    )
    assert result["name"] == "New Theme"
    assert result["company_id"] == empresa.id
    assert result["is_active"] is False


def test_update_theme(theme_service: ThemeService, empresa: Empresa):
    """Testa atualização de tema."""
    created = theme_service.create_theme(company_id=empresa.id, name="Old Name", icon_library="fontawesome")
    updated = theme_service.update_theme(created["id"], company_id=empresa.id, name="New Name")
    assert updated["name"] == "New Name"


def test_activate_theme(theme_service: ThemeService, empresa: Empresa):
    """Testa ativação de tema."""
    t1 = theme_service.create_theme(company_id=empresa.id, name="T1", icon_library="fontawesome")
    t2 = theme_service.create_theme(company_id=empresa.id, name="T2", icon_library="fontawesome")

    # Ativar t1
    theme_service.activate_theme(t1["id"], empresa.id)
    t1_check = theme_service.get_theme_by_id(t1["id"])
    assert t1_check["is_active"] is True

    # Ativar t2 deve desativar t1
    theme_service.activate_theme(t2["id"], empresa.id)
    t1_check = theme_service.get_theme_by_id(t1["id"])
    t2_check = theme_service.get_theme_by_id(t2["id"])
    assert t1_check["is_active"] is False
    assert t2_check["is_active"] is True


def test_delete_active_theme_raises(theme_service: ThemeService, empresa: Empresa):
    """Testa que não pode deletar tema ativo."""
    created = theme_service.create_theme(company_id=empresa.id, name="Active", icon_library="fontawesome")
    theme_service.activate_theme(created["id"], empresa.id)

    with pytest.raises(ConflictError):
        theme_service.delete_theme(created["id"])


def test_list_themes(theme_service: ThemeService, empresa: Empresa):
    """Testa listagem de temas."""
    theme_service.create_theme(company_id=empresa.id, name="T1", icon_library="fontawesome")
    theme_service.create_theme(company_id=empresa.id, name="T2", icon_library="fontawesome")

    results = theme_service.list_themes(empresa.id)
    assert len(results) == 2
