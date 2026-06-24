from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.{module_name}.models.{module_name} import {entity_name}
from app.modules.{module_name}.schemas.{module_name} import {entity_name}Create, {entity_name}Update


class {entity_name}Repository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_por_id(self, id: int) -> {entity_name} | None:
        stmt = select({entity_name}).where({entity_name}.id == id)
        return self.db.execute(stmt).scalar_one_or_none()

    def listar_todos(self, page: int = 1, page_size: int = 20) -> tuple[list[{entity_name}], int]:
        count_stmt = select(func.count()).select_from({entity_name})
        total = self.db.scalar(count_stmt) or 0
        stmt = select({entity_name}).order_by({entity_name}.id).offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.scalars(stmt).all())
        return items, total

    def criar(self, dados: {entity_name}Create) -> {entity_name}:
        obj = {entity_name}(**dados.model_dump())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def atualizar(self, obj: {entity_name}, dados: {entity_name}Update) -> {entity_name}:
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(obj, campo, valor)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def desativar(self, obj: {entity_name}) -> {entity_name}:
        obj.ativo = False
        self.db.commit()
        self.db.refresh(obj)
        return obj

    # === Optional custom queries (uncomment as needed) ===

    # def buscar_por_nome(self, nome: str) -> list[{entity_name}]:
    #     stmt = select({entity_name}).where({entity_name}.nome.ilike(f"%{nome}%"))
    #     return list(self.db.scalars(stmt).all())
