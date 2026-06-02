from app.modules.gestao_projetos.schemas.projeto import ProjetoCreate, ProjetoUpdate, ProjetoResponse
from app.modules.gestao_projetos.schemas.tarefa import TarefaCreate, TarefaUpdate, TarefaResponse
from app.modules.gestao_projetos.schemas.registro_tarefa import RegistroCreate, RegistroUpdate, RegistroResponse
from app.modules.gestao_projetos.schemas.recurso import RecursoCreate, RecursoUpdate, RecursoResponse
from app.modules.gestao_projetos.schemas.dashboard import (
    DashboardMetrics,
    DashboardResponse,
    ProximoPrazo,
    TarefaAtrasada,
    ProgressoProjeto,
    CargaTrabalho,
)
from app.modules.gestao_projetos.schemas.cronograma import TarefaGanttResponse

__all__ = [
    "ProjetoCreate", "ProjetoUpdate", "ProjetoResponse",
    "TarefaCreate", "TarefaUpdate", "TarefaResponse",
    "RegistroCreate", "RegistroUpdate", "RegistroResponse",
    "RecursoCreate", "RecursoUpdate", "RecursoResponse",
    "DashboardMetrics", "DashboardResponse", "ProximoPrazo",
    "TarefaAtrasada", "ProgressoProjeto", "CargaTrabalho",
    "TarefaGanttResponse",
]
