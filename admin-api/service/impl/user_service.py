import re
from typing import List
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from database.repository.meta.user_repository_meta import UserRepositoryMeta
from database.schema.user_schema import UserSchema
from models.user_books_model import UserBooksModel
from models.user_model import UserModel
from models.user_update_model import UserUpdateModel
from service.meta.user_service_meta import UserServiceMeta
from utils.custom_exceptions import BadRequestException, NotFoundException, ConflictException
from utils.dependecy_resolver import ResolveDependency
from utils.logger_utility import getlogger


class UserService(UserServiceMeta):

    _logger = getlogger(name="UserService")

    def __init__(
        self,
        user_repository: UserRepositoryMeta = ResolveDependency(UserRepositoryMeta),
    ) -> None:
        self.repository = user_repository

    def add(self, user: UserModel) -> UserModel:
        if not self.validate_email(user.email):
            raise BadRequestException("Invalid email supplied")
        
        try:
            return self.repository.save(
                UserSchema(
                    email=user.email,
                    firstname=user.firstname,
                    lastname=user.lastname,
                )
            )
        except IntegrityError as e:
            self.rollback()
            if isinstance(e.orig, UniqueViolation):
                error_msg = f"User with email {user.email} already exists"
                self._logger.error(error_msg)
                raise ConflictException(error_msg)
            else:
                self._logger.error(f"Integrity error occurred: {e.orig}")
                raise Exception(e.orig)
        except Exception as e:
            self._logger.error(f"Failed to save user {user.email} due to: {e}")
            self.rollback()
            raise Exception(e)

    def get_by_id(self, id: int) -> UserModel:
        try:
            user = self.repository.get_by_id(id)
        except Exception as e:
            self._logger.error(f"Failed to find user with id {id} due to: {e}")
            raise Exception(e)

        if user is None:
            raise NotFoundException("User not found")

        return user

    def get_by_email(self, email: str) -> UserModel:
        try:
            user = self.repository.get_by_email(email)
        except Exception as e:
            self._logger.error(f"Failed to find user with email {email} due to: {e}")
            raise Exception(e)

        if user is None:
            raise NotFoundException("User not found")

        return user

    def get_all_users(self) -> List[UserModel]:
        try:
            users = self.repository.get_all()
        except Exception as e:
            self._logger.error(f"Failed to find users due to: {e}")
            raise Exception(e)

        if users is None:
            raise NotFoundException("No users found")

        return users

    def get_all_users_books_including_returned(self) -> List[UserBooksModel]:
        try:
            users = self.repository.get_all_books_including_returned()
        except Exception as e:
            self._logger.error(f"Failed to find users with borrowed books due to: {e}")
            raise Exception(e)

        if users is None:
            raise NotFoundException("No users with borrowed books found")

        return users

    def get_all_users_currently_borrowed_books(self) -> List[UserBooksModel]:
        try:
            users = self.repository.get_all_users_with_currently_borrowed_books()
        except Exception as e:
            self._logger.error(f"Failed to find users with borrowed books due to: {e}")
            raise Exception(e)

        if users is None:
            raise NotFoundException("No users with borrowed books found")

        return users

    def update(self, id: int, user_update: UserUpdateModel) -> UserModel:
        try:
            user = self.repository.update(id, user_update)
        except Exception as e:
            self._logger.error(f"Failed to update user with id {id} due to: {e}")
            self.rollback()
            raise Exception(e)

        if user is None:
            raise NotFoundException("User not found")

        return user
    
    def validate_email(self, email: str):
        email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
        return email_regex.match(email)

    def rollback(self) -> None:
        self.repository.rollback()
