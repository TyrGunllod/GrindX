"""Encrypt/decrypt sensitive data using Fernet symmetric encryption.

Usage:
    from shared.security.encryption import encrypt_value, decrypt_value

    key = settings.SECRET_KEY  # Must be at least 32 chars
    encrypted = encrypt_value(key, "sensitive data")
    plaintext = decrypt_value(key, encrypted)
"""

import base64
import hashlib

from cryptography.fernet import Fernet


def _derive_fernet_key(secret_key: str) -> bytes:
    """Derives a 32-byte Fernet key from SECRET_KEY using SHA-256."""
    return base64.urlsafe_b64encode(hashlib.sha256(secret_key.encode()).digest())


def encrypt_value(secret_key: str, plaintext: str | None) -> str | None:
    """Encrypts a plaintext string.

    Args:
        secret_key: Application SECRET_KEY (min 32 chars).
        plaintext: Value to encrypt.

    Returns:
        Encrypted string with 'enc:' prefix, or None if input is None.
    """
    if plaintext is None:
        return None
    key = _derive_fernet_key(secret_key)
    cipher = Fernet(key)
    token = cipher.encrypt(plaintext.encode("utf-8"))
    return f"enc:{token.decode()}"


def decrypt_value(secret_key: str, ciphertext: str | None) -> str | None:
    """Decrypts a value previously encrypted with encrypt_value.

    Handles both encrypted (``enc:`` prefix) and plaintext values
    for backward compatibility with unencrypted data.

    Args:
        secret_key: Application SECRET_KEY.
        ciphertext: Value to decrypt.

    Returns:
        Decrypted string, or None if input is None.
    """
    if ciphertext is None:
        return None
    if not ciphertext.startswith("enc:"):
        return ciphertext
    key = _derive_fernet_key(secret_key)
    cipher = Fernet(key)
    try:
        token = ciphertext[4:]
        return cipher.decrypt(token.encode()).decode("utf-8")
    except Exception:
        return ciphertext
