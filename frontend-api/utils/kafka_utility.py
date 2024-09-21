import json
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from utils.environment import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_RETURN_BOOK_TOPIC,
    KAFKA_REMOVE_BOOK_TOPIC,
    KAFKA_ADD_BOOK_TOPIC,
)

def kafka_seriaizer(value: list) -> bytes:
    return json.dumps(value, default=str).encode()


def kafka_deseriaizer(value: bytes) -> list:
    return json.loads(value.decode())

kafka_producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, value_serializer=kafka_seriaizer)


kafka_consumer = AIOKafkaConsumer(
    KAFKA_ADD_BOOK_TOPIC,
    KAFKA_REMOVE_BOOK_TOPIC,
    KAFKA_RETURN_BOOK_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_deserializer=kafka_deseriaizer
)



