from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from .config import settings
import asyncio

producer = None  # Global producer instance
consumer = None  # Global consumer instance

async def get_kafka_producer():
    global producer
    if producer is None:  # Initialize only if producer is not already started
        producer = AIOKafkaProducer(
            loop=asyncio.get_event_loop(),
            bootstrap_servers=settings.KAFKA_BROKER_URL,
        )
        await producer.start()
    return producer

async def get_kafka_consumer(topic: str):
    global consumer
    if consumer is None:
        consumer = AIOKafkaConsumer(
            topic,
            loop=asyncio.get_event_loop(),
            bootstrap_servers=settings.KAFKA_BROKER_URL,
            group_id="my-consumer-group",  # Group to ensure each message is processed only once
            enable_auto_commit=True,        # Enable auto-commit to mark messages as processed
            auto_offset_reset="earliest"    # Start from the earliest message if no offset is found
        )
        await consumer.start()
    return consumer

async def close_kafka_connections():
    global producer, consumer
    if producer:
        await producer.stop()
        producer = None  # Reset to None after stopping
    if consumer:
        await consumer.stop()
        consumer = None  # Reset to None after stopping
