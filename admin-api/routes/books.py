from typing import List
from fastapi import APIRouter, Depends

from controllers.book_controller import BookController
from models.book_model import BookModel
from models.borrowed_book_model import BorrowedBookModel

books_route = APIRouter(tags=["Book Routes"], prefix="/books")


@books_route.get("/")
async def get_all_books(
    controller: BookController = Depends(BookController),
) -> List[BookModel]:
    return controller.get_all_books()


@books_route.get("/borrowed")
async def get_all_borrowed_books(
    controller: BookController = Depends(BookController),
) -> List[BorrowedBookModel]:
    return controller.get_all_borrowed_books()


@books_route.get("/{id}")
async def get_book_by_id(
    id: int, controller: BookController = Depends(BookController)
) -> BookModel:
    return controller.get_book_by_id(id)


@books_route.post("/")
async def add_book(
    book: BookModel,
    controller: BookController = Depends(BookController),
) -> BookModel:
    return await controller.add_book(book)

@books_route.delete("/{id}")
async def remove_book(
    id: int,
    controller: BookController = Depends(BookController),
) -> BookModel:
    return await controller.remove_book(id)
