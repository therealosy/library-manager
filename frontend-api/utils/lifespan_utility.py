from contextlib import asynccontextmanager
from aiokafka import AIOKafkaConsumer
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from fastapi import FastAPI, Depends

from models.book_model import BookModel
from service.impl.book_service import BookService
from service.meta.book_service_meta import BookServiceMeta
from database.repository.impl.book_repository import BookRepository
from utils.environment import (
    KAFKA_ADD_BOOK_TOPIC,
    KAFKA_REMOVE_BOOK_TOPIC,
    KAFKA_RETURN_BOOK_TOPIC,
    POLL_ADMIN_INTERVAL_SECS,
)
from database.schema.database import SessionLocal
from utils.kafka_utility import kafka_consumer, kafka_producer, kafka_deseriaizer
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

    # Listen for book updates from the admin at intervals
    logger.info(f"Will check for admin updates every {POLL_ADMIN_INTERVAL_SECS} seconds")
    scheduler.add_job(
        func=check_admin_updates, trigger="interval", seconds=POLL_ADMIN_INTERVAL_SECS
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
        kafka_producer=kafka_producer,
    )


def handle_add_book_message(
    message_value: list,
    book_service: BookServiceMeta = get_book_service(),
) -> None:
    for book_message in message_value:
        try:
            book = BookModel.model_validate(book_message)
            book_service.add(book)
            logger.info(f"Added book with title {book.title}")
        except Exception as e:
            logger.error(f"Failed to add book {book_message} due to: {e}")
            book_service.rollback()


def handle_return_book_message(
    message_value: list,
    book_service: BookServiceMeta = get_book_service(),
) -> None:
    for book_title in message_value:
        try:
            book = book_service.get_by_title(book_title)
            book_service.return_book(book.id)
            logger.info(f"Returned book with title {book_title}")
        except Exception as e:
            logger.error(f"Failed to return book {book_title} due to: {e}")
            book_service.rollback()


def handle_delete_book_message(
    message_value: list,
    book_service: BookServiceMeta = get_book_service(),
) -> None:
    for book_title in message_value:
        try:
            book = book_service.get_by_title(book_title)
            book_service.remove_book(book.id)
            logger.info(f"Deleted book {book_title}")
        except Exception as e:
            logger.error(f"Failed to delete book {book_title} due to: {e}")
            book_service.rollback()


async def check_admin_updates(
    consumer: AIOKafkaConsumer = kafka_consumer,
):
    logger.info("Checking for updated book information")
    try:
        messages = await consumer.getmany(timeout_ms=10000)

        if not messages:
            logger.info("No book updates found")
            return

        logger.info(f"Found messages: {messages}")

        for tp, message_list in messages.items():
            for message in message_list:
                if message.topic == KAFKA_RETURN_BOOK_TOPIC:
                    handle_return_book_message(message.value)

                elif message.topic == KAFKA_REMOVE_BOOK_TOPIC:
                    handle_delete_book_message(message.value)

                elif message.topic == KAFKA_ADD_BOOK_TOPIC:
                    handle_add_book_message(message.value)

                else:
                    logger.info("No relevant updated information found")

    except Exception as e:
        logger.error(f"Failed to listen for book updates due to: {e}")
    finally:
        logger.info("Done Checking for book updates")
