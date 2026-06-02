from datetime import date

from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    total_projetos: int
    projetos_ativos: int
    total_tarefas: int
    tarefas_concluidas: int
    tarefas_em_progresso: int
    tarefas_a_fazer: int
    total_recursos: int
    progresso_geral: int


class ProximoPrazo(BaseModel):
    id: int
    titulo: str
    data_fim: date
    dias_restantes: int
    projeto_id: int | None
    project_name: str | None
    project_color: str | None


class TarefaAtrasada(BaseModel):
    id: int
    titulo: str
    data_fim: date
    dias_atraso: int
    projeto_id: int | None
    project_name: str | None
    project_color: str | None


class ProgressoProjeto(BaseModel):
    id: int
    nome: str
    cor: str
    total_tarefas: int
    tarefas_concluidas: int
    progresso: int


class CargaTrabalho(BaseModel):
    id: int
    nome: str
    cor: str
    tarefas_ativas: int
    tarefas_concluidas: int


class DashboardResponse(BaseModel):
    metrics: DashboardMetrics
    proximos_prazos: list[ProximoPrazo]
    tarefas_atrasadas: list[TarefaAtrasada]
    total_tarefas_atrasadas: int
    progresso_projetos: list[ProgressoProjeto]
    carga_trabalho: list[CargaTrabalho]
