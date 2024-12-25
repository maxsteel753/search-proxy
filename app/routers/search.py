from fastapi import Depends, HTTPException, APIRouter
from app.services.searchResult import scrape_google_results
from app.redis import save_to_redis, get_from_redis
from app.db import get_database
from app.services.dbService import dbService
from app.services.kafka import KafkaServices   
import json
from app.services.transformer import transform_API_data

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
    primary_redis_key = q  # Key for raw MongoDB data

    # Step 1: Check if the data is in Redis
    try:
        # Check for paginated data in Redis
        cached_result = await get_from_redis(redis_key)
        if cached_result:
            return {"result": cached_result.decode("utf-8"), "source": "cache (Redis)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing Redis: {e}")

    # Step 2: Check if the raw data is in MongoDB or Redis
    try:
        cached_main_result = await get_from_redis(primary_redis_key)
        if cached_main_result:
            mongo_result = cached_main_result.decode("utf-8")
        else:
            mongo_result = await db_service.get_from_mongo(db, "google_search_results", q)
            if mongo_result:
                # Save raw MongoDB result to Redis for future use
                try:
                    await save_to_redis(primary_redis_key, mongo_result)
                except Exception as e:
                    print(f"Error saving raw data to Redis: {e}")
        
        if mongo_result:
            # Transform the MongoDB result into paginated format
            transformed_data = transform_API_data(mongo_result, page=page, page_size=pagesize)
            if (transformed_data and "error" not in transformed_data):
                # Save the transformed data (paginated) to Redis
                try:
                    await save_to_redis(redis_key, transformed_data)
                except Exception as e:
                    print(f"Error saving transformed data to Redis: {e}")
                return {"result": transformed_data, "source": "cache (MongoDB)"}
            else:
                return transformed_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing MongoDB: {e}")

    # Step 3: Send query to Kafka
    try:
        print(q)
        await kafka_service.send_message(q)
        return {"message": f"Query '{q}' sent to Kafka for processing.", "source": "Kafka"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending query to Kafka: {e}")



# @router.post("/")
# async def fetching_google_search_result(q: str, db = Depends(get_database)):
#     # Step 1: Check if the data is in Redis
#     cached_result = await get_from_redis(q)
    
#     if cached_result:
#         # If data is found in Redis, return it (decode from bytes)
#         return {"result": json.loads(cached_result.decode("utf-8")), "source": "cache (Redis)"}
    
#     # Step 2: Check if the data is in MongoDB
#     mongo_result = await db_service.get_from_mongo(db, "google_search_results", q)
    
#     if mongo_result:
#         # If data is found in MongoDB, return it
#         return {"result": mongo_result['result'], "source": "cache (MongoDB)"}
    
#     # Step 3: Scrape data if not found in Redis or MongoDB
#     result = await scrape_google_results(q)
    
#     # Step 4: Check if the result is empty
#     if len(result)<=0:
#         raise HTTPException(status_code=400, detail="Scraped result is empty, no data to save.")
    
#     # Save the valid result to Redis with a 12-hour expiration time
#     await save_to_redis(q, result, expiration=43200)

#     # Save the valid result to MongoDB
#     await db_service.save_to_mongo(db, "google_search_results", {"q": q, "result": result})
    
#     return {"result": result, "source": "scraped"}
