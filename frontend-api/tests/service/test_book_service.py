import unittest
from unittest.mock import MagicMock, AsyncMock

from aiokafka import AIOKafkaProducer

from models.book_filter_model import BookFilterModel
from service.impl.book_service import BookService
from database.repository.meta.book_repository_meta import BookRepositoryMeta
from models.book_model import BookModel
from utils.custom_exceptions import NotFoundException


class TestBookService(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.mock_book: BookModel = BookModel(
            id=1,
            title="Test Book",
            publisher="Test Publisher",
            category="Test Category",
            is_borrowed=False,
        )
        self.mock_borrow_duration_days = 2
        self.mock_user_email = "user@example.com"

        self.mock_repository: BookRepositoryMeta = MagicMock(spec=BookRepositoryMeta)
        self.mock_kafka_producer: AIOKafkaProducer = AsyncMock(spec=AIOKafkaProducer)

        self.book_service = BookService(self.mock_repository, self.mock_kafka_producer)

    def test_add_book_returns_book(self):
        book_to_add = self.mock_book
        self.mock_repository.save.return_value = book_to_add

        result = self.book_service.add(book_to_add)

        self.assertEqual(book_to_add, result)

    def test_remove_book_returns_book(self):
        book_to_remove = self.mock_book
        self.mock_repository.remove.return_value = book_to_remove

        result = self.book_service.remove_book(book_to_remove.id)

        self.assertEqual(book_to_remove, result)

    def test_find_book_by_id_returns_book(self):
        book = self.mock_book
        self.mock_repository.get_by_id.return_value = book

        result = self.book_service.get_by_id(book.id)

        self.assertEqual(book, result)

    def test_find_all_books_returns_list_of_books(self):
        book = self.mock_book
        self.mock_repository.get_all.return_value = [book]

        result = self.book_service.get_all()

        self.assertEqual([book], result)

    def test_search_books_calls_repository_with_filters(self):
        book = self.mock_book
        filters = BookFilterModel(
            title="Test Title", category="Test Category", publisher="Test Publisher"
        )
        self.mock_repository.search_books.return_value = book

        result = self.book_service.search_books(filters)

        self.mock_repository.search_books.assert_called_with(filters)

    def test_book_not_found_raises_not_found_exception(self):
        self.mock_repository.get_by_id.return_value = None

        with self.assertRaises(NotFoundException):
            self.book_service.get_by_id(2)

    def test_return_book_updates_borrow_flag_with_false(self):
        id = 1
        book = self.mock_book
        self.mock_repository.update_is_borrowed.return_value = book

        self.book_service.return_book(id)

        self.mock_repository.update_is_borrowed.assert_called_with(id, False)

    def test_return_invalid_book_raises_not_found_exception(self):
        self.mock_repository.update_is_borrowed.return_value = None
        self.mock_kafka_producer.send_and_wait.return_value = None

        with self.assertRaises(NotFoundException):
            self.book_service.return_book(2)

    async def test_borrow_book_updates_borrow_flag_with_true(self):
        id = 1
        book = self.mock_book
        borrow_duration_days = self.mock_borrow_duration_days
        user_email = self.mock_user_email
        self.mock_repository.get_by_id.return_value = book
        self.mock_repository.update_is_borrowed.return_value = book
        self.mock_kafka_producer.send_and_wait.return_value = None

        await self.book_service.borrow_book(id, user_email, borrow_duration_days)

        self.mock_repository.update_is_borrowed.assert_called_with(id, True)

    async def test_borrow_invalid_book_raises_not_found_exception(self):
        borrow_duration_days = self.mock_borrow_duration_days
        user_email = self.mock_user_email
        self.mock_repository.get_by_id.return_value = None
        self.mock_kafka_producer.send_and_wait.return_value = None

        with self.assertRaises(NotFoundException):
            await self.book_service.borrow_book(2, user_email, borrow_duration_days)

    def test_rollback_calls_repository_rollback(self):
        self.book_service.rollback()
        self.mock_repository.rollback.assert_called_once()
