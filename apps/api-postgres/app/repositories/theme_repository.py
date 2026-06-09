"""
Repository para CompanyTheme.

Operações de persistência para temas/skins de empresas.
"""

from shared.exceptions.base import ConflictError
from sqlalchemy.orm import Session

from app.core.cache import _theme_cache, _theme_lock, get_or_set, invalidate
from app.models.theme import CompanyTheme


class ThemeRepository:
    """Repository para CRUD de CompanyTheme."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_active_by_company_id(self, company_id: int) -> CompanyTheme | None:
        """Busca o tema ativo de uma empresa (com cache)."""

        def _fetch():
            return (
                self.db.query(CompanyTheme)
                .filter(CompanyTheme.company_id == company_id, CompanyTheme.is_active)
                .first()
            )

        return get_or_set(_theme_cache, _theme_lock, f"active:{company_id}", _fetch)

    def find_all_by_company_id(self, company_id: int) -> list[CompanyTheme]:
        """Busca todos os temas de uma empresa."""
        return (
            self.db.query(CompanyTheme)
            .filter(CompanyTheme.company_id == company_id)
            .all()
        )

    def find_by_id(self, theme_id: int) -> CompanyTheme | None:
        """Busca tema por ID."""
        return self.db.get(CompanyTheme, theme_id)

    def create(self, theme: CompanyTheme) -> CompanyTheme:
        """Cria um novo tema."""
        self.db.add(theme)
        self.db.commit()
        self.db.refresh(theme)
        return theme

    def update(self, theme: CompanyTheme, **kwargs) -> CompanyTheme:
        """Atualiza campos de um tema."""
        for key, value in kwargs.items():
            if hasattr(theme, key):
                setattr(theme, key, value)
        self.db.commit()
        self.db.refresh(theme)

        # Invalida cache do tema ativo desta empresa
        invalidate(_theme_cache, _theme_lock, f"active:{theme.company_id}")
        return theme

    def activate_theme(self, theme_id: int, company_id: int) -> CompanyTheme:
        """Ativa um tema e desativa todos os outros da mesma empresa."""
        self.db.query(CompanyTheme).filter(
            CompanyTheme.company_id == company_id
        ).update({"is_active": False})

        theme = self.db.get(CompanyTheme, theme_id)
        if theme is None:
            raise ValueError(f"Tema {theme_id} não encontrado")
        if theme.company_id != company_id:
            raise ValueError(f"Tema {theme_id} não pertence à empresa {company_id}")
        theme.is_active = True
        self.db.commit()
        self.db.refresh(theme)

        # Invalida cache do tema ativo desta empresa
        invalidate(_theme_cache, _theme_lock, f"active:{company_id}")
        return theme

    def delete(self, theme_id: int) -> None:
        """Deleta um tema. Não pode deletar tema ativo."""
        theme = self.db.get(CompanyTheme, theme_id)
        if theme is None:
            raise ValueError(f"Tema {theme_id} não encontrado")
        if theme.is_active:
            raise ConflictError(
                "Não é possível deletar um tema ativo. Desative-o primeiro."
            )
        self.db.delete(theme)
        self.db.commit()
