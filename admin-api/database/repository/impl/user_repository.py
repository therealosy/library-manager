from typing import List
from sqlalchemy.orm import Session
from database.repository.meta.user_repository_meta import UserRepositoryMeta
from database.schema.book_schema import BookSchema
from database.schema.borrow_entry_schema import BorrowEntrySchema
from database.schema.user_schema import UserSchema
from models.book_model import BookModel
from models.borrowed_book_model import BorrowedBookModel
from models.user_books_model import UserBooksModel
from models.user_model import UserModel
from models.user_update_model import UserUpdateModel
from utils.dependecy_resolver import ResolveDependency
from utils.logger_utility import getlogger


class UserRepository(UserRepositoryMeta):

    _logger = getlogger(name="UserRepository")

    def __init__(self, db: Session = ResolveDependency(Session)) -> None:
        self.db = db

    def save(self, user: UserSchema) -> UserModel:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self.db.query(UserSchema).filter(UserSchema.email == user.email).first()

    def get_by_id(self, id: int) -> UserModel:
        return self.db.query(UserSchema).filter(UserSchema.id == id).first()

    def get_by_email(self, email: str) -> UserModel:
        return self.db.query(UserSchema).filter(UserSchema.email == email).first()

    def get_all(self) -> List[UserModel]:
        return self.db.query(UserSchema).all()

    def get_all_books_including_returned(self) -> List[UserBooksModel]:
        results = (
            self.db.query(UserSchema, BookSchema, BorrowEntrySchema)
            .select_from(UserSchema)
            .join(BorrowEntrySchema)
            .join(BookSchema)
            .all()
        )
        users_books = {}

        for user, book, borrow_entry in results:
            if user.id not in users_books:
                self._logger.debug(f"user id: {user.id}")
                users_books[user.id] = {
                    "id": user.id,
                    "email": user.email,
                    "firstname": user.firstname,
                    "lastname": user.lastname,
                    "joined_on": user.joined_on,
                    "borrowed_books": [],
                }
            users_books[user.id]["borrowed_books"].append(
                BorrowedBookModel(
                    id=book.id,
                    title=book.title,
                    publisher=book.publisher,
                    category=book.category,
                    date_borrowed=borrow_entry.date_borrowed,
                    return_date=borrow_entry.return_date,
                    is_returned=borrow_entry.is_returned,
                )
            )

        return list(users_books.values())

    def get_all_users_with_currently_borrowed_books(self) -> List[UserBooksModel]:
        results = (
            self.db.query(UserSchema, BookSchema, BorrowEntrySchema)
            .select_from(UserSchema)
            .join(BorrowEntrySchema)
            .filter(BorrowEntrySchema.is_returned == False)
            .join(BookSchema)
            .all()
        )
        users_books = {}

        for user, book, borrow_entry in results:
            if user.id not in users_books:
                self._logger.debug(f"user id: {user.id}")
                users_books[user.id] = {
                    "id": user.id,
                    "email": user.email,
                    "firstname": user.firstname,
                    "lastname": user.lastname,
                    "joined_on": user.joined_on,
                    "borrowed_books": [],
                }
            users_books[user.id]["borrowed_books"].append(
                BorrowedBookModel(
                    id=book.id,
                    title=book.title,
                    publisher=book.publisher,
                    category=book.category,
                    date_borrowed=borrow_entry.date_borrowed,
                    return_date=borrow_entry.return_date,
                    is_returned=borrow_entry.is_returned,
                )
            )

        return list(users_books.values())

    def update(self, id: int, user_update: UserUpdateModel) -> UserModel:
        self.db.query(UserSchema).filter(UserSchema.id == id).update(
            user_update.model_dump(exclude_none=True)
        )
        self.db.commit()
        return self.db.query(UserSchema).filter(UserSchema.id == id).first()

    def rollback(self) -> None:
        self.db.rollback()

    def close(self) -> None:
        self.db.close()