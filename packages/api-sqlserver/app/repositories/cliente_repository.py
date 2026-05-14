"""
Repositório de acesso a dados para Cliente — SOMENTE LEITURA.

Encapsula todas as queries de consulta na tabela clientes do SQL Server.
Nenhuma operação de escrita é permitida nesta API.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.cliente import Cliente


class ClienteRepository:
    """Repositório read-only para a entidade Cliente."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_por_id(self, cliente_id: int) -> Cliente | None:
        """Busca um cliente pelo ID."""
        return self.db.query(Cliente).filter(Cliente.id == cliente_id).first()

    def buscar_por_cnpj(self, cnpj: str) -> Cliente | None:
        """Busca um cliente pelo CNPJ."""
        return self.db.query(Cliente).filter(Cliente.cnpj == cnpj).first()

    def listar(
        self,
        page: int = 1,
        page_size: int = 20,
        apenas_ativos: bool = True,
        razao_social: str | None = None,
        cidade: str | None = None,
        uf: str | None = None,
    ) -> tuple[list[Cliente], int]:
        """Lista clientes com paginação e filtros opcionais.

        Args:
            page: Número da página (1-indexed).
            page_size: Itens por página.
            apenas_ativos: Se True, retorna somente clientes ativos.
            razao_social: Filtro parcial por razão social.
            cidade: Filtro por cidade.
            uf: Filtro por UF.

        Returns:
            Tupla com (lista de clientes, total de registros).
        """
        query = self.db.query(Cliente)

        if apenas_ativos:
            query = query.filter(Cliente.ativo.is_(True))

        if razao_social:
            query = query.filter(
                func.lower(Cliente.razao_social).contains(razao_social.lower())
            )

        if cidade:
            query = query.filter(
                func.lower(Cliente.cidade) == cidade.lower()
            )

        if uf:
            query = query.filter(Cliente.uf == uf.upper())

        total = query.count()
        items = (
            query.order_by(Cliente.razao_social)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total
