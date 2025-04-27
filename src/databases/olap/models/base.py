from sqlalchemy import MetaData, orm

__all__ = ["BaseModel"]

metadata = MetaData()


class BaseModel(orm.DeclarativeBase):
    metadata = metadata
