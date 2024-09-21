from typing import List
from logging import Logger

from controllers.base_controller import BaseController
from models.borrow_details_model import BorrowDetailsModel
from models.book_filter_model import BookFilterModel
from models.book_model import BookModel
from service.meta.book_service_meta import BookServiceMeta
from service.meta.user_service_meta import UserServiceMeta
from utils.decorator_utility import async_controller_exception_handler, controller_exception_handler
from utils.dependecy_resolver import ResolveDependency
from utils.logger_utility import getlogger


class BookController(BaseController):

    def __init__(
        self,
        book_service: BookServiceMeta = ResolveDependency(BookServiceMeta),
        user_service: UserServiceMeta = ResolveDependency(UserServiceMeta),
    ) -> None:
        super().__init__(getlogger("BookController"))
        self.book_service = book_service
        self.user_service = user_service

    @controller_exception_handler
    def get_by_id(self, id: int) -> BookModel:
        self._logger.info(f"Searching for book with id {id}")
        return self.book_service.get_by_id(id)

    @controller_exception_handler
    def get_all(self) -> List[BookModel]:
        self._logger.info("Fetching all books")
        return self.book_service.get_all()

    @controller_exception_handler
    def search_books(
        self, category: str | None, publisher: str | None, title: str | None
    ) -> List[BookModel]:
        filters = BookFilterModel(category=category, publisher=publisher, title=title)
        self._logger.info(f"Searching for books with filters: {filters}")
        return self.book_service.search_books(filters)

    @async_controller_exception_handler
    async def borrow_book(self, id: int, borrow_details: BorrowDetailsModel) -> BookModel:
        self._logger.info(f"Borrowing book with id: {id}")
        user_email: str = self.user_service.get_by_id(borrow_details.user_id).email
        return await self.book_service.borrow_book(
            id, user_email, borrow_details.borrow_duration_days
        )

    def close(self) -> None:
        self.book_service.close()
