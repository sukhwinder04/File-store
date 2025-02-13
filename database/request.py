from motor.motor_asyncio import AsyncIOMotorClient
from config import DB_URI, DB_NAME, FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2

# Connect to MongoDB
mongo_client = AsyncIOMotorClient(DB_URI)
db = mongo_client[DB_NAME]
requests_collection = db["join_requests"]

async def req_channel_exist(chat_id: int) -> bool:
    """Check if a channel exists in the database."""
    return chat_id in [FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2]

async def req_sent_user_exist(user_id: int) -> bool:
    """Check if a user has already requested to join either channel."""
    return await requests_collection.find_one({"user_id": user_id}) is not None

async def req_sent_user(user_id: int):
    """Save a user join request to the database for both channels."""
    await requests_collection.insert_one({"user_id": user_id})

async def del_req_sent_user(user_id: int):
    """Remove a user from the request database for both channels."""
    await requests_collection.delete_one({"user_id": user_id})
