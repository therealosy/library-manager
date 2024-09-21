from abc import abstractmethod, ABC
from typing import List
from database.schema.user_schema import UserSchema
from models.user_model import UserModel
from models.user_update_model import UserUpdateModel


class UserRepositoryMeta(ABC):
    @abstractmethod
    def save(self, user: UserSchema) -> UserModel:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> UserModel:
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> UserModel:
        pass

    @abstractmethod
    def update(self, id: int, user_update: UserUpdateModel) -> UserModel:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass
    
    @abstractmethod
    def close(self) -> None:
        pass
