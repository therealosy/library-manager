from pydantic import BaseModel
from datetime import datetime

class BookModel(BaseModel):
  id: int | None = None
  title: str
  publisher: str
  category: str
  is_borrowed: bool = False

  class Config:
        from_attributes = True