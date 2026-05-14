"""Camada de repositórios (acesso a dados)."""

from app.repositories.produto_repository import ProdutoRepository
from app.repositories.usuario_repository import UsuarioRepository

__all__ = [
    "ProdutoRepository",
    "UsuarioRepository",
]
