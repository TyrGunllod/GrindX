from sqlalchemy import text
from sqlalchemy.orm import Session


class CronogramaRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar_tarefas_gantt(
        self, page: int = 1, page_size: int = 100, projeto_id: int | None = None,
    ) -> tuple[list[dict], int]:
        base_from = """
            FROM tarefas t
            LEFT JOIN projetos p ON t.projeto_id = p.id
            LEFT JOIN recursos r ON t.responsavel_id = r.id
            LEFT JOIN usuarios u ON r.user_id = u.id
        """
        where_clause = "WHERE t.ativo = 1"
        params: dict = {}
        if projeto_id is not None:
            where_clause += " AND t.projeto_id = :projeto_id"
            params["projeto_id"] = projeto_id

        count_sql = text(f"SELECT COUNT(*) {base_from} {where_clause}")
        total = self.db.scalar(count_sql, params) or 0

        offset = (page - 1) * page_size
        data_sql = text(f"""
            SELECT t.id, t.titulo, t.status, t.prioridade,
                   t.data_inicio, t.data_fim, t.progresso,
                   t.projeto_id, p.nome AS project_name, p.cor AS project_color,
                   t.responsavel_id, u.nome_completo AS assignee_name, r.cor AS assignee_color
            {base_from}
            {where_clause}
            ORDER BY t.data_inicio, t.id
            LIMIT :limit OFFSET :offset
        """)
        params["limit"] = page_size
        params["offset"] = offset
        rows = self.db.execute(data_sql, params).mappings().all()
        items = [dict(row) for row in rows]
        return items, total
