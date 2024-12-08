import redis.asyncio as aioredis
from datetime import timedelta
from .config import settings
import json

# Function to get Redis connection pool
async def get_redis_pool():
    # Create Redis client using the redis.asyncio interface
    redis = aioredis.from_url(
        settings.REDIS_URL,
        db=settings.REDIS_DB,
        max_connections=settings.REDIS_POOL_SIZE  # Remove timeout from here
    )
    
    # Set connection timeout separately in the Redis connection settings if necessary
    await redis.connection_pool.get_connection("PING")  # Ensures connection is properly established
    return redis

# Function to save data in Redis with expiration time (12 hours)
async def save_to_redis(key: str, value, expiration: int = 43200):  # 43200 seconds = 12 hours
    redis = await get_redis_pool()
    await redis.setex(key, expiration, json.dumps(value))  # Save with expiration time
    await redis.close()

# Function to get data from Redis
async def get_from_redis(key: str):
    redis = await get_redis_pool()
    result = await redis.get(key)
    await redis.close()
    return result
