from typing import List
from fastapi import APIRouter, Depends

from controllers.book_controller import BookController
from models.borrow_details_model import BorrowDetailsModel
from models.book_model import BookModel

books_route = APIRouter(tags=["Book Routes"], prefix="/books")


@books_route.get("/")
async def get_all_books(
    controller: BookController = Depends(BookController),
) -> List[BookModel]:
    return controller.get_all()


@books_route.get("/search")
async def search_books(
    category: str | None = None,
    publisher: str | None = None,
    title: str | None = None,
    controller: BookController = Depends(BookController),
) -> List[BookModel]:
    return controller.search_books(category=category, publisher=publisher, title=title)


@books_route.get("/{id}")
async def get_book_by_id(
    id: int, controller: BookController = Depends(BookController)
) -> BookModel:
    return controller.get_by_id(id)


@books_route.post("/{id}/borrow")
async def borrow_book(
    id: int,
    borrow_details: BorrowDetailsModel,
    controller: BookController = Depends(BookController),
) -> BookModel:
    return await controller.borrow_book(id, borrow_details)
