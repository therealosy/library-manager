import unittest
from unittest.mock import MagicMock
from datetime import date, datetime, timedelta


from models.borrowed_book_model import BorrowedBookModel
from models.user_books_model import UserBooksModel
from models.user_update_model import UserUpdateModel
from service.impl.user_service import UserService
from database.repository.meta.user_repository_meta import UserRepositoryMeta
from models.user_model import UserModel
from utils.custom_exceptions import NotFoundException, BadRequestException


class TestUserService(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.mock_user: UserModel = UserModel(
            id=1,
            email="user@example.com",
            firstname="John",
            lastname="Doe",
            joined_on=datetime.now(),
        )

        self.mock_user_books: UserBooksModel = UserBooksModel(
            id=1,
            email="user@example.com",
            firstname="John",
            lastname="Doe",
            joined_on=datetime.now(),
            borrowed_books=[
                BorrowedBookModel(
                    id=1,
                    title="Test Book",
                    publisher="Test Publisher",
                    category="Test Category",
                    date_borrowed=date.today(),
                    return_date=date.today() + timedelta(days=1),
                    is_returned=False,
                )
            ],
        )

        self.mock_repository: UserRepositoryMeta = MagicMock(spec=UserRepositoryMeta)
        self.user_service = UserService(self.mock_repository)

    def test_add_user_returns_user(self):
        user_to_add = self.mock_user
        self.mock_repository.save.return_value = user_to_add

        result = self.user_service.add(user_to_add)

        self.assertEqual(user_to_add, result)

    def test_add_user_with_invalid_email_raises_bad_request_exception(self):
        user_to_add = UserModel(
            id=1,
            email="bad_email",
            firstname="John",
            lastname="Doe",
            joined_on=datetime.now(),
        )

        with self.assertRaises(BadRequestException):
            self.user_service.add(user_to_add)

    def test_find_user_by_id_returns_user(self):
        user = self.mock_user
        self.mock_repository.get_by_id.return_value = user

        result = self.user_service.get_by_id(user.id)

        self.assertEqual(user, result)

    def test_find_invalid_user_by_id_raises_not_found_exception(self):
        self.mock_repository.get_by_id.return_value = None

        with self.assertRaises(NotFoundException):
            self.user_service.get_by_id(2)

    def test_find_user_by_email_returns_user(self):
        user = self.mock_user
        self.mock_repository.get_by_email.return_value = user

        result = self.user_service.get_by_email(user.email)

        self.assertEqual(user, result)

    def test_find_invalid_user_by_id_raises_not_found_exception(self):
        self.mock_repository.get_by_email.return_value = None

        with self.assertRaises(NotFoundException):
            self.user_service.get_by_email(2)

    def test_find_all_users_returns_list_of_users(self):
        user = self.mock_user
        self.mock_repository.get_all.return_value = [user]

        result = self.user_service.get_all_users()

        self.assertEqual([user], result)

    def test_find_all_users_books_currently_borrowed_returns_list_of_users_books(self):
        user_books = self.mock_user_books
        self.mock_repository.get_all_users_with_currently_borrowed_books.return_value = [
            user_books
        ]

        result = self.user_service.get_all_users_currently_borrowed_books()

        self.assertEqual([user_books], result)
        
    def test_find_all_users_books_including_returned_book_returns_list_of_users_books(self):
        user_books = self.mock_user_books
        self.mock_repository.get_all_books_including_returned.return_value = [
            user_books
        ]

        result = self.user_service.get_all_users_books_including_returned()

        self.assertEqual([user_books], result)

    def test_find_invalid_user_by_id_raises_not_found_exception(self):
        self.mock_repository.get_by_id.return_value = None

        with self.assertRaises(NotFoundException):
            self.user_service.get_by_id(2)

    def test_update_user_calls_update_method_with_update_model(self):
        user = self.mock_user
        self.mock_repository.update.return_value = user

        update_model = UserUpdateModel(
            email="newemail@example.com", firstname="Jane", lastname="Doe"
        )

        self.user_service.update(user.id, update_model)

        self.mock_repository.update.assert_called_with(user.id, update_model)

    def test_update_invalid_user_raises_not_found_exception(self):
        self.mock_repository.update.return_value = None

        update_model = UserUpdateModel(
            email="newemail@example.com", firstname="Jane", lastname="Doe"
        )

        with self.assertRaises(NotFoundException):
            self.user_service.update(2, update_model)

    def test_rollback_calls_repository_rollback(self):
        self.user_service.rollback()
        self.mock_repository.rollback.assert_called_once()
