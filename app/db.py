from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client = None
db = None

async def connect_to_mongo():
    global client, db
    if client is None:
        client =  AsyncIOMotorClient(settings.MONGODB_URL)
        print("mongo connected")
        db = client["google-search"]  # Set db here
    return client

async def get_database():
    if db is None:
        await connect_to_mongo()  # Ensure the connection is established
    return db
async def close_mongo_connection():
    if client:
        client.close()
