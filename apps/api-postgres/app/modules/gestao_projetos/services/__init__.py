from app.modules.gestao_projetos.services.projeto_service import ProjetoService
from app.modules.gestao_projetos.services.tarefa_service import TarefaService
from app.modules.gestao_projetos.services.registro_service import RegistroService
from app.modules.gestao_projetos.services.recurso_service import RecursoService
from app.modules.gestao_projetos.services.dashboard_service import DashboardService
from app.modules.gestao_projetos.services.cronograma_service import CronogramaService

__all__ = [
    "ProjetoService", "TarefaService", "RegistroService",
    "RecursoService", "DashboardService", "CronogramaService",
]
