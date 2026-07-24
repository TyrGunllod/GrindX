from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

metadata = MetaData()
reg = None


class IamBase(DeclarativeBase):
    metadata = metadata
