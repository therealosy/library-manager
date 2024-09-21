from logging import Logger

from controllers.base_controller import BaseController
from models.user_model import UserModel
from models.user_update_model import UserUpdateModel
from service.meta.user_service_meta import UserServiceMeta
from utils.decorator_utility import async_controller_exception_handler, controller_exception_handler
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

    @async_controller_exception_handler
    async def update_user(self, id: int, user_update: UserUpdateModel) -> UserModel:
        self._logger.info(f"Updating user with id {id}")
        return await self.service.update(id, user_update)

    @async_controller_exception_handler
    async def add_user(self, user: UserModel) -> UserModel:
        self._logger.info(f"Adding user with email: {user.email}")
        return await self.service.add(user)
