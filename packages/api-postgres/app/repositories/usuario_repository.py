"""
Repositório de acesso a dados para Usuario.

Encapsula todas as queries SQL para a tabela usuarios.
Nenhuma regra de negócio deve existir nesta camada.
"""

from sqlalchemy.orm import Session

from app.models.usuario import Usuario


class UsuarioRepository:
    """Repositório CRUD para a entidade Usuario."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        """Busca um usuário pelo ID.

        Args:
            usuario_id: ID do usuário.

        Returns:
            Usuario encontrado ou None.
        """
        return self.db.query(Usuario).filter(Usuario.id == usuario_id).first()

    def buscar_por_username(self, username: str) -> Usuario | None:
        """Busca um usuário pelo username (único).

        Args:
            username: Nome de usuário.

        Returns:
            Usuario encontrado ou None.
        """
        return self.db.query(Usuario).filter(Usuario.username == username).first()

    def buscar_por_email(self, email: str) -> Usuario | None:
        """Busca um usuário pelo email (único).

        Args:
            email: E-mail do usuário.

        Returns:
            Usuario encontrado ou None.
        """
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def listar_ativos(self, page: int = 1, page_size: int = 20) -> tuple[list[Usuario], int]:
        """Lista usuários ativos com paginação.

        Args:
            page: Número da página (1-indexed).
            page_size: Quantidade de itens por página.

        Returns:
            Tupla com (lista de usuários, total de registros).
        """
        query = self.db.query(Usuario).filter(Usuario.ativo.is_(True))
        total = query.count()
        items = (
            query.order_by(Usuario.username)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def listar_todos(self, page: int = 1, page_size: int = 20) -> tuple[list[Usuario], int]:
        """Lista todos os usuários com paginação.

        Args:
            page: Número da página (1-indexed).
            page_size: Quantidade de itens por página.

        Returns:
            Tupla com (lista de usuários, total de registros).
        """
        query = self.db.query(Usuario)
        total = query.count()
        items = (
            query.order_by(Usuario.username)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
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
        query = self.db.query(Usuario).filter(Usuario.role == role)
        total = query.count()
        items = (
            query.order_by(Usuario.username)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
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
        return usuario

    def atualizar(self, usuario: Usuario, dados: dict) -> Usuario:
        """Atualiza campos de um usuário existente.

        Args:
            usuario: Instância do usuário a ser atualizado.
            dados: Dicionário com campos a serem atualizados.

        Returns:
            Usuario atualizado.
        """
        for campo, valor in dados.items():
            if hasattr(usuario, campo):
                setattr(usuario, campo, valor)
        self.db.commit()
        self.db.refresh(usuario)
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
        return usuario

    def deletar(self, usuario: Usuario) -> None:
        """Delete físico de um usuário (hard delete).

        Use com cuidado em produção.

        Args:
            usuario: Instância do usuário a ser deletado.
        """
        self.db.delete(usuario)
        self.db.commit()
