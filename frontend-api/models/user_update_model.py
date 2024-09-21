from pydantic import BaseModel

class UserUpdateModel(BaseModel):
  email: str | None = None
  firstname: str | None = None
  lastname: str | None = None