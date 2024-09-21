from typing import List

from controllers.base_controller import BaseController
from models.user_books_model import UserBooksModel
from models.user_model import UserModel
from service.meta.user_service_meta import UserServiceMeta
from utils.decorator_utility import controller_exception_handler
from utils.dependecy_resolver import ResolveDependency
from utils.logger_utility import getlogger


class UserController(BaseController):

    def __init__(
        self,
        service: UserServiceMeta = ResolveDependency(UserServiceMeta),
    ) -> None:
        super().__init__(getlogger("UserController"))
        self.service = service

    @controller_exception_handler
    def get_user_by_id(self, id: int) -> UserModel:
        self._logger.info(f"Fetching user with id {id}")
        return self.service.get_by_id(id)

    @controller_exception_handler
    def get_all_users(self) -> List[UserModel]:
        self._logger.info(f"Getting all users")
        return self.service.get_all_users()

    @controller_exception_handler
    def get_all_users_with_books(self, include_returned: bool) -> List[UserBooksModel]:
        self._logger.info(f"Getting all users and their borrowed books")
        if include_returned:
            self._logger.info("Including returned books")
            return self.service.get_all_users_books_including_returned()
        return self.service.get_all_users_currently_borrowed_books()
