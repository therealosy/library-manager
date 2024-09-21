from abc import abstractmethod, ABC
from models.user_model import UserModel
from models.user_update_model import UserUpdateModel


class UserServiceMeta(ABC):
    @abstractmethod
    def add(self, user: UserModel) -> UserModel:
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
    def validate_email(self, email: str):
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        pass
    
    @abstractmethod
    def close(self) -> None:
        pass