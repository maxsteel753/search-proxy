import asyncio
from app.kafka import get_kafka_producer, get_kafka_consumer

class KafkaServices:

    @staticmethod  # Added the static method decorator
    async def send_message(message: str):
        # Temporarily remove Kafka code to test if the endpoint works without Kafka
        producer = await get_kafka_producer()
        try:
            await asyncio.wait_for(
                producer.send_and_wait("navigaze", value=message.encode('utf-8')), timeout=1
            )
        except TimeoutError:
            return {"error": "Kafka producer timed out"}
        return {"message": "Message sent to Kafka", "data": message}

    
    # async def receive_messages(self):
    #     topic = "navizage-search"
    #     consumer = await get_kafka_consumer(topic)
        
    #     messages = []
    #     try:
    #         await asyncio.wait_for(self.consume_messages(consumer, messages), timeout=1)
    #     except asyncio.TimeoutError:
    #         # No need to raise an error; return an empty object instead
    #         return {"messages": [],"error":"No New Messages"}
        
    #     return {"messages": messages}

    # async def consume_messages(consumer, messages, max_messages=1):
    #     async for msg in consumer:
    #         messages.append(msg.value.decode('utf-8'))
    #         if len(messages) >= max_messages:
    #             break