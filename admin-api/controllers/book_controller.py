from typing import List

from controllers.base_controller import BaseController
from models.book_model import BookModel
from models.borrowed_book_model import BorrowedBookModel
from service.meta.book_service_meta import BookServiceMeta
from utils.decorator_utility import async_controller_exception_handler, controller_exception_handler
from utils.dependecy_resolver import ResolveDependency
from utils.logger_utility import getlogger


class BookController(BaseController):

    def __init__(
        self,
        service: BookServiceMeta = ResolveDependency(BookServiceMeta),
    ) -> None:
        super().__init__(getlogger("BookController"))
        self.service = service

    @async_controller_exception_handler
    async def add_book(self, book: BookModel) -> BookModel:
        self._logger.info(f"Adding book with title {book.title}")
        return await self.service.add(book)

    @controller_exception_handler
    def get_book_by_id(self, id: int) -> BookModel:
        self._logger.info(f"Searching for book with id {id}")
        return self.service.get_by_id(id)

    @async_controller_exception_handler
    async def remove_book(self, id: int) -> BookModel:
        self._logger.info(f"Removing book with id {id}")
        return await self.service.remove_book(id)

    @controller_exception_handler
    def get_all_books(self) -> List[BookModel]:
        self._logger.info("Fetching all books")
        return self.service.get_all()

    @controller_exception_handler
    def get_all_borrowed_books(self) -> List[BorrowedBookModel]:
        self._logger.info("Fetching all borrowed books")
        return self.service.get_all_borrowed()
    
    def close(self) -> None:
        self.service.close()

