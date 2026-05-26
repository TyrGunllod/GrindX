from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, registry

reg = registry()
metadata = MetaData()


class IamBase(DeclarativeBase):
    registry = reg
    metadata = metadata
    __table_args__ = {"schema": "iam"}
