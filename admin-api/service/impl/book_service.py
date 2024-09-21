from datetime import date, timedelta
from typing import List

from aiokafka import AIOKafkaProducer
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from database.repository.meta.book_repository_meta import BookRepositoryMeta
from database.repository.meta.borrow_entry_repository_meta import (
    BorrowEntryRepositoryMeta,
)
from database.schema.book_schema import BookSchema
from database.schema.borrow_entry_schema import BorrowEntrySchema
from models.book_model import BookModel
from models.borrow_entry_model import BorrowEntryModel
from models.borrowed_book_model import BorrowedBookModel
from service.meta.book_service_meta import BookServiceMeta
from utils.environment import (
    KAFKA_ADD_BOOK_TOPIC,
    KAFKA_REMOVE_BOOK_TOPIC,
    KAFKA_RETURN_BOOK_TOPIC,
)
from utils.custom_exceptions import (
    NotFoundException,
    ConflictException,
)
from utils.dependecy_resolver import ResolveDependency
from utils.logger_utility import getlogger


class BookService(BookServiceMeta):
    _logger = getlogger(name="BookService")

    def __init__(
        self,
        book_repository: BookRepositoryMeta = ResolveDependency(BookRepositoryMeta),
        borrow_entry_repository: BorrowEntryRepositoryMeta = ResolveDependency(
            BorrowEntryRepositoryMeta
        ),
        kafka_producer: AIOKafkaProducer = ResolveDependency(AIOKafkaProducer),
    ) -> None:
        self.book_repository = book_repository
        self.borrow_entry_repository = borrow_entry_repository
        self.kafka_producer = kafka_producer

    async def add(self, book: BookModel) -> BookModel:
        try:
            inserted_book = BookModel.model_validate(
                self.book_repository.save(
                    BookSchema(
                        id=book.id,
                        title=book.title.lower(),
                        publisher=book.publisher.lower(),
                        category=book.category.lower(),
                    )
                )
            )
            await self.kafka_producer.send_and_wait(
                KAFKA_ADD_BOOK_TOPIC, [inserted_book.model_dump()]
            )
        except IntegrityError as e:
            self.rollback()
            if isinstance(e.orig, UniqueViolation):
                error_msg = f"Book with title {book.title} already exists"
                self._logger.error(error_msg)
                raise ConflictException(error_msg)
            else:
                self._logger.error(f"Integrity error occurred: {e.orig}")
                raise Exception(e.orig)
        except Exception as e:
            self._logger.error(f"Failed to save book {book.title} due to: {e}")
            self.rollback()
            raise Exception(e)

        return inserted_book

    def get_by_id(self, id: int) -> BookModel:
        try:
            book = self.book_repository.get_by_id(id)
        except Exception as e:
            self._logger.error(f"Failed to find book with id {id} due to: {e}")
            raise Exception(e)

        if book is None:
            raise NotFoundException("Book not found")

        return book

    def get_by_title(self, title: str) -> BookModel:
        try:
            book = self.book_repository.get_by_title(title)
        except Exception as e:
            self._logger.error(f"Failed to find book with title {title} due to: {e}")
            raise Exception(e)

        if book is None:
            raise NotFoundException("Book not found")

        return book

    def get_all_due(self) -> List[BorrowEntryModel]:
        try:
            borrow_entries = self.borrow_entry_repository.get_all_due()
        except Exception as e:
            self._logger.error(f"Failed to find any due books because: {e}")
            raise Exception(e)

        if borrow_entries is None:
            raise NotFoundException("No due books found")

        return borrow_entries

    async def return_book(self, borrow_id: int) -> BookModel:
        try:
            borrow_entry = self.borrow_entry_repository.update_return_status(borrow_id)
        except Exception as e:
            self._logger.error(
                f"Failed to return borrow entry with id {borrow_id} due to: {e}"
            )
            self.rollback()
            raise Exception(e)

        if borrow_entry is None:
            raise NotFoundException("No such entry found")

        try:
            book = self.book_repository.get_by_id(borrow_entry.book_id)
        except Exception as e:
            self._logger.error(
                f"Failed to return borrow entry with id {borrow_id} due to: {e}"
            )
            self.rollback()
            raise Exception(e)

        if book is None:
            raise NotFoundException("No such book found")

        await self.kafka_producer.send_and_wait(KAFKA_RETURN_BOOK_TOPIC, [book.title])
        return book

    def borrow_book(
        self, title: str, user_id: int, borrow_duration_days: int
    ) -> BookModel:
        try:
            book = self.book_repository.get_by_title(title)
        except Exception as e:
            self._logger.error(f"Failed to borrow book with title {title} due to: {e}")
            self.rollback()
            raise Exception(e)

        if book is None:
            raise NotFoundException("Book not found")

        try:
            unreturned_entry = self.borrow_entry_repository.get_unreturned_entry_by_book_id(book.id)
        except Exception as e:
            self._logger.error(f"Failed when checking borrow entry for {title} due to {e}")
            self.rollback()
            raise Exception(e)
        
        if unreturned_entry is not None:
            raise ConflictException("Book Already borrowed")

        try:
            self.borrow_entry_repository.save(
                BorrowEntrySchema(
                    book_id=book.id,
                    user_id=user_id,
                    return_date=date.today() + timedelta(days=borrow_duration_days),
                )
            )
        except Exception as e:
            self._logger.error(f"Failed to insert borrow entry for {title} due to {e}")
            self.rollback()
            raise Exception(e)

        return book

    def get_all(self) -> List[BookModel]:
        self._logger.info("Getting all")
        try:
            books = self.book_repository.get_all()
        except Exception as e:
            self._logger.error(f"Failed to find any books due to: {e}")
            raise Exception(e)

        if books is None:
            raise NotFoundException("No Books found")

        return books

    def get_all_borrowed(self) -> List[BorrowedBookModel]:
        self._logger.info("Getting all borrowed")
        try:
            books = self.book_repository.get_all_borrowed()
        except Exception as e:
            self._logger.error(f"Failed to find any borrowed books due to: {e}")
            raise Exception(e)

        if books is None:
            raise NotFoundException("No Borrowed Books found")

        return books

    async def remove_book(self, id: int) -> BookModel:
        try:
            unreturned_entry = self.borrow_entry_repository.get_unreturned_entry_by_book_id(id)
        except Exception as e:
            self._logger.error(f"Failed when checking for borrow entry for book with id {id} due to {e}")
            self.rollback()
            raise Exception(e)
        
        if unreturned_entry is not None:
            raise ConflictException("Cannot remove book that has not been returned")
        
        try:
            removed_book = self.book_repository.remove(id)
        except Exception as e:
            self._logger.error(f"Failed to remove book with id {id} due to: {e}")
            self.rollback()
            raise Exception(e)

        if removed_book is None:
            raise NotFoundException("Book not found")

        await self.kafka_producer.send_and_wait(
            KAFKA_REMOVE_BOOK_TOPIC, [removed_book.title]
        )

        return removed_book

    def rollback(self) -> None:
        self.book_repository.rollback()
        
    def close(self) -> None:
        self.book_repository.close()
        self.borrow_entry_repository.close()
