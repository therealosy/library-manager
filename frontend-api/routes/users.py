from typing import List
from fastapi import APIRouter, Depends

from controllers.user_controller import UserController
from models.user_model import UserModel

users_route = APIRouter(tags=["User Routes"], prefix="/users")

@users_route.post("/")
async def add_user(
    user: UserModel,
    controller: UserController = Depends(UserController),
) -> UserModel:
    return await controller.add_user(user)


@users_route.get("/{id}")
async def get_user_by_id(
    id: int, controller: UserController = Depends(UserController)
) -> UserModel:
    return controller.get_user_by_id(id)
