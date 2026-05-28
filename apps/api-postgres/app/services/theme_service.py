"""
Service para CompanyTheme.

Business logic para gestão de skins/temas de empresas.
"""

import structlog
from shared.exceptions.base import NotFoundError

from app.models.theme import CompanyTheme
from app.models.theme_history import ThemeHistory
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

        # Log creation to history
        self._log_history(
            theme_id=theme.id,
            company_id=theme.company_id,
            action="created",
            theme_snapshot=self._to_dict(theme),
        )

        logger.info("Tema criado", theme_id=theme.id, company_id=company_id)
        return self._to_dict(theme)

    def update_theme(self, theme_id: int, company_id: int, **kwargs) -> dict:
        """Atualiza um tema existente."""
        theme = self.repo.find_by_id(theme_id)
        if theme is None:
            raise NotFoundError(f"Tema {theme_id} não encontrado")
        if theme.company_id != company_id:
            raise NotFoundError(f"Tema {theme_id} não pertence à empresa {company_id}")

        # Get original values for change tracking
        original_values = {
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
        }

        theme = self.repo.update(theme, **kwargs)

        # Calculate changes (only include fields that actually changed)
        changes = {}
        updated_dict = self._to_dict(theme)
        for key, original_value in original_values.items():
            new_value = updated_dict.get(key)
            if new_value != original_value:
                changes[key] = {"from": original_value, "to": new_value}

        # Log update to history
        self._log_history(
            theme_id=theme.id,
            company_id=theme.company_id,
            action="updated",
            theme_snapshot=updated_dict,
            changes=changes if changes else None,
        )

        logger.info("Tema atualizado", theme_id=theme.id)
        return self._to_dict(theme)

    def activate_theme(self, theme_id: int, company_id: int) -> dict:
        """Ativa um tema e desativa os outros da mesma empresa."""
        theme = self.repo.activate_theme(theme_id, company_id)

        # Log activation to history
        self._log_history(
            theme_id=theme.id,
            company_id=theme.company_id,
            action="activated",
            theme_snapshot=self._to_dict(theme),
        )

        logger.info("Tema ativado", theme_id=theme.id, company_id=company_id)
        return self._to_dict(theme)

    def delete_theme(self, theme_id: int) -> None:
        """Deleta um tema."""
        theme = self.repo.find_by_id(theme_id)
        if theme is None:
            raise NotFoundError(f"Tema {theme_id} não encontrado")

        theme_snapshot = self._to_dict(theme)

        # Log deletion to history BEFORE deleting (FK constraint)
        self._log_history(
            theme_id=theme_id,
            company_id=theme.company_id,
            action="deleted",
            theme_snapshot=theme_snapshot,
        )

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
            "atualizado_em": theme.atualizado_em.isoformat()
            if theme.atualizado_em
            else None,
        }

    def _log_history(
        self,
        theme_id: int,
        company_id: int,
        action: str,
        theme_snapshot: dict | None = None,
        changes: dict | None = None,
        performed_by: int | None = None,
    ) -> None:
        """Log a theme history entry.

        Args:
            theme_id: ID of the theme
            company_id: ID of the company
            action: Action performed (created, updated, deleted, activated, deactivated)
            theme_snapshot: Complete theme state after action
            changes: Diff of changes (for updates)
            performed_by: User ID who performed the action
        """
        # This would typically be done via a repository, but for simplicity
        # we'll add it directly here. In a real implementation, you'd want
        # to inject a ThemeHistoryRepository.
        from app.database import SessionLocal

        db = SessionLocal()
        try:
            history_entry = ThemeHistory(
                theme_id=theme_id,
                company_id=company_id,
                action=action,
                performed_by=performed_by,
                theme_snapshot=theme_snapshot,
                changes=changes,
            )
            db.add(history_entry)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error("Failed to log theme history", error=str(e))
        finally:
            db.close()

    def get_theme_history(self, theme_id: int, company_id: int) -> list[dict]:
        """Get history of changes for a theme."""
        from app.database import SessionLocal

        db = SessionLocal()
        try:
            # Verify theme belongs to company
            theme = self.repo.find_by_id(theme_id)
            if theme is None or theme.company_id != company_id:
                return []

            # Query history entries
            history_entries = (
                db.query(ThemeHistory)
                .filter(ThemeHistory.theme_id == theme_id)
                .order_by(ThemeHistory.criado_em.desc())
                .all()
            )

            return [
                {
                    "id": entry.id,
                    "theme_id": entry.theme_id,
                    "company_id": entry.company_id,
                    "action": entry.action,
                    "performed_by": entry.performed_by,
                    "theme_snapshot": entry.theme_snapshot,
                    "changes": entry.changes,
                    "criado_em": entry.criado_em,
                }
                for entry in history_entries
            ]
        finally:
            db.close()
