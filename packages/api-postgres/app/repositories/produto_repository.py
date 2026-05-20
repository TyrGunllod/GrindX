"""
Repositório de acesso a dados para Produto.

Encapsula todas as queries SQL para a tabela produtos.
Nenhuma regra de negócio deve existir nesta camada.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.produto import Produto
from app.schemas.produto import ProdutoCreate, ProdutoUpdate


class ProdutoRepository:
    """Repositório CRUD para a entidade Produto."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_por_id(self, produto_id: int) -> Produto | None:
        """Busca um produto pelo ID.

        Args:
            produto_id: ID do produto.

        Returns:
            Produto encontrado ou None.
        """
        stmt = select(Produto).where(Produto.id == produto_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def listar_ativos(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[Produto], int]:
        """Lista produtos ativos com paginação.

        Args:
            page: Número da página (1-indexed).
            page_size: Quantidade de itens por página.

        Returns:
            Tupla com (lista de produtos, total de registros).
        """
        # Query para total
        count_stmt = (
            select(func.count()).select_from(Produto).where(Produto.ativo.is_(True))
        )
        total = self.db.scalar(count_stmt) or 0

        # Query para itens
        stmt = (
            select(Produto)
            .where(Produto.ativo.is_(True))
            .order_by(Produto.nome)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(self.db.scalars(stmt).all())
        return items, total

    def listar_todos(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[Produto], int]:
        """Lista todos os produtos com paginação.

        Args:
            page: Número da página (1-indexed).
            page_size: Quantidade de itens por página.

        Returns:
            Tupla com (lista de produtos, total de registros).
        """
        # Query para total
        count_stmt = select(func.count()).select_from(Produto)
        total = self.db.scalar(count_stmt) or 0

        # Query para itens
        stmt = (
            select(Produto)
            .order_by(Produto.nome)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(self.db.scalars(stmt).all())
        return items, total

    def buscar_por_nome(self, nome: str) -> list[Produto]:
        """Busca produtos pelo nome (case-insensitive, parcial).

        Args:
            nome: Termo de busca.

        Returns:
            Lista de produtos que contêm o termo no nome.
        """
        stmt = select(Produto).where(func.lower(Produto.nome).contains(nome.lower()))
        return list(self.db.scalars(stmt).all())

    def criar(self, dados: ProdutoCreate) -> Produto:
        """Cria um novo produto no banco.

        Args:
            dados: Dados validados do novo produto.

        Returns:
            Produto criado com ID gerado.
        """
        produto = Produto(**dados.model_dump())
        self.db.add(produto)
        self.db.commit()
        self.db.refresh(produto)
        return produto

    def atualizar(self, produto: Produto, dados: ProdutoUpdate) -> Produto:
        """Atualiza campos de um produto existente.

        Args:
            produto: Instância do produto a ser atualizado.
            dados: Dados parciais para atualização.

        Returns:
            Produto atualizado.
        """
        campos_atualizar = dados.model_dump(exclude_unset=True)
        for campo, valor in campos_atualizar.items():
            setattr(produto, campo, valor)
        self.db.commit()
        self.db.refresh(produto)
        return produto

    def desativar(self, produto: Produto) -> Produto:
        """Soft delete — desativa o produto.

        Args:
            produto: Instância do produto a ser desativado.

        Returns:
            Produto com ativo=False.
        """
        produto.ativo = False
        self.db.commit()
        self.db.refresh(produto)
        return produto
