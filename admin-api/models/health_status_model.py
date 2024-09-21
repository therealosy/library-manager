from pydantic import BaseModel
from datetime import datetime


class HealthStatusModel(BaseModel):
    status: str
    time: datetime 
