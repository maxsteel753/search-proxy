from fastapi import Depends, HTTPException, APIRouter
from app.redis import save_to_redis, get_from_redis
from app.db import get_database
from app.services.dbService import dbService
from app.services.kafka import KafkaServices   
import json

from asyncio import create_task

router = APIRouter()
db_service = dbService

@router.post("/check")
async def check_or_send_to_kafka(
    q: str,
    page: int | None = 1,
    pagesize: int | None = 8,
    db=Depends(get_database)
):
    kafka_service = KafkaServices()
    redis_key = f"{q}:{page}:{pagesize}"  # Unique Redis key for query and pagination
    primary_redis_key = str("test_" + q)  # Key for raw MongoDB data

    # Step 1: Check for paginated data in Redis
    try:
        cached_result = await get_from_redis(redis_key)
        # if cached_result:
        #     return {"result": json.loads(cached_result.decode("utf-8")), "source": "cache (Redis)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing Redis: {e}")

    # Step 2: Check if the raw data is in MongoDB or Redis
    try:
        mongo_result = await db_service.get_from_mongo_with_pagination_and_related(
            db,
            skip=(page - 1) * pagesize,
            limit=pagesize,
            search_text=q
        )
        if mongo_result and mongo_result.get("total_count", 0) > 0:
            # Save raw MongoDB result to Redis for future use
            try:
                await save_to_redis(primary_redis_key, mongo_result)
            except Exception as e:
                print(f"Error saving raw data to Redis: {e}")

        if mongo_result and mongo_result.get("total_count", 0) > 0:
            # Save the data (paginated) to Redis
            try:
                await save_to_redis(redis_key, mongo_result)
            except Exception as e:
                print(f"Error saving data to Redis: {e}")
            return {"result": mongo_result, "source": "cache (MongoDB)"}

        # If no results, send the query to Kafka
        if mongo_result.get("total_count", 0) == 20 :
            create_task(kafka_service.send_message(q))
            return mongo_result.update({
                "message": f"Query '{q}' sent to Kafka for processing.", "source": "Kafka (background)"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing MongoDB: {e}")

    # Step 3: Send query to Kafka in the background if MongoDB returns no data
    try:
        create_task(kafka_service.send_message(q))
        return {"message": f"Query '{q}' sent to Kafka for processing.", "source": "Kafka (background)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scheduling query for Kafka: {e}")
