from typing import List
from models.borrowed_book_model import BorrowedBookModel
from models.user_model import UserModel


class UserBooksModel(UserModel):
    borrowed_books: List[BorrowedBookModel]

    class Config:
        from_attributes = True
