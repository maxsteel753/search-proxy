from fastapi import Depends, HTTPException, APIRouter
from app.services.searchResult import scrape_google_results
from app.redis import save_to_redis, get_from_redis
from app.db import get_database
from app.services.dbService import dbService
from app.services.kafka import KafkaServices  
import json


router = APIRouter()
db_service = dbService
kafka_service = KafkaServices

@router.post("/check")
async def check_or_send_to_kafka(q: str):
    # Step 1: Check if the data is in Redis
    cached_result = await get_from_redis(q)
    
    if cached_result:
        # If data is found in Redis, return it (decode from bytes)
        return {"result": cached_result.decode("utf-8"), "source": "cache (Redis)"}
    
    # Step 2: If not found in Redis, send query to Kafka
     # Step 2: Check if the data is in MongoDB
    mongo_result = await db_service.get_from_mongo(db, "google_search_results", q)
    
    if mongo_result:
        # If data is found in MongoDB, return it
        return {"result": mongo_result['result'], "source": "cache (MongoDB)"}
    
    try:
        await kafka_service.send_message(q)
        return {"message": f"Query '{q}' sent to Kafka for processing.", "source": "Kafka"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending query to Kafka: {e}")

@router.post("/")
async def fetching_google_search_result(q: str, db = Depends(get_database)):
    # Step 1: Check if the data is in Redis
    cached_result = await get_from_redis(q)
    
    if cached_result:
        # If data is found in Redis, return it (decode from bytes)
        return {"result": json.loads(cached_result.decode("utf-8")), "source": "cache (Redis)"}
    
    # Step 2: Check if the data is in MongoDB
    mongo_result = await db_service.get_from_mongo(db, "google_search_results", q)
    
    if mongo_result:
        # If data is found in MongoDB, return it
        return {"result": mongo_result['result'], "source": "cache (MongoDB)"}
    
    # Step 3: Scrape data if not found in Redis or MongoDB
    result = await scrape_google_results(q)
    
    # Step 4: Check if the result is empty
    if len(result)<=0:
        raise HTTPException(status_code=400, detail="Scraped result is empty, no data to save.")
    
    # Save the valid result to Redis with a 12-hour expiration time
    await save_to_redis(q, result, expiration=43200)

    # Save the valid result to MongoDB
    await db_service.save_to_mongo(db, "google_search_results", {"q": q, "result": result})
    
    return {"result": result, "source": "scraped"}
