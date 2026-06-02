from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.gestao_projetos.models.projeto import Projeto
from app.modules.gestao_projetos.schemas.projeto import ProjetoCreate, ProjetoUpdate


class ProjetoRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_por_id(self, id: int) -> Projeto | None:
        stmt = select(Projeto).where(Projeto.id == id)
        return self.db.execute(stmt).scalar_one_or_none()

    def listar_todos(self, page: int = 1, page_size: int = 20) -> tuple[list[Projeto], int]:
        count_stmt = select(func.count()).select_from(Projeto)
        total = self.db.scalar(count_stmt) or 0
        stmt = select(Projeto).order_by(Projeto.id).offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.scalars(stmt).all())
        return items, total

    def listar_ativos(self) -> list[Projeto]:
        stmt = select(Projeto).where(Projeto.ativo.is_(True)).order_by(Projeto.nome)
        return list(self.db.scalars(stmt).all())

    def buscar_por_nome(self, nome: str) -> list[Projeto]:
        stmt = select(Projeto).where(Projeto.nome.ilike(f"%{nome}%"))
        return list(self.db.scalars(stmt).all())

    def criar(self, dados: ProjetoCreate) -> Projeto:
        obj = Projeto(**dados.model_dump())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def atualizar(self, obj: Projeto, dados: ProjetoUpdate) -> Projeto:
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(obj, campo, valor)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def desativar(self, obj: Projeto) -> Projeto:
        obj.ativo = False
        self.db.commit()
        self.db.refresh(obj)
        return obj
