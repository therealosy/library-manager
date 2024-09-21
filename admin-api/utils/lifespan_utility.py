from contextlib import asynccontextmanager
from aiokafka import AIOKafkaConsumer
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from fastapi import FastAPI, Depends

from database.repository.impl.borrow_entry_repository import BorrowEntryRepository
from models.book_model import BookModel
from models.borrow_details_model import BorrowDetailsModel
from models.borrow_entry_model import BorrowEntryModel
from models.user_model import UserModel
from models.user_update_model import UserUpdateModel
from service.impl.book_service import BookService
from service.meta.book_service_meta import BookServiceMeta
from service.impl.user_service import UserService
from service.meta.user_service_meta import UserServiceMeta
from database.repository.impl.book_repository import BookRepository
from database.repository.impl.user_repository import UserRepository
from utils.environment import (
    KAFKA_BORROW_BOOK_TOPIC,
    KAFKA_CREATE_USER_TOPIC,
    KAFKA_UPDATE_USER_TOPIC,
    POLL_FRONTEND_INTERVAL_SECS,
    UPDATE_RETURNED_BOOKS_CRONTAB,
)
from database.schema.database import SessionLocal
from utils.kafka_utility import kafka_consumer, kafka_producer
from utils.logger_utility import getlogger

logger = getlogger(__name__)


@asynccontextmanager
async def lifecycle_manager(app: FastAPI):
    # Start Kafka Producer and Consumer
    await kafka_producer.start()
    await kafka_consumer.start()

    book_service = get_book_service()

    # Create Async Background Scheduler
    scheduler = AsyncIOScheduler()

    # Listen for updates from the front end at intervals
    logger.info(
        f"Will check for frontend updates every {POLL_FRONTEND_INTERVAL_SECS} seconds"
    )
    scheduler.add_job(
        func=check_front_end_updates,
        trigger="interval",
        seconds=POLL_FRONTEND_INTERVAL_SECS,
    )

    logger.info(
        f"Will update for returns using the cron expression: {UPDATE_RETURNED_BOOKS_CRONTAB}"
    )
    scheduler.add_job(
        func=check_books_for_returns,
        trigger=CronTrigger.from_crontab(UPDATE_RETURNED_BOOKS_CRONTAB),
    )

    # Start Scheduler
    scheduler.start()

    yield

    # Shutdown all background activities before application shutdown
    scheduler.shutdown()
    await kafka_producer.stop()
    await kafka_consumer.stop()


def get_book_service():
    return BookService(
        book_repository=BookRepository(db=SessionLocal()),
        borrow_entry_repository=BorrowEntryRepository(db=SessionLocal()),
        kafka_producer=kafka_producer,
    )


def get_user_service():
    return UserService(user_repository=UserRepository(db=SessionLocal()))


def handle_create_user_message(
    message_value: list,
    user_service: UserServiceMeta = get_user_service(),
):
    for user_entry in message_value:
        try:
            user = UserModel.model_validate(user_entry)
            user_service.add(user)
            logger.info(f"Added user with {user.email}")
        except Exception as e:
            logger.error(f"Failed to add user {user_entry} due to: {e}")
            user_service.rollback()


def handle_borrow_book_message(
    message_value: list,
    book_service: BookServiceMeta = get_book_service(),
    user_service: UserServiceMeta = get_user_service(),
) -> None:
    for borrow_entry in message_value:
        try:
            entry = BorrowDetailsModel.model_validate(borrow_entry)
            user = user_service.get_by_email(entry.user_email)
            book_service.borrow_book(
                entry.book_title, user.id, entry.borrow_duration_days
            )
            logger.info(f"Added borrow entry for {entry.book_title}")
        except Exception as e:
            logger.error(f"Failed to add borrow entry {borrow_entry} due to: {e}")
            book_service.rollback()


async def check_front_end_updates(
    consumer: AIOKafkaConsumer = kafka_consumer,
):
    logger.info("Checking for updates from the frontend")
    try:
        messages = await consumer.getmany(timeout_ms=10000)

        if not messages:
            logger.info("No front end updates found")
            return

        logger.info(f"Found messages: {messages}")

        for tp, message_list in messages.items():
            for message in message_list:
                if message.topic == KAFKA_CREATE_USER_TOPIC:
                    handle_create_user_message(message.value)

                elif message.topic == KAFKA_BORROW_BOOK_TOPIC:
                    handle_borrow_book_message(message.value)

                else:
                    logger.info("No relevant updated information found")

    except Exception as e:
        logger.error(f"Failed to listen for book updates due to: {e}")
    finally:
        logger.info("Done Checking for book updates")


async def check_books_for_returns(book_service: BookServiceMeta = get_book_service()):
    logger.info("Checking for books due for returns")
    try:
        due_borrow_entries = book_service.get_all_due()
    except Exception as e:
        logger.error(f"Failed to retrieve due books because: {e}")
        return
    for entry in due_borrow_entries:
        try:
            await book_service.return_book(entry.id)
        except Exception as e:
            logger.error(f"Failed to return due entry with id {entry.id} because: {e}")
