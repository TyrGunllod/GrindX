from datetime import date

from pydantic import BaseModel


class TarefaGanttResponse(BaseModel):
    id: int
    titulo: str
    status: str
    prioridade: str
    data_inicio: date
    data_fim: date
    progresso: int
    projeto_id: int | None
    project_name: str | None
    project_color: str | None
    responsavel_id: int | None
    assignee_name: str | None
    assignee_color: str | None
