from abc import abstractmethod, ABC
from typing import List
from database.schema.book_schema import BookSchema
from models.book_model import BookModel
from models.borrowed_book_model import BorrowedBookModel


class BookRepositoryMeta(ABC):
    @abstractmethod
    def save(self, book: BookSchema) -> BookModel:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> BookModel:
        pass

    @abstractmethod
    def get_by_title(self, title: str) -> BookModel:
        pass

    @abstractmethod
    def get_all_borrowed(self) -> List[BorrowedBookModel]:
        pass

    @abstractmethod
    def get_all(self) -> List[BookModel]:
        pass

    @abstractmethod
    def remove(self, id: int) -> BookModel:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass
