from abc import abstractmethod, ABC
from typing import List
from database.schema.borrow_entry_schema import BorrowEntrySchema
from models.borrow_entry_model import BorrowEntryModel


class BorrowEntryRepositoryMeta(ABC):
    @abstractmethod
    def save(self, borrowed_book: BorrowEntrySchema) -> BorrowEntryModel:
        pass

    @abstractmethod
    def update_return_status(self, id: int) -> BorrowEntryModel:
        pass

    @abstractmethod
    def get_all_due(self) -> List[BorrowEntryModel]:
        pass
    
    @abstractmethod
    def get_unreturned_entry_by_book_id(self, book_id: int) -> BorrowEntryModel:
        pass


    @abstractmethod
    def rollback(self) -> None:
        pass
