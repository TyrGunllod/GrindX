from app.modules.gestao_projetos.repositories.dashboard_repository import DashboardRepository
from app.modules.gestao_projetos.schemas.dashboard import (
    CargaTrabalho,
    DashboardMetrics,
    DashboardResponse,
    ProximoPrazo,
    ProgressoProjeto,
    TarefaAtrasada,
)


class DashboardService:
    def __init__(self, repository: DashboardRepository) -> None:
        self.repository = repository

    def carregar_dados(self) -> DashboardResponse:
        metrics_data = self.repository.buscar_metrics()
        metrics = DashboardMetrics(**metrics_data)

        proximos_prazos = [ProximoPrazo(**p) for p in self.repository.buscar_proximos_prazos()]
        tarefas_atrasadas_data, total_atrasadas = self.repository.buscar_tarefas_atrasadas()
        tarefas_atrasadas = [TarefaAtrasada(**t) for t in tarefas_atrasadas_data]
        progresso_projetos = [ProgressoProjeto(**p) for p in self.repository.buscar_progresso_projetos()]
        carga_trabalho = [CargaTrabalho(**c) for c in self.repository.buscar_carga_trabalho()]

        return DashboardResponse(
            metrics=metrics,
            proximos_prazos=proximos_prazos,
            tarefas_atrasadas=tarefas_atrasadas,
            total_tarefas_atrasadas=total_atrasadas,
            progresso_projetos=progresso_projetos,
            carga_trabalho=carga_trabalho,
        )
