
import motor.motor_asyncio
from config import DB_URI, DB_NAME

dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database['users']

default_verify = {
    'is_verified': False,
    'verified_time': 0,
    'verify_token': "",
    'link': ""
}

def new_user(id):
    return {
        '_id': id,
        'verify_status': {
            'is_verified': False,
            'verified_time': "",
            'verify_token': "",
            'link': ""
        }
    }

async def present_user(user_id: int):
    found = await user_data.find_one({'_id': user_id})
    return bool(found)

async def add_user(user_id: int):
    user = new_user(user_id)
    await user_data.insert_one(user)
    return

async def db_verify_status(user_id):
    user = await user_data.find_one({'_id': user_id})
    if user:
        return user.get('verify_status', default_verify)
    return default_verify

async def db_update_verify_status(user_id, verify):
    await user_data.update_one({'_id': user_id}, {'$set': {'verify_status': verify}})

async def full_userbase():
    user_docs = user_data.find()
    user_ids = [doc['_id'] async for doc in user_docs]
    return user_ids

async def del_user(user_id: int):
    await user_data.delete_one({'_id': user_id})
    return


async def add_premium_user(user_id: int, duration: str):
    time_map = {'min': 1, 'd': 1440, 'w': 10080, 'm': 43200}
    
    unit = duration[-1]
    if unit not in time_map:
        return False  # Invalid format

    try:
        value = int(duration[:-1])
        minutes = value * time_map[unit]
        expiry_date = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)
        
        await premium_users.update_one(
            {'_id': user_id}, 
            {'$set': {'expiry_date': expiry_date}}, 
            upsert=True
        )
        return True
    except ValueError:
        return False  # Invalid format

async def remove_premium_user(user_id: int):
    await premium_users.delete_one({'_id': user_id})

async def get_premium_users():
    users = premium_users.find()
    return [{'_id': doc['_id'], 'expiry_date': doc['expiry_date']} async for doc in users]

async def is_premium(user_id: int):
    user = await premium_users.find_one({'_id': user_id})
    return bool(user)
