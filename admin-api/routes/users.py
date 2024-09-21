from typing import List
from fastapi import APIRouter, Depends

from controllers.user_controller import UserController
from models.user_books_model import UserBooksModel
from models.user_model import UserModel

users_route = APIRouter(tags=["User Routes"], prefix="/users")


@users_route.get("/")
async def get_all_users(
    controller: UserController = Depends(UserController),
) -> List[UserModel]:
    return controller.get_all_users()


@users_route.get("/books")
async def get_all_users_with_books(
    include_returned: bool = True,
    controller: UserController = Depends(UserController),
) -> List[UserBooksModel]:
    return controller.get_all_users_with_books(include_returned)


@users_route.get("/{id}")
async def get_user_by_id(
    id: int, controller: UserController = Depends(UserController)
) -> UserModel:
    return controller.get_user_by_id(id)
