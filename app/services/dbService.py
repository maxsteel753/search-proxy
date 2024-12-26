from fastapi import  HTTPException
import json

class dbService:

    async def save_to_mongo(db,collection_name,data):
        collection = db[collection_name]
        result = await collection.insert_one(data)
        return result.inserted_id


    async def get_from_mongo(db,collection_name,key):
        collection = db[collection_name]
        result = await collection.find_one({"q": key})
        if result:
            return result
        else:
            return None
    
    @staticmethod
    async def get_from_mongo_with_pagination_and_related(db, skip: int, limit: int, filters: dict = None, search_text: str = None):
        """
        Retrieve documents from the specified MongoDB collection with pagination and optional filters or text search.
        Additionally, fetch related queries from another collection.

        Args:
            db: The database connection.
            skip: The number of records to skip.
            limit: The maximum number of records to return.
            filters: A dictionary of filters to apply (optional).
            search_text: Text to search in the "title" field (optional).

        Returns:
            A dictionary containing the total count, the list of documents, and related queries.
        """
        collection = db["search_results"]
        related_collection = db["related_queries"]
        try:
            query = filters if filters else {}

            # Initialize related queries
            related_queries = []

            if search_text:
                # Modify the query to match any substring in the title field
                query["$or"] = [
                    {"keyword": search_text},  # Exact match on 'keyword'
                    {"title": {"$regex": f".*{search_text}.*", "$options": "i"}}  # Match substring in 'title'
                ]

                # Fetch related queries (limit to 6)
                async for related in related_collection.find(query).limit(6):
                    related_queries.append(related.get("title", ""))

            # Execute the main query with pagination
            cursor = collection.find(query).skip(skip).limit(limit)
            results = []
            async for document in cursor:
                document["_id"] = str(document["_id"])  # Convert ObjectId to string
                results.append(document)

            # Get the total count of matching documents
            total_count = await collection.count_documents(query)

            return {
                "total_count": total_count,
                "results": results,
                "related_queries": related_queries
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve data: {str(e)}")
