from pydantic import BaseModel


class BookBorrowModel(BaseModel):
    book_title: str
    user_email: str
    borrow_duration_days: int
