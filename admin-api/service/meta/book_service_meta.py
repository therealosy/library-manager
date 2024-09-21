from abc import abstractmethod, ABC
from typing import List
from models.book_model import BookModel
from models.borrow_entry_model import BorrowEntryModel


class BookServiceMeta(ABC):
    @abstractmethod
    def add(self, book: BookModel) -> BookModel:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> BookModel:
        pass

    @abstractmethod
    def get_by_title(self, id: int) -> BookModel:
        pass

    @abstractmethod
    def return_book(self, borrow_id: int) -> BookModel:
        pass

    @abstractmethod
    def get_all(self) -> List[BookModel]:
        pass

    @abstractmethod
    def get_all_borrowed(self) -> List[BorrowEntryModel]:
        pass

    @abstractmethod
    def get_all_due(self) -> List[BorrowEntryModel]:
        pass

    @abstractmethod
    def remove_book(self, id: int) -> BookModel:
        pass

    @abstractmethod
    def borrow_book(
        self, title: str, user_id: int, borrow_duration_days: int
    ) -> BookModel:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass
    
    @abstractmethod
    def close(self) -> None:
        pass

