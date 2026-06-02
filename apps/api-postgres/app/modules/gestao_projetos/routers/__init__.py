from app.modules.gestao_projetos.routers.projeto_router import router as projeto_router
from app.modules.gestao_projetos.routers.tarefa_router import router as tarefa_router
from app.modules.gestao_projetos.routers.recurso_router import router as recurso_router
from app.modules.gestao_projetos.routers.dashboard_router import router as dashboard_router
from app.modules.gestao_projetos.routers.cronograma_router import router as cronograma_router

__all__ = [
    "projeto_router", "tarefa_router", "recurso_router",
    "dashboard_router", "cronograma_router",
]
