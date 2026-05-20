"""
Camada de serviço para Produto.

Contém regras de negócio. Não conhece HTTP nem SQL direto.
Depende do ProdutoRepository para acesso a dados.
"""

import math

import structlog
from shared.exceptions.base import PrecoInvalidoError, ProdutoNaoEncontradoError
from shared.schemas.base import PaginatedResponse

from app.repositories.produto_repository import ProdutoRepository
from app.schemas.produto import ProdutoCreate, ProdutoUpdate

logger = structlog.get_logger(__name__)


class ProdutoService:
    """Serviço com regras de negócio para a entidade Produto."""

    def __init__(self, repository: ProdutoRepository) -> None:
        self.repository = repository

    def buscar_produto(self, produto_id: int):
        """Busca um produto pelo ID.

        Args:
            produto_id: ID do produto.

        Returns:
            Instância do Produto encontrado.

        Raises:
            ProdutoNaoEncontradoError: Se o produto não existir.
        """
        produto = self.repository.buscar_por_id(produto_id)
        if not produto:
            raise ProdutoNaoEncontradoError(produto_id)
        return produto

    def listar_produtos(
        self,
        page: int = 1,
        page_size: int = 20,
        apenas_ativos: bool = True,
    ) -> PaginatedResponse:
        """Lista produtos com paginação.

        Args:
            page: Número da página.
            page_size: Itens por página.
            apenas_ativos: Se True, retorna somente produtos ativos.

        Returns:
            PaginatedResponse com os produtos e metadados de paginação.
        """
        if apenas_ativos:
            items, total = self.repository.listar_ativos(page, page_size)
        else:
            items, total = self.repository.listar_todos(page, page_size)

        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def criar_produto(self, dados: ProdutoCreate):
        """Cria um novo produto após validação de negócio.

        Args:
            dados: Dados validados do produto.

        Returns:
            Produto criado.

        Raises:
            PrecoInvalidoError: Se o preço for inválido.
        """
        if dados.preco <= 0:
            raise PrecoInvalidoError()

        produto = self.repository.criar(dados)
        logger.info(
            "Produto criado",
            produto_id=produto.id,
            nome=produto.nome,
        )
        return produto

    def atualizar_produto(self, produto_id: int, dados: ProdutoUpdate):
        """Atualiza um produto existente.

        Args:
            produto_id: ID do produto a atualizar.
            dados: Campos a serem atualizados.

        Returns:
            Produto atualizado.

        Raises:
            ProdutoNaoEncontradoError: Se o produto não existir.
            PrecoInvalidoError: Se o novo preço for inválido.
        """
        produto = self.buscar_produto(produto_id)

        if dados.preco is not None and dados.preco <= 0:
            raise PrecoInvalidoError()

        produto_atualizado = self.repository.atualizar(produto, dados)
        logger.info("Produto atualizado", produto_id=produto_id)
        return produto_atualizado

    def desativar_produto(self, produto_id: int):
        """Desativa (soft delete) um produto.

        Args:
            produto_id: ID do produto a desativar.

        Returns:
            Produto desativado.

        Raises:
            ProdutoNaoEncontradoError: Se o produto não existir.
        """
        produto = self.buscar_produto(produto_id)
        produto_desativado = self.repository.desativar(produto)
        logger.info("Produto desativado", produto_id=produto_id)
        return produto_desativado
