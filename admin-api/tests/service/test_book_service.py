from datetime import date, timedelta
import unittest
from unittest.mock import MagicMock, AsyncMock

from aiokafka import AIOKafkaProducer

from database.repository.meta.borrow_entry_repository_meta import (
    BorrowEntryRepositoryMeta,
)

from models.borrow_entry_model import BorrowEntryModel
from models.borrowed_book_model import BorrowedBookModel
from service.impl.book_service import BookService
from database.repository.meta.book_repository_meta import BookRepositoryMeta
from models.book_model import BookModel
from utils.custom_exceptions import ConflictException, NotFoundException


class TestBookService(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.mock_book: BookModel = BookModel(
            id=1,
            title="Test Book",
            publisher="Test Publisher",
            category="Test Category",
        )

        self.mock_borrowed_book: BorrowedBookModel = BorrowedBookModel(
            id=1,
            title="Test Book",
            publisher="Test Publisher",
            category="Test Category",
            date_borrowed=date.today(),
            return_date=date.today() + timedelta(days=1),
            is_returned=False,
        )

        self.mock_borrow_entry: BorrowEntryModel = BorrowEntryModel(
            id=1,
            book_id=1,
            user_id=1,
            date_borrowed=date.today(),
            return_date=date.today() + timedelta(days=1),
        )

        self.mock_book_repository: BookRepositoryMeta = MagicMock(
            spec=BookRepositoryMeta
        )
        self.mock_borrow_entry_repository: BorrowEntryRepositoryMeta = MagicMock(
            spec=BorrowEntryRepositoryMeta
        )
        self.mock_kafka_producer: AIOKafkaProducer = AsyncMock(spec=AIOKafkaProducer)

        self.book_service = BookService(
            self.mock_book_repository,
            self.mock_borrow_entry_repository,
            self.mock_kafka_producer,
        )

    async def test_add_book_returns_book(self):
        book_to_add = self.mock_book
        self.mock_book_repository.save.return_value = book_to_add
        self.mock_kafka_producer.send_and_wait.return_value = None

        result = await self.book_service.add(book_to_add)

        self.assertEqual(book_to_add, result)

    async def test_remove_book_returns_book(self):
        book_to_remove = self.mock_book
        self.mock_book_repository.remove.return_value = book_to_remove
        self.mock_kafka_producer.send_and_wait.return_value = None

        result = await self.book_service.remove_book(book_to_remove.id)

        self.assertEqual(book_to_remove, result)

    async def test_remove_invalid_book_raises_not_found_exception(self):
        self.mock_book_repository.remove.return_value = None
        self.mock_kafka_producer.send_and_wait.return_value = None

        with self.assertRaises(NotFoundException):
            await self.book_service.remove_book(2)

    def test_find_book_by_id_returns_book(self):
        book = self.mock_book
        self.mock_book_repository.get_by_id.return_value = book

        result = self.book_service.get_by_id(book.id)

        self.assertEqual(book, result)

    def test_find_book_by_title_returns_book(self):
        book = self.mock_book
        self.mock_book_repository.get_by_title.return_value = book

        result = self.book_service.get_by_title(book.title)

        self.assertEqual(book, result)

    def test_find_all_books_returns_list_of_books(self):
        book = self.mock_book
        self.mock_book_repository.get_all.return_value = [book]

        result = self.book_service.get_all()

        self.assertEqual([book], result)

    def test_find_borrowed_books_returns_list_of_borrowed_books(self):
        borrowed_book = self.mock_borrowed_book
        self.mock_book_repository.get_all_borrowed.return_value = [borrowed_book]

        result = self.book_service.get_all_borrowed()

        self.assertEqual([borrowed_book], result)

    def test_book_not_found_raises_not_found_exception(self):
        self.mock_book_repository.get_by_id.return_value = None

        with self.assertRaises(NotFoundException):
            self.book_service.get_by_id(2)

    def test_borrow_book_calls_borrow_entry_save(self):
        book = self.mock_book
        self.mock_book_repository.get_by_title.return_value = book
        self.mock_borrow_entry_repository.get_unreturned_entry_by_book_id.return_value = (
            None
        )

        self.book_service.borrow_book(book.title, 1, 1)

        self.mock_borrow_entry_repository.save.assert_called_once()

    def test_borrow_book_with_existing_unreturned_entry_raises_conflict_exception(self):
        book = self.mock_book
        borrow_entry = self.mock_borrow_entry
        self.mock_book_repository.get_by_title.return_value = book
        self.mock_borrow_entry_repository.get_unreturned_entry_by_book_id.return_value = (
            borrow_entry
        )

        with self.assertRaises(ConflictException):
            self.book_service.borrow_book(book.title, 1, 1)

    def test_borrow_invalid_book_raises_not_found_exception(self):
        self.mock_book_repository.get_by_title.return_value = None
        self.mock_kafka_producer.send_and_wait.return_value = None

        with self.assertRaises(NotFoundException):
            self.book_service.borrow_book("Test book", 1, 1)

    async def test_return_invalid_book_raises_not_found_exception(self):
        self.mock_book_repository.get_by_id.return_value = None
        self.mock_borrow_entry_repository.update_return_status.return_value = None
        self.mock_kafka_producer.send_and_wait.return_value = None

        with self.assertRaises(NotFoundException):
            await self.book_service.return_book(2)

    async def test_return_book_calls_update_return_status(self):
        book = self.mock_book
        borrow_entry = self.mock_borrow_entry

        self.mock_book_repository.get_by_id.return_value = book
        self.mock_borrow_entry_repository.update_return_status.return_value = (
            borrow_entry
        )
        self.mock_kafka_producer.send_and_wait.return_value = None

        await self.book_service.return_book(1)

        self.mock_borrow_entry_repository.update_return_status.assert_called_once()

    def test_rollback_calls_repository_rollback(self):
        self.book_service.rollback()
        self.mock_book_repository.rollback.assert_called_once()
