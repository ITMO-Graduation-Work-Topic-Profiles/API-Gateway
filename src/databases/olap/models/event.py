from clickhouse_sqlalchemy import engines, types
from sqlalchemy import Column

from .base import Base

__all__ = ["EventModel"]


class EventModel(Base):
    __tablename__ = "events"
    __table_args__ = (
        engines.MergeTree(
            order_by=("user_id", "timestamp"),
        ),
    )

    event_id = Column(types.UUID, primary_key=True)
    timestamp = Column(types.DateTime, nullable=False)
    user_id = Column(types.String, nullable=False)
    topics = Column(
        types.Nested(
            [
                ("name", types.String),
                ("weight", types.Float32),
            ]
        )
    )
    entities = Column(
        types.Nested(
            [
                ("name", types.String),
                ("weight", types.Float32),
            ]
        )
    )
    sentiment = Column(
        types.Tuple(
            [
                ("positive", types.Float32),
                ("negative", types.Float32),
                ("neutral", types.Float32),
            ]
        )
    )
