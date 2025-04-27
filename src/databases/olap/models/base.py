from clickhouse_sqlalchemy import get_declarative_base
from sqlalchemy import MetaData

__all__ = ["Base"]

metadata = MetaData()
Base = get_declarative_base(metadata=metadata)
