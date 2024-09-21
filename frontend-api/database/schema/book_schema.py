from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String
)

from database.schema.database import Base

class BookSchema(Base):
  __tablename__ = "books"
  
  id = Column(Integer, primary_key=True, index=True, unique=True)
  title = Column(String, unique=True, nullable=False)
  publisher = Column(String, nullable=False)
  category = Column(String, nullable=False)
  is_borrowed = Column(Boolean, nullable=False, default=False)
  