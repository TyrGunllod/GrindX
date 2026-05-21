"""Testes unitários para ThemeService."""

import pytest
from app.models.empresa import Empresa
from app.models.theme import CompanyTheme
from app.repositories.theme_repository import ThemeRepository
from app.services.theme_service import ThemeService
from shared.exceptions.base import ConflictError
from sqlalchemy.orm import Session


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


def test_create_theme_logs_history(theme_service: ThemeService, empresa: Empresa, db_session: Session):
    """Testa que criar tema registra histórico."""
    from unittest.mock import MagicMock, patch

    mock_session = MagicMock(wraps=db_session)
    mock_session.close = MagicMock()

    with patch("app.database.SessionLocal", return_value=mock_session):
        theme_service.create_theme(company_id=empresa.id, name="History Test", icon_library="fontawesome")

    from app.models.theme_history import ThemeHistory

    history = db_session.query(ThemeHistory).filter_by(action="created").first()
    assert history is not None
    assert history.action == "created"
    assert history.theme_snapshot is not None


def test_update_theme_logs_history(theme_service: ThemeService, empresa: Empresa, db_session: Session):
    """Testa que atualizar tema registra histórico com snapshot anterior."""
    from unittest.mock import MagicMock, patch

    mock_session = MagicMock(wraps=db_session)
    mock_session.close = MagicMock()

    from app.models.theme_history import ThemeHistory

    with patch("app.database.SessionLocal", return_value=mock_session):
        created = theme_service.create_theme(company_id=empresa.id, name="Old", icon_library="fontawesome")
        theme_service.update_theme(created["id"], company_id=empresa.id, name="New")

    history = db_session.query(ThemeHistory).filter_by(action="updated").first()
    assert history is not None
    assert history.action == "updated"
    assert history.theme_snapshot["name"] == "New"
    assert history.changes is not None
    assert "name" in history.changes
    assert history.changes["name"]["from"] == "Old"
    assert history.changes["name"]["to"] == "New"


def test_activate_theme_logs_history(theme_service: ThemeService, empresa: Empresa, db_session: Session):
    """Testa que ativar tema registra histórico."""
    from unittest.mock import MagicMock, patch

    mock_session = MagicMock(wraps=db_session)
    mock_session.close = MagicMock()

    from app.models.theme_history import ThemeHistory

    with patch("app.database.SessionLocal", return_value=mock_session):
        created = theme_service.create_theme(company_id=empresa.id, name="Activate Test", icon_library="fontawesome")
        theme_service.activate_theme(created["id"], empresa.id)

    history = db_session.query(ThemeHistory).filter_by(action="activated").first()
    assert history is not None
    assert history.action == "activated"


def test_delete_theme_logs_history(theme_service: ThemeService, empresa: Empresa, db_session: Session):
    """Testa que deletar tema registra histórico com snapshot completo."""
    from unittest.mock import patch

    created = theme_service.create_theme(company_id=empresa.id, name="Delete Test", icon_library="fontawesome")

    # Patch _log_history to capture the call arguments
    captured = {}
    original_log = theme_service._log_history

    def _capture_log(**kwargs):
        captured.update(kwargs)
        # Still call the real method via mocked SessionLocal
        from unittest.mock import MagicMock
        mock_session = MagicMock(wraps=db_session)
        mock_session.close = MagicMock()
        with patch("app.database.SessionLocal", return_value=mock_session):
            original_log(**kwargs)


    with patch.object(theme_service, "_log_history", side_effect=_capture_log, autospec=False):
        theme_service.delete_theme(created["id"])

    assert captured.get("action") == "deleted"
    assert captured.get("theme_snapshot") is not None
    assert captured["theme_snapshot"]["name"] == "Delete Test"
