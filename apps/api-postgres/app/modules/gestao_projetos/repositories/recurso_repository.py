from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.gestao_projetos.models.recurso import Recurso
from app.modules.gestao_projetos.schemas.recurso import RecursoCreate, RecursoUpdate


class RecursoRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_por_id(self, id: int) -> Recurso | None:
        stmt = select(Recurso).where(Recurso.id == id)
        return self.db.execute(stmt).scalar_one_or_none()

    def listar_todos(
        self, page: int = 1, page_size: int = 20, projeto_id: int | None = None,
    ) -> tuple[list[Recurso], int]:
        stmt_base = select(Recurso).where(Recurso.alocado.is_(True))
        count_base = select(func.count()).select_from(Recurso).where(Recurso.alocado.is_(True))
        if projeto_id is not None:
            stmt_base = stmt_base.where(Recurso.projeto_id == projeto_id)
            count_base = count_base.where(Recurso.projeto_id == projeto_id)
        total = self.db.scalar(count_base) or 0
        stmt = stmt_base.order_by(Recurso.id).offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.scalars(stmt).all())
        return items, total

    def buscar_por_user_projeto(self, user_id: int, projeto_id: int) -> Recurso | None:
        stmt = select(Recurso).where(Recurso.user_id == user_id, Recurso.projeto_id == projeto_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def criar(self, dados: RecursoCreate) -> Recurso:
        obj = Recurso(**dados.model_dump())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def atualizar(self, obj: Recurso, dados: RecursoUpdate) -> Recurso:
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(obj, campo, valor)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def desalocar(self, obj: Recurso) -> Recurso:
        obj.alocado = False
        self.db.commit()
        self.db.refresh(obj)
        return obj
