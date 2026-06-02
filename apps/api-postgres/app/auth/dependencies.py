"""
Dependencies de autenticação e injeção de dependência.

Fornece as factories para injetar services e o current_user
autenticado via JWT nas rotas do FastAPI.
"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from shared.exceptions.base import TokenInvalidoError
from shared.schemas.auth import TokenPayload
from shared.security.jwt import verificar_jwt
from shared.security.permissions import Role
from sqlalchemy.orm import Session

from app.auth.service import AuthService
from app.core.config import settings
from app.database import get_db

# Scheme que extrai o token do header Authorization: Bearer <token>
_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> TokenPayload:
    """Dependency que extrai e valida o usuário atual do token JWT.

    Extrai o token do header Authorization, decodifica e retorna
    o payload com sub (user_id) e role.

    Args:
        credentials: Credenciais extraídas do header pelo HTTPBearer.

    Returns:
        TokenPayload com dados do usuário autenticado.

    Raises:
        TokenInvalidoError: Se o token estiver ausente ou inválido.
    """
    if not credentials:
        raise TokenInvalidoError()

    return verificar_jwt(credentials.credentials, settings.SECRET_KEY)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Factory para o AuthService com injeção da sessão do banco.

    Args:
        db: Sessão do SQLAlchemy injetada via Depends.

    Returns:
        Instância do AuthService.
    """
    return AuthService(db)


from app.modules.gestao_projetos.repositories.projeto_repository import ProjetoRepository
from app.modules.gestao_projetos.services.projeto_service import ProjetoService
from app.modules.gestao_projetos.repositories.tarefa_repository import TarefaRepository
from app.modules.gestao_projetos.services.tarefa_service import TarefaService
from app.modules.gestao_projetos.repositories.registro_repository import RegistroRepository
from app.modules.gestao_projetos.services.registro_service import RegistroService
from app.modules.gestao_projetos.repositories.recurso_repository import RecursoRepository
from app.modules.gestao_projetos.services.recurso_service import RecursoService
from app.modules.gestao_projetos.repositories.dashboard_repository import DashboardRepository
from app.modules.gestao_projetos.services.dashboard_service import DashboardService
from app.modules.gestao_projetos.repositories.cronograma_repository import CronogramaRepository
from app.modules.gestao_projetos.services.cronograma_service import CronogramaService


def get_gestao_projetos_service(db: Session = Depends(get_db)) -> ProjetoService:
    repository = ProjetoRepository(db)
    return ProjetoService(repository)


def get_gestao_projetos_tarefa_service(db: Session = Depends(get_db)) -> TarefaService:
    repository = TarefaRepository(db)
    return TarefaService(repository)


def get_gestao_projetos_registro_service(db: Session = Depends(get_db)) -> RegistroService:
    repository = RegistroRepository(db)
    return RegistroService(repository)


def get_gestao_projetos_recurso_service(db: Session = Depends(get_db)) -> RecursoService:
    repository = RecursoRepository(db)
    return RecursoService(repository)


def get_gestao_projetos_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    repository = DashboardRepository(db)
    return DashboardService(repository)


def get_gestao_projetos_cronograma_service(db: Session = Depends(get_db)) -> CronogramaService:
    repository = CronogramaRepository(db)
    return CronogramaService(repository)


# --- Versões vinculadas das permissões ---



def require_role(*roles_permitidas: str | Role):
    """Atalho para shared.require_role vinculado ao get_current_user desta API."""
    from shared.security import permissions

    return permissions.require_role(*roles_permitidas, get_user=get_current_user)


def require_role_or_higher(role_minimo: str | Role):
    """Atalho para shared.require_role_or_higher vinculado ao get_current_user desta API."""
    from shared.security import permissions

    return permissions.require_role_or_higher(role_minimo, get_user=get_current_user)
