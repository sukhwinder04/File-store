import motor.motor_asyncio
import datetime
from config import DB_URI, DB_NAME

# Connect to the MongoDB database
dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]

# Collections
user_data = database['users']
premium_users = database['premium_users']


# Default verification data
default_verify = {
    'is_verified': False,
    'verified_time': 0,
    'verify_token': "",
    'link': ""
}


# New user template with premium set to False
def new_user(user_id: int):
    return {
        'user_id': user_id,
        'verify_status': {
            'is_verified': False,
            'verified_time': "",
            'verify_token': "",
            'link': ""
        },
        'premium': False  # Default: Not a premium user
    }

# Check if a user exists in the database
async def present_user(user_id: int):
    found = await user_data.find_one({'user_id': user_id})
    return bool(found)

# Add a new user to the database
async def add_user(user_id: int):
    user = new_user(user_id)
    await user_data.insert_one(user)

# Get verification status of a user
async def db_verify_status(user_id: int):
    user = await user_data.find_one({'user_id': user_id})
    return user.get('verify_status', {}) if user else {}

# Update verification status of a user
async def db_update_verify_status(user_id: int, verify):
    await user_data.update_one({'user_id': user_id}, {'$set': {'verify_status': verify}})

# Get all user IDs in the database
async def full_userbase():
    user_docs = user_data.find()
    return [doc['user_id'] async for doc in user_docs]

# Delete a user from the database
async def del_user(user_id: int):
    await user_data.delete_one({'user_id': user_id})

# Add a user to premium with expiry duration
async def add_premium_user(user_id: int, duration: str):
    time_map = {'min': 1, 'd': 1440, 'w': 10080, 'm': 43200}
    
    unit = duration[-1]
    if unit not in time_map:
        return False  # Invalid format

    try:
        value = int(duration[:-1])
        minutes = value * time_map[unit]
        expiry_date = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)
        
        # Update premium status in users collection
        await user_data.update_one(
            {'user_id': user_id}, 
            {'$set': {'premium': True, 'expiry_date': expiry_date}}, 
            upsert=True
        )
        return True
    except ValueError:
        return False  # Invalid format

# Remove a user from premium
async def remove_premium_user(user_id: int):
    await user_data.update_one({'user_id': user_id}, {'$set': {'premium': False, 'expiry_date': None}})

# Get all premium users
async def get_premium_users():
    users = user_data.find({'premium': True})
    return [{'_id': doc['user_id'], 'expiry_date': doc['expiry_date']} async for doc in users]

# Check if a user is premium
async def is_premium(user_id: int):
    user = await user_data.find_one({'user_id': user_id})
    return bool(user and user.get('premium', False))  # Check if 'premium' is True
