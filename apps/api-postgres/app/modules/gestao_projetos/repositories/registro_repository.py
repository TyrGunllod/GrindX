from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.gestao_projetos.models.registro_tarefa import RegistroTarefa
from app.modules.gestao_projetos.schemas.registro_tarefa import RegistroCreate, RegistroUpdate


class RegistroRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_por_id(self, id: int) -> RegistroTarefa | None:
        stmt = select(RegistroTarefa).where(RegistroTarefa.id == id)
        return self.db.execute(stmt).scalar_one_or_none()

    def listar_por_tarefa(
        self, tarefa_id: int, page: int = 1, page_size: int = 50, tipo: str | None = None,
    ) -> tuple[list[RegistroTarefa], int]:
        stmt_base = select(RegistroTarefa).where(
            RegistroTarefa.tarefa_id == tarefa_id, RegistroTarefa.ativo.is_(True)
        )
        count_base = select(func.count()).select_from(RegistroTarefa).where(
            RegistroTarefa.tarefa_id == tarefa_id, RegistroTarefa.ativo.is_(True)
        )
        if tipo is not None:
            stmt_base = stmt_base.where(RegistroTarefa.tipo == tipo)
            count_base = count_base.where(RegistroTarefa.tipo == tipo)
        total = self.db.scalar(count_base) or 0
        stmt = stmt_base.order_by(RegistroTarefa.criado_em.desc()).offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.scalars(stmt).all())
        return items, total

    def criar(self, tarefa_id: int, dados: RegistroCreate) -> RegistroTarefa:
        obj = RegistroTarefa(tarefa_id=tarefa_id, **dados.model_dump())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def atualizar(self, obj: RegistroTarefa, dados: RegistroUpdate) -> RegistroTarefa:
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(obj, campo, valor)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def desativar(self, obj: RegistroTarefa) -> RegistroTarefa:
        obj.ativo = False
        self.db.commit()
        self.db.refresh(obj)
        return obj
