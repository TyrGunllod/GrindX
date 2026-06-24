from sqlalchemy.orm import DeclarativeBase
from app.modules.iam.base import metadata, reg


class {entity_name}Base(DeclarativeBase):
    registry = reg
    metadata = metadata
    __table_args__ = {"schema": "{schema_name}"}
