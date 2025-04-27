import typing as tp

from beanie import Document, Indexed

from .mixins import TimestampDocumentMixin

__all__ = ["UserDocument"]


class UserDocument(Document, TimestampDocumentMixin):
    user_id: tp.Annotated[str, Indexed(unique=True)]

    class Settings:
        name = "users"
        keep_nulls = False
