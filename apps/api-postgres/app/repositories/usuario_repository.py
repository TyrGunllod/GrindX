"""
Repositório de acesso a dados para Usuario.

Encapsula todas as queries SQL para a tabela usuarios.
Nenhuma regra de negócio deve existir nesta camada.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.cache import _user_cache, _user_lock, get_or_set, invalidate
from app.models.usuario import Usuario


class UsuarioRepository:
    """Repositório CRUD para a entidade Usuario."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        """Busca um usuário pelo ID (com cache).

        Args:
            usuario_id: ID do usuário.

        Returns:
            Usuario encontrado ou None.
        """

        def _fetch():
            stmt = select(Usuario).where(Usuario.id == usuario_id)
            return self.db.execute(stmt).scalar_one_or_none()

        return get_or_set(_user_cache, _user_lock, f"id:{usuario_id}", _fetch)

    def buscar_por_username(self, username: str) -> Usuario | None:
        """Busca um usuário pelo username (único, com cache).

        Args:
            username: Nome de usuário.

        Returns:
            Usuario encontrado ou None.
        """

        def _fetch():
            stmt = select(Usuario).where(Usuario.username == username)
            return self.db.execute(stmt).scalar_one_or_none()

        return get_or_set(_user_cache, _user_lock, f"username:{username}", _fetch)

    def buscar_por_email(self, email: str) -> Usuario | None:
        """Busca um usuário pelo email (único).

        Args:
            email: E-mail do usuário.

        Returns:
            Usuario encontrado ou None.
        """
        stmt = select(Usuario).where(Usuario.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def listar_ativos(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[Usuario], int]:
        """Lista usuários ativos com paginação.

        Args:
            page: Número da página (1-indexed).
            page_size: Quantidade de itens por página.

        Returns:
            Tupla com (lista de usuários, total de registros).
        """
        # Query para total
        count_stmt = (
            select(func.count()).select_from(Usuario).where(Usuario.ativo.is_(True))
        )
        total = self.db.scalar(count_stmt) or 0

        # Query para itens
        stmt = (
            select(Usuario)
            .where(Usuario.ativo.is_(True))
            .order_by(Usuario.username)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(self.db.scalars(stmt).all())
        return items, total

    def listar_todos(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[Usuario], int]:
        """Lista todos os usuários com paginação.

        Args:
            page: Número da página (1-indexed).
            page_size: Quantidade de itens por página.

        Returns:
            Tupla com (lista de usuários, total de registros).
        """
        # Query para total
        count_stmt = select(func.count()).select_from(Usuario)
        total = self.db.scalar(count_stmt) or 0

        # Query para itens
        stmt = (
            select(Usuario)
            .order_by(Usuario.username)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(self.db.scalars(stmt).all())
        return items, total

    def listar_por_role(
        self, role: str, page: int = 1, page_size: int = 20
    ) -> tuple[list[Usuario], int]:
        """Lista usuários filtrados por role.

        Args:
            role: Perfil de acesso (admin, operador, leitura).
            page: Número da página (1-indexed).
            page_size: Quantidade de itens por página.

        Returns:
            Tupla com (lista de usuários, total de registros).
        """
        # Query para total
        count_stmt = (
            select(func.count()).select_from(Usuario).where(Usuario.role == role)
        )
        total = self.db.scalar(count_stmt) or 0

        # Query para itens
        stmt = (
            select(Usuario)
            .where(Usuario.role == role)
            .order_by(Usuario.username)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(self.db.scalars(stmt).all())
        return items, total

    def criar(self, usuario: Usuario) -> Usuario:
        """Cria um novo usuário no banco.

        Args:
            usuario: Instância do Usuario a ser criada.

        Returns:
            Usuario criado com ID gerado.
        """
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        # Invalida cache de busca por username para novo usuário
        invalidate(_user_cache, _user_lock, f"username:{usuario.username}")
        return usuario

    def atualizar(self, usuario: Usuario, dados: dict) -> Usuario:
        """Atualiza campos de um usuário existente.

        Args:
            usuario: Instância do usuário a ser atualizado.
            dados: Dicionário com campos a serem atualizados.

        Returns:
            Usuario atualizado.
        """
        # Reattach ao session atual (objeto pode vir do cache de request anterior)
        usuario = self.db.merge(usuario)
        for campo, valor in dados.items():
            if hasattr(usuario, campo):
                setattr(usuario, campo, valor)
        self.db.commit()
        self.db.refresh(usuario)

        # Invalida cache do usuário atualizado
        invalidate(_user_cache, _user_lock, f"id:{usuario.id}")
        invalidate(_user_cache, _user_lock, f"username:{usuario.username}")
        return usuario

    def desativar(self, usuario: Usuario) -> Usuario:
        """Soft delete — desativa o usuário.

        Args:
            usuario: Instância do usuário a ser desativado.

        Returns:
            Usuario com ativo=False.
        """
        usuario.ativo = False
        self.db.commit()
        self.db.refresh(usuario)

        # Invalida cache do usuário desativado
        invalidate(_user_cache, _user_lock, f"id:{usuario.id}")
        invalidate(_user_cache, _user_lock, f"username:{usuario.username}")
        return usuario

    def deletar(self, usuario: Usuario) -> None:
        """Delete físico de um usuário (hard delete).

        Use com cuidado em produção.

        Args:
            usuario: Instância do usuário a ser deletado.
        """
        # Invalida cache antes de deletar
        invalidate(_user_cache, _user_lock, f"id:{usuario.id}")
        invalidate(_user_cache, _user_lock, f"username:{usuario.username}")
        self.db.delete(usuario)
        self.db.commit()
