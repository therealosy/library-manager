from sqlalchemy.orm import Session
from typing import List
from database.repository.meta.book_repository_meta import BookRepositoryMeta
from database.schema.book_schema import BookSchema
from models.book_filter_model import BookFilterModel
from models.book_model import BookModel
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
        return (
            self.db.query(BookSchema)
            .filter(BookSchema.id == id, BookSchema.is_borrowed == False)
            .first()
        )

    def get_by_title(self, title: str) -> BookModel:
        return self.db.query(BookSchema).filter(BookSchema.title == title).first()

    def update_is_borrowed(self, id: int, is_borrowed: bool) -> BookModel:
        self.db.query(BookSchema).filter(BookSchema.id == id).update(
            {"is_borrowed": is_borrowed}
        )
        self.db.commit()
        return self.db.query(BookSchema).filter(BookSchema.id == id).first()

    def get_all(self) -> List[BookModel]:
        return self.db.query(BookSchema).filter(BookSchema.is_borrowed == False).all()

    def search_books(self, filters: BookFilterModel) -> List[BookModel]:
        filter_list = [getattr(BookSchema, "is_borrowed") == False]
        for key, value in filters.model_dump(exclude_none=True).items():
            filter_list.append(getattr(BookSchema, key).contains(value))

        return self.db.query(BookSchema).filter(*filter_list).all()

    def remove(self, id: int) -> BookModel:
        book = self.db.query(BookSchema).filter(BookSchema.id == id).first()
        self.db.query(BookSchema).filter(BookSchema.id == id).delete()
        self.db.commit()
        return book

    def rollback(self) -> None:
        self.db.rollback()
