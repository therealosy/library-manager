from abc import abstractmethod, ABC
from typing import List
from models.book_borrow_model import BookBorrowModel
from models.book_filter_model import BookFilterModel
from models.book_model import BookModel


class BookServiceMeta(ABC):
    @abstractmethod
    def add(self, book: BookModel) -> BookModel:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> BookModel:
        pass
    
    @abstractmethod
    def get_by_title(self, title: str) -> BookModel:
        pass

    @abstractmethod
    def return_book(self, id: int) -> BookModel:
        pass

    @abstractmethod
    def get_all(self) -> List[BookModel]:
        pass

    @abstractmethod
    def search_books(self, filters: BookFilterModel) -> List[BookModel]:
        pass

    @abstractmethod
    def remove_book(self, id: int) -> BookModel:
        pass
    
    @abstractmethod
    def borrow_book(self, id:int, user_email: str, borrow_duration_days: int) -> BookModel:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass
    
    