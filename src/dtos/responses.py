from pydantic import BaseModel

__all__ = ["MessageResponseDTO"]


class MessageResponseDTO(BaseModel):
    message: str
