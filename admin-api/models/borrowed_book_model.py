from datetime import date

from models.book_model import BookModel


class BorrowedBookModel(BookModel):
    date_borrowed: date
    return_date: date
    is_returned: bool

    class Config:
        from_attributes = True
