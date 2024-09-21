from typing import List

from aiokafka import AIOKafkaProducer
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from database.repository.meta.book_repository_meta import BookRepositoryMeta
from database.schema.book_schema import BookSchema
from models.book_borrow_model import BookBorrowModel
from models.borrow_details_model import BorrowDetailsModel
from models.book_filter_model import BookFilterModel
from models.book_model import BookModel
from models.user_model import UserModel
from service.meta.book_service_meta import BookServiceMeta
from service.meta.user_service_meta import UserServiceMeta
from utils.environment import KAFKA_BORROW_BOOK_TOPIC
from utils.custom_exceptions import (
    NotFoundException,
    ConflictException,
)
from utils.dependecy_resolver import ResolveDependency
from utils.logger_utility import getlogger

# from utils.kafka_utility import kafka_seriaizer


class BookService(BookServiceMeta):
    _logger = getlogger(name="BookService")

    def __init__(
        self,
        book_repository: BookRepositoryMeta = ResolveDependency(BookRepositoryMeta),
        kafka_producer: AIOKafkaProducer = ResolveDependency(AIOKafkaProducer),
    ) -> None:
        self.repository = book_repository
        self.kafka_producer = kafka_producer

    def add(self, book: BookModel) -> BookModel:
        try:
            return self.repository.save(
                BookSchema(
                    id=book.id,
                    title=book.title.lower(),
                    publisher=book.publisher.lower(),
                    category=book.category.lower(),
                )
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

    def get_by_id(self, id: int) -> BookModel:
        try:
            book = self.repository.get_by_id(id)
        except Exception as e:
            self._logger.error(f"Failed to find book with id {id} due to: {e}")
            raise Exception(e)

        if book is None:
            raise NotFoundException("Book not found")

        return book

    def get_by_title(self, title: str) -> BookModel:
        try:
            book = self.repository.get_by_title(title)
        except Exception as e:
            self._logger.error(f"Failed to find book with title {title} due to: {e}")
            raise Exception(e)

        if book is None:
            raise NotFoundException("Book not found")

        return book

    def return_book(self, id: int) -> BookModel:
        try:
            book = self.repository.update_is_borrowed(id, False)
        except Exception as e:
            self._logger.error(f"Failed to return book with id {id} due to: {e}")
            self.rollback()
            raise Exception(e)

        if book is None:
            raise NotFoundException("Book not found")

        return book

    async def borrow_book(
        self, id: int, user_email: str, borrow_duration_days: int
    ) -> BookModel:

        try:
            existing_book = self.repository.get_by_id(id)
        except Exception as e:
            self._logger.error(f"Failed to borrow book with id {id} due to: {e}")
            self.rollback()
            raise Exception(e)

        if existing_book is None:
            raise NotFoundException("Book not found")

        if existing_book.is_borrowed:
            raise ConflictException("Book has already been borrowed")

        try:
            book = self.repository.update_is_borrowed(id, True)
            
            # Send message to admin service to borrow book
            message = [
                BookBorrowModel(
                    book_title=book.title,
                    user_email=user_email,
                    borrow_duration_days=borrow_duration_days,
                ).model_dump()
            ]
            await self.kafka_producer.send_and_wait(KAFKA_BORROW_BOOK_TOPIC, message)
        except Exception as e:
            self._logger.error(f"Failed to borrow book with id {id} due to: {e}")
            self.rollback()
            raise Exception(e)

        return book

    def get_all(self) -> List[BookModel]:
        try:
            books = self.repository.get_all()
        except Exception as e:
            self._logger.error(f"Failed to find any books due to: {e}")
            raise Exception(e)

        if books is None:
            raise NotFoundException("No Books found")

        return books

    def search_books(self, filters: BookFilterModel) -> List[BookModel]:
        try:
            books = self.repository.search_books(filters)
        except Exception as e:
            self._logger.error(f"Failed to find any books due to: {e}")
            raise Exception(e)

        if books is None:
            raise NotFoundException("No Books found matching criteria")

        return books

    def remove_book(self, id: int) -> BookModel:
        try:
            removed_book = self.repository.remove(id)
        except Exception as e:
            self._logger.error(f"Failed to remove book with id {id} due to: {e}")
            self.rollback()
            raise Exception(e)

        if removed_book is None:
            raise NotFoundException("Book not found")

        return removed_book

    def rollback(self) -> None:
        self.repository.rollback()

    def close(self) -> None:
        self.repository.close()