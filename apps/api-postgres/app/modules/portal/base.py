from sqlalchemy.orm import DeclarativeBase

from app.modules.iam.base import metadata, reg


class PortalBase(DeclarativeBase):
    registry = reg
    metadata = metadata
    __table_args__ = {"schema": "portal"}
