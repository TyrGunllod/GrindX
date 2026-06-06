"""
Testes de segurança para autenticação com senhas temporárias.

Valida geração via secrets module, expiração de 15 minutos,
e limpeza de campos temporários após uso.
"""

import re
from datetime import datetime, timedelta, timezone

import pytest
from shared.exceptions.base import CredenciaisInvalidasError, NotFoundError
from shared.security.jwt import gerar_hash_senha, verificar_senha

from app.auth.service import AuthService
from app.modules.iam.models.usuario import Usuario


class TestTempPasswordGeneration:
    """Testa geração segura de senhas temporárias."""

    def test_temp_password_generated_with_secrets(self, db_session):
        """Senha temporária deve ter 16 caracteres alfanuméricos."""
        # Create user
        usuario = Usuario(
            username="testuser",
            email="test@example.com",
            nome_completo="Test User",
            senha_hash=gerar_hash_senha("oldpassword"),
            role="leitura",
        )
        db_session.add(usuario)
        db_session.commit()

        # Generate temp password
        service = AuthService(db_session)
        email, nome, temp_password = service.forgot_password("testuser")

        # Assert: 16 alphanumeric characters
        assert len(temp_password) == 16
        assert re.match(r"^[A-Za-z0-9]{16}$", temp_password) is not None

    def test_temp_password_stored_with_expiry(self, db_session):
        """Hash da senha temporária e expiração devem ser persistidos no banco."""
        # Create user
        usuario = Usuario(
            username="testuser",
            email="test@example.com",
            nome_completo="Test User",
            senha_hash=gerar_hash_senha("oldpassword"),
            role="leitura",
        )
        db_session.add(usuario)
        db_session.commit()

        # Generate temp password
        service = AuthService(db_session)
        service.forgot_password("testuser")

        # Refresh from DB
        db_session.refresh(usuario)

        # Assert: temp_password_hash is set
        assert usuario.temp_password_hash is not None

        # Assert: expires_at is ~15min from now
        assert usuario.expires_at is not None
        now = datetime.now(timezone.utc)
        expected_expiry = now + timedelta(minutes=15)
        # Handle SQLite naive datetimes
        expires_at = usuario.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        # Allow 1 minute tolerance
        assert abs((expires_at - expected_expiry).total_seconds()) < 60


class TestTempPasswordExpiry:
    """Testa rejeição de senhas temporárias expiradas."""

    def test_expired_temp_password_rejected(self, db_session):
        """Senha temporária expirada deve ser rejeitada no login."""
        # Create user with expired temp password
        usuario = Usuario(
            username="testuser",
            email="test@example.com",
            nome_completo="Test User",
            senha_hash=gerar_hash_senha("oldpassword"),
            role="leitura",
        )
        db_session.add(usuario)
        db_session.commit()

        # Set temp password manually with past expiry
        temp_password = "TempPass12345678"
        usuario.temp_password_hash = gerar_hash_senha(temp_password)
        usuario.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        db_session.commit()

        # Attempt login with expired temp password
        service = AuthService(db_session)
        with pytest.raises(CredenciaisInvalidasError) as exc_info:
            service.autenticar("testuser", temp_password)

        assert "expirada" in str(exc_info.value).lower()

    def test_valid_temp_password_accepted(self, db_session):
        """Senha temporária válida deve permitir login."""
        # Create user with valid temp password
        usuario = Usuario(
            username="testuser",
            email="test@example.com",
            nome_completo="Test User",
            senha_hash=gerar_hash_senha("oldpassword"),
            role="leitura",
        )
        db_session.add(usuario)
        db_session.commit()

        # Generate temp password via service
        service = AuthService(db_session)
        _, _, temp_password = service.forgot_password("testuser")

        # Attempt login with valid temp password
        tokens = service.autenticar("testuser", temp_password)
        assert tokens.access_token is not None

        # Verify temp fields cleared
        db_session.refresh(usuario)
        assert usuario.temp_password_hash is None
        assert usuario.expires_at is None

    def test_temp_password_rejected_when_expires_at_is_none(self, db_session):
        """Senha temporária sem expiração deve ser rejeitada no login (fail-closed)."""
        # Create user with temp password but no expiry
        usuario = Usuario(
            username="testuser",
            email="test@example.com",
            nome_completo="Test User",
            senha_hash=gerar_hash_senha("oldpassword"),
            role="leitura",
        )
        db_session.add(usuario)
        db_session.commit()

        # Set temp password manually WITHOUT setting expires_at (None)
        temp_password = "TempPass12345678"
        usuario.temp_password_hash = gerar_hash_senha(temp_password)
        # expires_at is left as None (fail-closed must reject)
        db_session.commit()

        # Attempt login with temp password — should be rejected
        service = AuthService(db_session)
        with pytest.raises(CredenciaisInvalidasError) as exc_info:
            service.autenticar("testuser", temp_password)

        assert "expirada" in str(exc_info.value).lower()


class TestApplyTempPassword:
    """Testa aplicação de senha temporária."""

    def test_apply_temp_password_clears_fields(self, db_session):
        """Após aplicar senha temporária, campos temp devem ser limpos."""
        # Create user
        usuario = Usuario(
            username="testuser",
            email="test@example.com",
            nome_completo="Test User",
            senha_hash=gerar_hash_senha("oldpassword"),
            role="leitura",
        )
        db_session.add(usuario)
        db_session.commit()

        # Generate temp password
        service = AuthService(db_session)
        _, _, temp_password = service.forgot_password("testuser")

        # Apply temp password
        service.apply_temp_password("testuser", temp_password)

        # Verify temp fields cleared
        db_session.refresh(usuario)
        assert usuario.temp_password_hash is None
        assert usuario.expires_at is None

        # Verify new password works
        assert verificar_senha(temp_password, usuario.senha_hash)

    def test_apply_temp_password_rejected_when_expires_at_is_none(self, db_session):
        """Aplicar senha temporária sem expiração deve ser rejeitado (fail-closed)."""
        # Create user with temp password but no expiry
        usuario = Usuario(
            username="testuser",
            email="test@example.com",
            nome_completo="Test User",
            senha_hash=gerar_hash_senha("oldpassword"),
            role="leitura",
        )
        db_session.add(usuario)
        db_session.commit()

        # Set temp password manually WITHOUT setting expires_at (None)
        temp_password = "TempPass12345678"
        usuario.temp_password_hash = gerar_hash_senha(temp_password)
        # expires_at is left as None (fail-closed must reject)
        db_session.commit()

        # Attempt to apply temp password — should be rejected
        service = AuthService(db_session)
        with pytest.raises(CredenciaisInvalidasError) as exc_info:
            service.apply_temp_password("testuser", temp_password)

        assert "expirada" in str(exc_info.value).lower()

    def test_apply_expired_temp_password_rejected(self, db_session):
        """Senha temporária expirada deve ser rejeitada ao aplicar."""
        # Create user with expired temp password
        usuario = Usuario(
            username="testuser",
            email="test@example.com",
            nome_completo="Test User",
            senha_hash=gerar_hash_senha("oldpassword"),
            role="leitura",
        )
        db_session.add(usuario)
        db_session.commit()

        # Set temp password manually with past expiry
        temp_password = "TempPass12345678"
        usuario.temp_password_hash = gerar_hash_senha(temp_password)
        usuario.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        db_session.commit()

        # Attempt to apply expired temp password
        service = AuthService(db_session)
        with pytest.raises(CredenciaisInvalidasError) as exc_info:
            service.apply_temp_password("testuser", temp_password)

        assert "expirada" in str(exc_info.value).lower()
