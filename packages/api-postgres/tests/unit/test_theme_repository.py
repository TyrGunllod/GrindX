"""Testes unitários para ThemeRepository."""

import pytest
from app.models.empresa import Empresa
from app.models.theme import CompanyTheme
from app.repositories.theme_repository import ThemeRepository
from sqlalchemy.orm import Session


@pytest.fixture
def theme_repo(db_session: Session) -> ThemeRepository:
    return ThemeRepository(db_session)


@pytest.fixture
def empresa(db_session: Session) -> Empresa:
    emp = Empresa(nome="Test Corp", dominio="test.com")
    db_session.add(emp)
    db_session.commit()
    return emp


@pytest.fixture
def active_theme(db_session: Session, empresa: Empresa) -> CompanyTheme:
    theme = CompanyTheme(
        company_id=empresa.id,
        name="Active Theme",
        is_active=True,
        colors={"--skin-primary": "#ff0000"},
        icon_library="fontawesome",
    )
    db_session.add(theme)
    db_session.commit()
    return theme


def test_find_active_by_company_id(
    theme_repo: ThemeRepository, empresa: Empresa, active_theme: CompanyTheme
):
    """Testa busca do tema ativo por empresa."""
    result = theme_repo.find_active_by_company_id(empresa.id)
    assert result is not None
    assert result.id == active_theme.id
    assert result.colors["--skin-primary"] == "#ff0000"


def test_find_active_returns_none_if_no_theme(
    theme_repo: ThemeRepository, empresa: Empresa
):
    """Testa que retorna None se não há tema ativo."""
    result = theme_repo.find_active_by_company_id(empresa.id)
    assert result is None


def test_find_all_by_company_id(theme_repo: ThemeRepository, empresa: Empresa):
    """Testa busca de todos os temas de uma empresa."""
    t1 = CompanyTheme(company_id=empresa.id, name="Theme 1", icon_library="fontawesome")
    t2 = CompanyTheme(company_id=empresa.id, name="Theme 2", icon_library="fontawesome")
    theme_repo.db.add_all([t1, t2])
    theme_repo.db.commit()

    results = theme_repo.find_all_by_company_id(empresa.id)
    assert len(results) == 2


def test_activate_deactivates_others(theme_repo: ThemeRepository, empresa: Empresa):
    """Testa que ativar um tema desativa os outros."""
    t1 = CompanyTheme(
        company_id=empresa.id, name="T1", is_active=True, icon_library="fontawesome"
    )
    t2 = CompanyTheme(
        company_id=empresa.id, name="T2", is_active=False, icon_library="fontawesome"
    )
    theme_repo.db.add_all([t1, t2])
    theme_repo.db.commit()

    theme_repo.activate_theme(t2.id, empresa.id)

    t1_check = theme_repo.db.get(CompanyTheme, t1.id)
    t2_check = theme_repo.db.get(CompanyTheme, t2.id)
    assert t1_check.is_active is False
    assert t2_check.is_active is True


def test_delete_raises_if_active(
    theme_repo: ThemeRepository, empresa: Empresa, active_theme: CompanyTheme
):
    """Testa que não pode deletar tema ativo."""
    from shared.exceptions.base import ConflictError

    with pytest.raises(ConflictError):
        theme_repo.delete(active_theme.id)
