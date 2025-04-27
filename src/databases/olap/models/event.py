import uuid
from datetime import datetime

from clickhouse_sqlalchemy import engines, types
from sqlalchemy import orm

from .base import BaseModel

__all__ = ["EventModel"]


class EventModel(BaseModel):
    __tablename__ = "events"
    __table_args__ = (
        engines.MergeTree(
            order_by=("user_id", "timestamp"),
        ),
    )

    event_id: orm.Mapped[uuid.UUID] = orm.mapped_column(types.UUID, primary_key=True)
    timestamp: orm.Mapped[datetime] = orm.mapped_column(types.DateTime, nullable=False)
    user_id: orm.Mapped[str] = orm.mapped_column(types.String, nullable=False)
    topics: orm.Mapped[list[tuple[str, float]]] = orm.mapped_column(
        types.Nested(
            [
                ("name", types.String),
                ("weight", types.Float32),
            ]
        )
    )
    entities: orm.Mapped[list[tuple[str, float]]] = orm.mapped_column(
        types.Nested(
            [
                ("name", types.String),
                ("weight", types.Float32),
            ]
        )
    )
    sentiment: orm.Mapped[tuple[float, float, float]] = orm.mapped_column(
        types.Tuple(
            [
                ("positive", types.Float32),
                ("negative", types.Float32),
                ("neutral", types.Float32),
            ]
        )
    )
