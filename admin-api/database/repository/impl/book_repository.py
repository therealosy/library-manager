from datetime import date
from sqlalchemy.orm import Session
from typing import List
from database.repository.meta.book_repository_meta import BookRepositoryMeta
from database.schema.book_schema import BookSchema
from database.schema.borrow_entry_schema import BorrowEntrySchema
from models.book_model import BookModel
from models.borrowed_book_model import BorrowedBookModel
from utils.dependecy_resolver import ResolveDependency
from utils.logger_utility import getlogger


class BookRepository(BookRepositoryMeta):

    _logger = getlogger(name="BookRepository")

    def __init__(self, db: Session = ResolveDependency(Session)) -> None:
        self.db = db

    def save(self, book: BookSchema) -> BookModel:
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return self.db.query(BookSchema).filter(BookSchema.title == book.title).first()

    def get_by_id(self, id: int) -> BookModel | None:
        return self.db.query(BookSchema).filter(BookSchema.id == id).first()

    def get_by_title(self, title: str) -> BookModel:
        return self.db.query(BookSchema).filter(BookSchema.title == title).first()

    def get_all_borrowed(self) -> List[BorrowedBookModel]:
        result = (
            self.db.query(BookSchema, BorrowEntrySchema)
            .join(BorrowEntrySchema)
            .filter(BorrowEntrySchema.is_returned == False)
            .all()
        )
        return [
            BorrowedBookModel(
                id=book.id,
                title=book.title,
                publisher=book.publisher,
                category=book.category,
                date_borrowed = borrow_entry.date_borrowed,
                return_date=borrow_entry.return_date,
                is_returned=borrow_entry.is_returned
            )
            for book, borrow_entry in result
        ]

    def get_all_due(self) -> List[BookModel]:
        result = (
            self.db.query(BookSchema, BorrowEntrySchema.return_date)
            .join(BorrowEntrySchema)
            .filter(
                BorrowEntrySchema.is_returned == False,
                BorrowEntrySchema.return_date == date.today(),
            )
            .all()
        )
        return [
            BorrowedBookModel(
                id=book.id,
                title=book.title,
                publisher=book.publisher,
                category=book.category,
                date_borrowed = borrow_entry.date_borrowed,
                return_date=borrow_entry.return_date,
                is_returned=borrow_entry.is_returned
            )
            for book, borrow_entry in result
        ]

    def get_all(self) -> List[BookModel]:
        return self.db.query(BookSchema).all()

    def remove(self, id: int) -> BookModel:
        book = self.db.query(BookSchema).filter(BookSchema.id == id).first()
        self.db.query(BookSchema).filter(BookSchema.id == id).delete()
        self.db.commit()
        return book

    def rollback(self) -> None:
        self.db.rollback()
        
    def close(self) -> None:
        self.db.close()
