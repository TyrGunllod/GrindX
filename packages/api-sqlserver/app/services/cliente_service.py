"""
Camada de serviço para Cliente — somente consulta.

Contém regras de negócio de leitura. Nenhuma operação de escrita.
"""

import math

import structlog

from app.repositories.cliente_repository import ClienteRepository
from shared.exceptions.base import ClienteNaoEncontradoError, CnpjNaoEncontradoError
from shared.schemas.base import PaginatedResponse

logger = structlog.get_logger(__name__)


class ClienteService:
    """Serviço read-only para a entidade Cliente."""

    def __init__(self, repository: ClienteRepository) -> None:
        self.repository = repository

    def buscar_cliente(self, cliente_id: int):
        """Busca um cliente pelo ID.

        Raises:
            ClienteNaoEncontradoError: Se o cliente não existir.
        """
        cliente = self.repository.buscar_por_id(cliente_id)
        if not cliente:
            raise ClienteNaoEncontradoError(cliente_id)
        return cliente

    def buscar_por_cnpj(self, cnpj: str):
        """Busca um cliente pelo CNPJ.

        Raises:
            CnpjNaoEncontradoError: Se nenhum cliente for encontrado.
        """
        cliente = self.repository.buscar_por_cnpj(cnpj)
        if not cliente:
            raise CnpjNaoEncontradoError(cnpj)
        return cliente

    def listar_clientes(
        self,
        page: int = 1,
        page_size: int = 20,
        apenas_ativos: bool = True,
        razao_social: str | None = None,
        cidade: str | None = None,
        uf: str | None = None,
    ) -> PaginatedResponse:
        """Lista clientes com paginação e filtros."""
        items, total = self.repository.listar(
            page=page,
            page_size=page_size,
            apenas_ativos=apenas_ativos,
            razao_social=razao_social,
            cidade=cidade,
            uf=uf,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
