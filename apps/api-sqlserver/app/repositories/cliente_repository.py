"""
Repositório de acesso a dados para Cliente — SOMENTE LEITURA.

Encapsula todas as queries de consulta na tabela clientes do SQL Server.
Nenhuma operação de escrita é permitida nesta API.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.cliente import Cliente


class ClienteRepository:
    """Repositório read-only para a entidade Cliente."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_por_id(self, cliente_id: int) -> Cliente | None:
        """Busca um cliente pelo ID."""
        stmt = select(Cliente).where(Cliente.id == cliente_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def buscar_por_cnpj(self, cnpj: str) -> Cliente | None:
        """Busca um cliente pelo CNPJ."""
        stmt = select(Cliente).where(Cliente.cnpj == cnpj)
        return self.db.execute(stmt).scalar_one_or_none()

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
        stmt = select(Cliente)

        if apenas_ativos:
            stmt = stmt.where(Cliente.ativo.is_(True))

        if razao_social:
            stmt = stmt.where(
                func.lower(Cliente.razao_social).contains(razao_social.lower())
            )

        if cidade:
            stmt = stmt.where(func.lower(Cliente.cidade) == cidade.lower())

        if uf:
            stmt = stmt.where(Cliente.uf == uf.upper())

        # Query para total (clonamos o stmt atual e trocamos o que selecionamos)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.scalar(count_stmt) or 0

        # Query para itens
        stmt = (
            stmt.order_by(Cliente.razao_social)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(self.db.scalars(stmt).all())
        return items, total
