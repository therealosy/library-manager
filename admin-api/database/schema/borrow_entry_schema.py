from datetime import date
from typing import List
from sqlalchemy import Boolean, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from database.schema.database import Base


class BorrowEntrySchema(Base):
    __tablename__ = "borrow_entries"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    book_id = Column(
        Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date_borrowed = Column(Date, nullable=False, default=date.today())
    return_date = Column(Date, nullable=False)
    is_returned = Column(Boolean, nullable=False, default=False)


BorrowEntrySchema.user = relationship("UserSchema", back_populates="borrowed_books")
BorrowEntrySchema.book = relationship("BookSchema", back_populates="users")
