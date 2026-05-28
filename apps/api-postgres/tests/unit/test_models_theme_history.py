"""Testes unitários para o modelo ThemeHistory."""

from sqlalchemy.orm import Session

from app.models.empresa import Empresa
from app.models.theme import CompanyTheme
from app.models.theme_history import ThemeHistory


def test_create_theme_history(db_session: Session):
    """Testa criação de registro de histórico."""
    empresa = Empresa(nome="Test Corp", dominio="test.com")
    db_session.add(empresa)
    db_session.commit()

    theme = CompanyTheme(
        company_id=empresa.id, name="Test Theme", icon_library="fontawesome"
    )
    db_session.add(theme)
    db_session.commit()

    history = ThemeHistory(
        theme_id=theme.id, company_id=empresa.id, action="created", theme_snapshot={}
    )
    db_session.add(history)
    db_session.commit()
    db_session.refresh(history)

    assert history.id is not None
    assert history.theme_id == theme.id
    assert history.company_id == empresa.id
    assert history.action == "created"
    assert history.theme_snapshot == {}
    assert history.criado_em is not None


def test_history_cascade_on_theme_delete(db_session: Session):
    """Testa que histórico é deletado quando tema é deletado."""
    empresa = Empresa(nome="Cascade Corp", dominio="cascade.com")
    db_session.add(empresa)
    db_session.commit()

    theme = CompanyTheme(
        company_id=empresa.id, name="To Delete", icon_library="fontawesome"
    )
    db_session.add(theme)
    db_session.commit()

    history = ThemeHistory(
        theme_id=theme.id, company_id=empresa.id, action="created", theme_snapshot={}
    )
    db_session.add(history)
    db_session.commit()

    theme_id = theme.id
    db_session.delete(theme)
    db_session.commit()

    result = db_session.query(ThemeHistory).filter_by(theme_id=theme_id).first()
    assert result is None
