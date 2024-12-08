from fastapi import  HTTPException


class dbService:

    async def save_to_mongo(db,collection_name,data):
        collection = db[collection_name]
        result = await collection.insert_one(data)
        return result.inserted_id


    async def get_from_mongo(db,collection_name,key):
        collection = db[collection_name]
        result = await collection.find_one({"q": key})
        return result