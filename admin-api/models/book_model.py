from typing import Any
from pydantic import BaseModel
from datetime import date


class BookModel(BaseModel):
    id: int | None = None
    title: str
    publisher: str
    category: str

    class Config:
        from_attributes = True
