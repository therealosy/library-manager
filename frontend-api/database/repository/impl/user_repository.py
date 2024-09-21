from sqlalchemy.orm import Session
from database.repository.meta.user_repository_meta import UserRepositoryMeta
from database.schema.user_schema import UserSchema
from models.user_model import UserModel
from models.user_update_model import UserUpdateModel
from utils.dependecy_resolver import ResolveDependency
from utils.logger_utility import getlogger


class UserRepository(UserRepositoryMeta):

    _logger = getlogger(name="UserRepository")

    def __init__(self, db: Session = ResolveDependency(Session)) -> None:
        self.db = db

    def save(self, user: UserSchema) -> UserModel:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self.db.query(UserSchema).filter(UserSchema.email == user.email).first()

    def get_by_id(self, id: int) -> UserModel:
        return self.db.query(UserSchema).filter(UserSchema.id == id).first()
    
    def get_by_email(self, email: str) -> UserModel:
        return self.db.query(UserSchema).filter(UserSchema.email == email).first()

    def update(self, id: int, user_update: UserUpdateModel) -> UserModel:
        self.db.query(UserSchema).filter(UserSchema.id == id).update(
            user_update.model_dump(exclude_none=True)
        )
        self.db.commit()
        return self.db.query(UserSchema).filter(UserSchema.id == id).first()

    def rollback(self) -> None:
        self.db.rollback()
