from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.gestao_projetos.models.tarefa import Tarefa
from app.modules.gestao_projetos.schemas.tarefa import TarefaCreate, TarefaUpdate


class TarefaRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_por_id(self, id: int) -> Tarefa | None:
        stmt = select(Tarefa).where(Tarefa.id == id)
        return self.db.execute(stmt).scalar_one_or_none()

    def listar_todos(
        self, page: int = 1, page_size: int = 20,
        projeto_id: int | None = None, status: str | None = None,
    ) -> tuple[list[Tarefa], int]:
        stmt_base = select(Tarefa).where(Tarefa.ativo.is_(True))
        count_base = select(func.count()).select_from(Tarefa).where(Tarefa.ativo.is_(True))
        if projeto_id is not None:
            stmt_base = stmt_base.where(Tarefa.projeto_id == projeto_id)
            count_base = count_base.where(Tarefa.projeto_id == projeto_id)
        if status is not None:
            stmt_base = stmt_base.where(Tarefa.status == status)
            count_base = count_base.where(Tarefa.status == status)
        total = self.db.scalar(count_base) or 0
        stmt = stmt_base.order_by(Tarefa.data_inicio).offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.scalars(stmt).all())
        return items, total

    def criar(self, dados: TarefaCreate) -> Tarefa:
        obj = Tarefa(**dados.model_dump())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def atualizar(self, obj: Tarefa, dados: TarefaUpdate) -> Tarefa:
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(obj, campo, valor)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def desativar(self, obj: Tarefa) -> Tarefa:
        obj.ativo = False
        self.db.commit()
        self.db.refresh(obj)
        return obj
