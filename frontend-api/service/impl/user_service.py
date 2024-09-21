from aiokafka import AIOKafkaProducer
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
import re

from database.repository.impl.user_repository import UserRepository
from database.repository.meta.user_repository_meta import UserRepositoryMeta
from database.schema.user_schema import UserSchema
from models.user_model import UserModel
from models.user_update_model import UserUpdateModel
from service.meta.user_service_meta import UserServiceMeta
from utils.environment import KAFKA_CREATE_USER_TOPIC, KAFKA_UPDATE_USER_TOPIC
from utils.custom_exceptions import BadRequestException, NotFoundException, ConflictException
from utils.dependecy_resolver import ResolveDependency
from utils.logger_utility import getlogger


class UserService(UserServiceMeta):

    _logger = getlogger(name="UserService")

    def __init__(
        self,
        user_repository: UserRepositoryMeta = ResolveDependency(UserRepositoryMeta),
        kafka_producer: AIOKafkaProducer = ResolveDependency(AIOKafkaProducer),
    ) -> None:
        self.repository = user_repository
        self.kafka_producer = kafka_producer

    async def add(self, user: UserModel) -> UserModel:
        
        if not self.validate_email(user.email):
            raise BadRequestException("Invalid Email Supplied")
        
        try:
            saved_user = UserModel.model_validate(
                self.repository.save(
                    UserSchema(
                        email=user.email,
                        firstname=user.firstname,
                        lastname=user.lastname,
                    )
                )
            )

            # Send user info to the admin api on creation
            await self.kafka_producer.send_and_wait(
                KAFKA_CREATE_USER_TOPIC, [saved_user.model_dump()]
            )

            return saved_user
        except IntegrityError as e:
            self.rollback()
            if isinstance(e.orig, UniqueViolation):
                error_msg = f"User with email {user.email} already exists"
                self._logger.error(error_msg)
                raise ConflictException(error_msg)
            else:
                self._logger.error(f"Integrity error occurred: {e.orig}")
                raise Exception(e.orig)
        except Exception as e:
            self._logger.error(f"Failed to save user {user.email} due to: {e}")
            self.rollback()
            raise Exception(e)

    def get_by_id(self, id: int) -> UserModel:
        try:
            user = self.repository.get_by_id(id)
        except Exception as e:
            self._logger.error(f"Failed to find user with id {id} due to: {e}")
            raise Exception(e)

        if user is None:
            raise NotFoundException("User not found")

        return user

    async def update(self, id: int, user_update: UserUpdateModel) -> UserModel:
        
        if user_update.email and not self.validate_email(user_update.email):
            raise BadRequestException("Invalid Email Supplied")
        
        try:
            user = self.repository.update(id, user_update)
        except Exception as e:
            self._logger.error(f"Failed to update user with id {id} due to: {e}")
            self.rollback()
            raise Exception(e)

        if user is None:
            raise NotFoundException("User not found")

        # Send user info to the admin api on creation
        await self.kafka_producer.send_and_wait(
            KAFKA_UPDATE_USER_TOPIC, [user_update.model_dump()]
        )

        return user

    def get_by_email(self, email: str) -> UserModel:
        try:
            user = self.repository.get_by_email(email)
        except Exception as e:
            self._logger.error(f"Failed to find user with email {email} due to: {e}")
            raise Exception(e)

        if user is None:
            raise NotFoundException("User not found")

        return user
    
    def validate_email(self, email: str):
        email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
        return email_regex.match(email)
    
    def rollback(self) -> None:
        self.repository.rollback()
