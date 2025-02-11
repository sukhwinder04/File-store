from motor.motor_asyncio import AsyncIOMotorClient
from config import DB_URI, DB_NAME

# Connect to MongoDB
mongo_client = AsyncIOMotorClient(DB_URI)
db = mongo_client[DB_NAME]
requests_collection = db["join_requests"]

async def req_channel_exist(chat_id: int) -> bool:
    """Check if a channel exists in the database."""
    channel = await requests_collection.find_one({"chat_id": chat_id})
    return bool(channel)

async def req_sent_user_exist(chat_id: int, user_id: int) -> bool:
    """Check if a user has already requested to join."""
    return await requests_collection.find_one({"chat_id": chat_id, "user_id": user_id}) is not None

async def req_sent_user(chat_id: int, user_id: int):
    """Save a user join request to the database."""
    await requests_collection.insert_one({"chat_id": chat_id, "user_id": user_id})

async def del_req_sent_user(chat_id: int, user_id: int):
    """Remove a user from the request database."""
    await requests_collection.delete_one({"chat_id": chat_id, "user_id": user_id})
