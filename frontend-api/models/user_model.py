from pydantic import BaseModel
from datetime import datetime

class UserModel(BaseModel):
  id: int | None = None
  email: str
  firstname: str
  lastname: str
  joined_on: datetime = datetime.now()
  
  class Config:
        from_attributes = True