from app.modules.gestao_projetos.repositories.projeto_repository import ProjetoRepository
from app.modules.gestao_projetos.repositories.tarefa_repository import TarefaRepository
from app.modules.gestao_projetos.repositories.registro_repository import RegistroRepository
from app.modules.gestao_projetos.repositories.recurso_repository import RecursoRepository
from app.modules.gestao_projetos.repositories.dashboard_repository import DashboardRepository
from app.modules.gestao_projetos.repositories.cronograma_repository import CronogramaRepository

__all__ = [
    "ProjetoRepository", "TarefaRepository", "RegistroRepository",
    "RecursoRepository", "DashboardRepository", "CronogramaRepository",
]
