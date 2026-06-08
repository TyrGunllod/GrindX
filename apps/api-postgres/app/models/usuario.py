"""Re-exports from IAM module for backward compatibility.

This module re-exports Usuario and UsuarioModulo from the IAM module
to maintain import paths that existing code depends on. New code should
import directly from app.modules.iam.models.usuario.
"""
from app.modules.iam.models.usuario import Usuario, UsuarioModulo  # noqa: F401
