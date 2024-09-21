from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import punq
from sqlalchemy.orm import Session

from database.repository.impl.book_repository import BookRepository
from database.repository.impl.borrow_entry_repository import BorrowEntryRepository
from database.repository.impl.user_repository import UserRepository
from database.repository.meta.book_repository_meta import BookRepositoryMeta
from database.repository.meta.borrow_entry_repository_meta import BorrowEntryRepositoryMeta
from database.repository.meta.user_repository_meta import UserRepositoryMeta
from database.schema.database import SessionLocal
from service.impl.book_service import BookService
from service.impl.user_service import UserService
from service.meta.book_service_meta import BookServiceMeta
from service.meta.user_service_meta import UserServiceMeta

from utils.kafka_utility import kafka_producer, kafka_consumer

def db_session():
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.rollback()
    finally:
        db.close()

def get_container() -> punq.Container:
    container = punq.Container()

    # Resgister Services
    container.register(BookServiceMeta, BookService)
    container.register(UserServiceMeta, UserService)

    # Register Repositories
    container.register(BookRepositoryMeta, BookRepository)
    container.register(BorrowEntryRepositoryMeta, BorrowEntryRepository)
    container.register(UserRepositoryMeta, UserRepository)

    # Register Database Session
    container.register(Session, factory=db_session)

    # Register Kafka Producer and Consumer Singleton
    container.register(AIOKafkaProducer, instance=kafka_producer)
    container.register(AIOKafkaConsumer, instance=kafka_consumer)

    return container
