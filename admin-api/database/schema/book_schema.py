from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String
)

from sqlalchemy.orm import relationship

from database.schema.database import Base

class BookSchema(Base):
  __tablename__ = "books"
  
  id = Column(Integer, primary_key=True, index=True, unique=True)
  title = Column(String, unique=True, nullable=False)
  publisher = Column(String, nullable=False)
  category = Column(String, nullable=False)
  
  users = relationship("BorrowEntrySchema", back_populates="book")
  
  