import unittest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime

from aiokafka import AIOKafkaProducer

from models.user_update_model import UserUpdateModel
from service.impl.user_service import UserService
from database.repository.meta.user_repository_meta import UserRepositoryMeta
from models.user_model import UserModel
from utils.custom_exceptions import NotFoundException, BadRequestException


class TestUserService(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.mock_user: UserModel = UserModel(
            id=1,
            email="user@example.com",
            firstname="John",
            lastname="Doe",
            joined_on=datetime.now()
        )
        
        self.mock_repository: UserRepositoryMeta = MagicMock(spec=UserRepositoryMeta)
        self.mock_kafka_producer: AIOKafkaProducer = AsyncMock(spec=AIOKafkaProducer)
        self.user_service = UserService(self.mock_repository, self.mock_kafka_producer)

    async def test_add_user_returns_user(self):
        user_to_add = self.mock_user
        self.mock_repository.save.return_value = user_to_add
        self.mock_kafka_producer.send_and_wait.return_value = None
        
        result = await self.user_service.add(user_to_add)

        self.assertEqual(user_to_add, result)
        
    async def test_add_user_with_invalid_email_raises_bad_request_exception(self):
        user_to_add = UserModel(id=1, email="bad_email", firstname="John", lastname="Doe", joined_on=datetime.now())

        with self.assertRaises(BadRequestException):
            await self.user_service.add(user_to_add)

    def test_find_user_by_id_returns_user(self):
        user = self.mock_user
        self.mock_repository.get_by_id.return_value = user

        result = self.user_service.get_by_id(user.id)

        self.assertEqual(user, result)
        
    def test_find_invalid_user_by_id_raises_not_found_exception(self):
        self.mock_repository.get_by_id.return_value = None

        with self.assertRaises(NotFoundException):
            self.user_service.get_by_id(2)

    async def test_update_user_calls_update_method_with_update_model(self):
        user = self.mock_user
        self.mock_repository.update.return_value = user
        self.mock_kafka_producer.send_and_wait.return_value = None

        update_model = UserUpdateModel(email="newemail@example.com", firstname="Jane", lastname="Doe")

        await self.user_service.update(user.id, update_model)

        self.mock_repository.update.assert_called_with(user.id, update_model)

    async def test_update_invalid_user_raises_not_found_exception(self):
        self.mock_repository.update.return_value = None
        self.mock_kafka_producer.send_and_wait.return_value = None

        update_model = UserUpdateModel(email="newemail@example.com", firstname="Jane", lastname="Doe")

        with self.assertRaises(NotFoundException):
            await self.user_service.update(2, update_model)

            
    def test_rollback_calls_repository_rollback(self):
        self.user_service.rollback()
        self.mock_repository.rollback.assert_called_once()
