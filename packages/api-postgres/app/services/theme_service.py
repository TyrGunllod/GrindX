"""
Service para CompanyTheme.

Business logic para gestão de skins/temas de empresas.
"""

import structlog
from shared.exceptions.base import NotFoundError

from app.repositories.theme_repository import ThemeRepository

logger = structlog.get_logger(__name__)


class ThemeService:
    """Service para CRUD de temas de empresas."""

    def __init__(self, repo: ThemeRepository) -> None:
        self.repo = repo

    def get_active_theme(self, company_id: int) -> dict | None:
        """Retorna o tema ativo de uma empresa como dict serializável."""
        theme = self.repo.find_active_by_company_id(company_id)
        if theme is None:
            return None
        return self._to_dict(theme)

    def list_themes(self, company_id: int) -> list[dict]:
        """Lista todos os temas de uma empresa."""
        themes = self.repo.find_all_by_company_id(company_id)
        return [self._to_dict(t) for t in themes]

    def get_theme_by_id(self, theme_id: int) -> dict | None:
        """Busca tema por ID."""
        theme = self.repo.find_by_id(theme_id)
        if theme is None:
            return None
        return self._to_dict(theme)

    def create_theme(
        self,
        company_id: int,
        name: str,
        colors: dict | None = None,
        fonts: dict | None = None,
        icon_library: str = "fontawesome",
        tokens: dict | None = None,
        logo_url: str | None = None,
        logo_short_url: str | None = None,
        company_name: str | None = None,
        copyright_text: str | None = None,
    ) -> dict:
        """Cria um novo tema."""
        from app.models.theme import CompanyTheme

        theme = CompanyTheme(
            company_id=company_id,
            name=name,
            colors=colors,
            fonts=fonts,
            icon_library=icon_library,
            tokens=tokens,
            logo_url=logo_url,
            logo_short_url=logo_short_url,
            company_name=company_name,
            copyright_text=copyright_text,
        )
        theme = self.repo.create(theme)
        logger.info("Tema criado", theme_id=theme.id, company_id=company_id)
        return self._to_dict(theme)

    def update_theme(self, theme_id: int, company_id: int, **kwargs) -> dict:
        """Atualiza um tema existente."""
        theme = self.repo.find_by_id(theme_id)
        if theme is None:
            raise NotFoundError(f"Tema {theme_id} não encontrado")
        if theme.company_id != company_id:
            raise NotFoundError(f"Tema {theme_id} não pertence à empresa {company_id}")

        theme = self.repo.update(theme, **kwargs)
        logger.info("Tema atualizado", theme_id=theme.id)
        return self._to_dict(theme)

    def activate_theme(self, theme_id: int, company_id: int) -> dict:
        """Ativa um tema e desativa os outros da mesma empresa."""
        theme = self.repo.activate_theme(theme_id, company_id)
        logger.info("Tema ativado", theme_id=theme.id, company_id=company_id)
        return self._to_dict(theme)

    def delete_theme(self, theme_id: int) -> None:
        """Deleta um tema."""
        self.repo.delete(theme_id)
        logger.info("Tema deletado", theme_id=theme_id)

    @staticmethod
    def _to_dict(theme) -> dict:
        """Converte modelo para dict serializável."""
        return {
            "id": theme.id,
            "company_id": theme.company_id,
            "name": theme.name,
            "is_active": theme.is_active,
            "colors": theme.colors,
            "fonts": theme.fonts,
            "icon_library": theme.icon_library,
            "tokens": theme.tokens,
            "logo_url": theme.logo_url,
            "logo_short_url": theme.logo_short_url,
            "company_name": theme.company_name,
            "copyright_text": theme.copyright_text,
            "criado_em": theme.criado_em.isoformat() if theme.criado_em else None,
            "atualizado_em": theme.atualizado_em.isoformat() if theme.atualizado_em else None,
        }
