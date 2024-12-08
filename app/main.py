from fastapi import FastAPI
from .db import connect_to_mongo, close_mongo_connection
from .kafka import get_kafka_producer, close_kafka_connections
#get_kafka_consumer
from contextlib import asynccontextmanager
# from app.routers import tracking_configuration
from app.routers import search

@asynccontextmanager
async def lifespan_context(app):
    # Connect to MongoDB
    await connect_to_mongo()
    # Start Kafka producer
    await get_kafka_producer()
    # await get_kafka_consumer("navizage")
    yield
    # Clean up connections
    await close_mongo_connection()
    await close_kafka_connections()

app = FastAPI(lifespan=lifespan_context)

# app.include_router(tracking_configuration.router, prefix="/tracking-configuration", tags=["Configuration"])
app.include_router(search.router,prefix="/google",tags=["search"])

@app.get("/")
async def root():
    
    return {"message": "Server Working fine"}

