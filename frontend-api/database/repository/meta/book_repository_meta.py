from abc import abstractmethod, ABC
from typing import List
from database.schema.book_schema import BookSchema
from models.book_filter_model import BookFilterModel
from models.book_model import BookModel


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
    def update_is_borrowed(self, id: int, is_borrowed: bool) -> BookModel:
        pass

    @abstractmethod
    def get_all(self) -> List[BookModel]:
        pass

    @abstractmethod
    def search_books(self, filters: BookFilterModel) -> List[BookModel]:
        pass

    @abstractmethod
    def remove(self, id: int) -> BookModel:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass
    
    @abstractmethod
    def close(self) -> None:
        pass