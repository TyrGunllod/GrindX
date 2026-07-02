"""Custom EncryptedString SQLAlchemy type for transparent field-level encryption."""

import sqlalchemy.types as types
from shared.security.encryption import decrypt_value, encrypt_value


class EncryptedString(types.TypeDecorator):
    """Encrypts string values transparently when stored in the database.

    Uses Fernet symmetric encryption with the app's SECRET_KEY.
    Handles ``None`` values gracefully.

    Usage in models::

        cpf: Mapped[str | None] = mapped_column(
            EncryptedString(14), nullable=True, comment="CPF"
        )
    """

    impl = types.String
    cache_ok = True

    def __init__(self, length: int | None = None):
        super().__init__(length)
        self._secret_key: str | None = None

    def _get_key(self) -> str:
        if self._secret_key is None:
            from app.core.config import settings

            self._secret_key = settings.SECRET_KEY
        return self._secret_key

    def process_bind_param(self, value: str | None, dialect) -> str | None:
        """Encrypt on the way into the database."""
        if value is None:
            return None
        return encrypt_value(self._get_key(), value)

    def process_result_value(self, value: str | None, dialect) -> str | None:
        """Decrypt on the way out of the database."""
        if value is None:
            return None
        return decrypt_value(self._get_key(), value)
