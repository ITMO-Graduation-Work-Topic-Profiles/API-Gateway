import typing as tp

from pydantic import AnyUrl, BaseModel, model_validator
from pydantic_settings import BaseSettings

__all__ = ["Settings"]


class URLSchema(BaseModel):
    scheme: str
    host: str
    port: int
    username: str | None = None
    password: str | None = None

    _url: AnyUrl

    @model_validator(mode="after")
    def validate_url(self) -> tp.Self:
        self._url = AnyUrl.build(
            scheme=self.scheme,
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
        )

        return self

    @property
    def url(self) -> str:
        return str(self._url)


class MongoSchema(BaseModel):
    connection: URLSchema
    database: str


class ClickHouseSchema(BaseModel):
    connection: URLSchema
    database: str


class Settings(BaseSettings):
    mongo: MongoSchema
    clickhouse: ClickHouseSchema
