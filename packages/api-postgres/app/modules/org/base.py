from sqlalchemy.orm import DeclarativeBase

from app.modules.iam.base import reg, metadata


class OrgBase(DeclarativeBase):
    registry = reg
    metadata = metadata
    __table_args__ = {"schema": "org"}
