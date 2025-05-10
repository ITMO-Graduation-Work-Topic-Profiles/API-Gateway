import typing as tp

from pydantic import AnyUrl, BaseModel, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

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

    @property
    def dsn(self) -> str:
        return f"{self.connection.url}/{self.database}"


class KafkaSchema(BaseModel):
    connection: URLSchema

    @property
    def bootstrap_servers(self) -> str:
        return f"{self.connection.host}:{self.connection.port}"


class Settings(BaseSettings):
    mongo: MongoSchema
    clickhouse: ClickHouseSchema
    kafka: KafkaSchema

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )
