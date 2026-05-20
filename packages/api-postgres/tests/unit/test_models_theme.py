"""Testes unitários para os modelos Empresa e CompanyTheme."""

import pytest
from sqlalchemy.orm import Session

from app.database import Base
from app.models.empresa import Empresa
from app.models.theme import CompanyTheme


def test_create_empresa(db_session: Session):
    """Testa criação de empresa."""
    empresa = Empresa(nome="Acme Corp", dominio="acme.com")
    db_session.add(empresa)
    db_session.commit()
    db_session.refresh(empresa)

    assert empresa.id is not None
    assert empresa.nome == "Acme Corp"
    assert empresa.dominio == "acme.com"
    assert empresa.ativo is True


def test_create_company_theme(db_session: Session):
    """Testa criação de tema vinculado a empresa."""
    empresa = Empresa(nome="Test Corp", dominio="test.com")
    db_session.add(empresa)
    db_session.commit()

    theme = CompanyTheme(
        company_id=empresa.id,
        name="Test Theme",
        colors={"--skin-primary": "#ff0000"},
        icon_library="fontawesome",
    )
    db_session.add(theme)
    db_session.commit()
    db_session.refresh(theme)

    assert theme.id is not None
    assert theme.company_id == empresa.id
    assert theme.is_active is False
    assert theme.colors["--skin-primary"] == "#ff0000"


def test_activate_theme_deactivates_others(db_session: Session):
    """Testa que ativar um tema desativa os outros da mesma empresa."""
    empresa = Empresa(nome="Multi Theme Corp", dominio="multi.com")
    db_session.add(empresa)
    db_session.commit()

    theme1 = CompanyTheme(company_id=empresa.id, name="Theme 1", is_active=True, icon_library="fontawesome")
    theme2 = CompanyTheme(company_id=empresa.id, name="Theme 2", is_active=False, icon_library="fontawesome")
    db_session.add_all([theme1, theme2])
    db_session.commit()

    # Ativar theme2 deve desativar theme1
    theme2.is_active = True
    db_session.commit()

    db_session.refresh(theme1)
    db_session.refresh(theme2)

    assert theme1.is_active is False
    assert theme2.is_active is True


def test_insert_active_theme_deactivates_existing(db_session: Session):
    """Testa que inserir um tema ativo desativa o tema existente da mesma empresa."""
    empresa = Empresa(nome="Insert Test Corp", dominio="insert.com")
    db_session.add(empresa)
    db_session.commit()

    theme1 = CompanyTheme(company_id=empresa.id, name="Theme 1", is_active=True, icon_library="fontawesome")
    db_session.add(theme1)
    db_session.commit()
    db_session.refresh(theme1)
    assert theme1.is_active is True

    theme2 = CompanyTheme(company_id=empresa.id, name="Theme 2", is_active=True, icon_library="fontawesome")
    db_session.add(theme2)
    db_session.commit()

    db_session.refresh(theme1)
    db_session.refresh(theme2)

    assert theme1.is_active is False
    assert theme2.is_active is True
