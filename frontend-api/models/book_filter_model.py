from pydantic import BaseModel

class BookFilterModel(BaseModel):
  title: str | None = None
  category: str | None = None
  publisher: str | None = None