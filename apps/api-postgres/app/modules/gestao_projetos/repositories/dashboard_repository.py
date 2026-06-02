from datetime import date, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session


class DashboardRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_metrics(self) -> dict:
        queries = {
            "total_projetos": "SELECT COUNT(*) FROM projetos WHERE ativo = 1",
            "projetos_ativos": "SELECT COUNT(*) FROM projetos WHERE status = 'active' AND ativo = 1",
            "total_tarefas": "SELECT COUNT(*) FROM tarefas WHERE ativo = 1",
            "tarefas_concluidas": "SELECT COUNT(*) FROM tarefas WHERE status = 'done' AND ativo = 1",
            "tarefas_em_progresso": "SELECT COUNT(*) FROM tarefas WHERE status = 'in-progress' AND ativo = 1",
            "tarefas_a_fazer": "SELECT COUNT(*) FROM tarefas WHERE status = 'todo' AND ativo = 1",
            "total_recursos": "SELECT COUNT(*) FROM recursos WHERE alocado = 1",
            "progresso_geral": "SELECT COALESCE(AVG(progresso), 0) FROM tarefas WHERE ativo = 1",
        }
        result = {}
        for key, sql in queries.items():
            result[key] = self.db.execute(text(sql)).scalar() or 0
        result["progresso_geral"] = round(result["progresso_geral"])
        return result

    def buscar_proximos_prazos(self) -> list[dict]:
        hoje = date.today()
        limite = hoje + timedelta(days=7)
        sql = """
            SELECT t.id, t.titulo, t.data_fim, t.projeto_id,
                   p.nome AS project_name, p.cor AS project_color
            FROM tarefas t
            JOIN projetos p ON t.projeto_id = p.id
            WHERE t.ativo = 1 AND t.status != 'done'
              AND t.data_fim BETWEEN :hoje AND :limite
            ORDER BY t.data_fim ASC
            LIMIT 5
        """
        rows = self.db.execute(text(sql), {"hoje": hoje, "limite": limite}).mappings().all()
        result = []
        for row in rows:
            dias = (row["data_fim"] - hoje).days
            result.append({
                "id": row["id"],
                "titulo": row["titulo"],
                "data_fim": row["data_fim"],
                "dias_restantes": max(dias, 0),
                "projeto_id": row["projeto_id"],
                "project_name": row["project_name"],
                "project_color": row["project_color"],
            })
        return result

    def buscar_tarefas_atrasadas(self) -> tuple[list[dict], int]:
        hoje = date.today()
        sql_lista = """
            SELECT t.id, t.titulo, t.data_fim, t.projeto_id,
                   p.nome AS project_name, p.cor AS project_color
            FROM tarefas t
            JOIN projetos p ON t.projeto_id = p.id
            WHERE t.ativo = 1 AND t.status != 'done'
              AND t.data_fim < :hoje
            ORDER BY t.data_fim ASC
            LIMIT 5
        """
        sql_total = """
            SELECT COUNT(*) FROM tarefas
            WHERE ativo = 1 AND status != 'done' AND data_fim < :hoje
        """
        rows = self.db.execute(text(sql_lista), {"hoje": hoje}).mappings().all()
        total = self.db.execute(text(sql_total), {"hoje": hoje}).scalar() or 0
        result = []
        for row in rows:
            dias = (hoje - row["data_fim"]).days
            result.append({
                "id": row["id"],
                "titulo": row["titulo"],
                "data_fim": row["data_fim"],
                "dias_atraso": max(dias, 1),
                "projeto_id": row["projeto_id"],
                "project_name": row["project_name"],
                "project_color": row["project_color"],
            })
        return result, total

    def buscar_progresso_projetos(self) -> list[dict]:
        sql = """
            SELECT p.id, p.nome, p.cor,
                   COUNT(t.id) AS total_tarefas,
                   COALESCE(SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END), 0) AS tarefas_concluidas,
                   COALESCE(AVG(t.progresso), 0) AS progresso
            FROM projetos p
            LEFT JOIN tarefas t ON t.projeto_id = p.id AND t.ativo = 1
            WHERE p.ativo = 1
            GROUP BY p.id, p.nome, p.cor
            ORDER BY p.nome ASC
        """
        rows = self.db.execute(text(sql)).mappings().all()
        return [
            {
                "id": r["id"],
                "nome": r["nome"],
                "cor": r["cor"],
                "total_tarefas": r["total_tarefas"],
                "tarefas_concluidas": r["tarefas_concluidas"],
                "progresso": round(r["progresso"]),
            }
            for r in rows
        ]

    def buscar_carga_trabalho(self) -> list[dict]:
        sql = """
            SELECT r.id, r.user_id AS nome, r.cor,
                   COALESCE(SUM(CASE WHEN t.status != 'done' THEN 1 ELSE 0 END), 0) AS tarefas_ativas,
                   COALESCE(SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END), 0) AS tarefas_concluidas
            FROM recursos r
            LEFT JOIN tarefas t ON t.responsavel_id = r.id AND t.ativo = 1
            WHERE r.alocado = 1
            GROUP BY r.id, r.user_id, r.cor
            ORDER BY r.id ASC
        """
        rows = self.db.execute(text(sql)).mappings().all()
        return [
            {
                "id": r["id"],
                "nome": r["nome"],
                "cor": r["cor"],
                "tarefas_ativas": r["tarefas_ativas"],
                "tarefas_concluidas": r["tarefas_concluidas"],
            }
            for r in rows
        ]
