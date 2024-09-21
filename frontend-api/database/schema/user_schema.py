from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime

from database.schema.database import Base


class UserSchema(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    email = Column(String, unique=True, nullable=False)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    joined_on = Column(DateTime, nullable=False, default=datetime.now())
