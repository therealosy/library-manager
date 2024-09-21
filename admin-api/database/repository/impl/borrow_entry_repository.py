from datetime import date
from typing import List
from sqlalchemy.orm import Session
from database.repository.meta.borrow_entry_repository_meta import (
    BorrowEntryRepositoryMeta,
)
from database.schema.borrow_entry_schema import BorrowEntrySchema
from models.borrow_entry_model import BorrowEntryModel
from utils.dependecy_resolver import ResolveDependency


class BorrowEntryRepository(BorrowEntryRepositoryMeta):

    def __init__(self, db: Session = ResolveDependency(Session)) -> None:
        self.db = db

    def save(self, borrowed_book: BorrowEntrySchema) -> BorrowEntryModel:
        self.db.add(borrowed_book)
        self.db.commit()
        self.db.refresh(borrowed_book)
        return (
            self.db.query(BorrowEntrySchema)
            .filter(
                BorrowEntrySchema.return_date == borrowed_book.return_date,
                BorrowEntrySchema.book_id == borrowed_book.book_id,
            )
            .first()
        )

    def update_return_status(self, id: int) -> BorrowEntryModel:
        self.db.query(BorrowEntrySchema).filter(
            BorrowEntrySchema.id == id,
        ).update({"is_returned": True})
        self.db.commit()
        return (
            self.db.query(BorrowEntrySchema).filter(BorrowEntrySchema.id == id).first()
        )

    def get_all_due(self) -> List[BorrowEntryModel]:
        return (
            self.db.query(BorrowEntrySchema)
            .filter(
                BorrowEntrySchema.is_returned == False,
                BorrowEntrySchema.return_date <= date.today(),
            )
            .all()
        )

    def get_unreturned_entry_by_book_id(self, book_id: int) -> BorrowEntryModel:
        return (
            self.db.query(BorrowEntrySchema)
            .filter(
                BorrowEntrySchema.is_returned == False,
                BorrowEntrySchema.book_id == book_id,
            )
            .first()
        )

    def rollback(self) -> None:
        self.db.rollback()
