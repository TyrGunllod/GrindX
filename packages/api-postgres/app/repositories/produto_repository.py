"""
Repositório de acesso a dados para Produto.

Encapsula todas as queries SQL para a tabela produtos.
Nenhuma regra de negócio deve existir nesta camada.
"""

from sqlalchemy import func
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
        return self.db.query(Produto).filter(Produto.id == produto_id).first()

    def listar_ativos(self, page: int = 1, page_size: int = 20) -> tuple[list[Produto], int]:
        """Lista produtos ativos com paginação.

        Args:
            page: Número da página (1-indexed).
            page_size: Quantidade de itens por página.

        Returns:
            Tupla com (lista de produtos, total de registros).
        """
        query = self.db.query(Produto).filter(Produto.ativo.is_(True))
        total = query.count()
        items = (
            query.order_by(Produto.nome)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def listar_todos(self, page: int = 1, page_size: int = 20) -> tuple[list[Produto], int]:
        """Lista todos os produtos com paginação.

        Args:
            page: Número da página (1-indexed).
            page_size: Quantidade de itens por página.

        Returns:
            Tupla com (lista de produtos, total de registros).
        """
        query = self.db.query(Produto)
        total = query.count()
        items = (
            query.order_by(Produto.nome)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def buscar_por_nome(self, nome: str) -> list[Produto]:
        """Busca produtos pelo nome (case-insensitive, parcial).

        Args:
            nome: Termo de busca.

        Returns:
            Lista de produtos que contêm o termo no nome.
        """
        return (
            self.db.query(Produto)
            .filter(func.lower(Produto.nome).contains(nome.lower()))
            .all()
        )

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
