from datetime import datetime

from beanie import Insert, Replace, SaveChanges, Update, before_event
from pydantic import BaseModel, Field

from ....utils.dates import utcnow

__all__ = ["TimestampDocumentMixin"]


class TimestampDocumentMixin(BaseModel):
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime | None = None

    @before_event(Insert)
    def set_created_at(self) -> None:
        self.created_at = utcnow()

    @before_event(Update, SaveChanges, Replace)
    def set_updated_at(self) -> None:
        self.updated_at = utcnow()
