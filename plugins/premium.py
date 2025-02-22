import datetime
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from bot import Bot
from config import ADMINS
from database.database import user_data

# Time mappings for premium duration
time_map = {'min': 1, 'd': 1440, 'm': 43200, '3m': 129600, 'y': 525600}

# Function to generate premium buttons
def get_premium_buttons(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1 Min", callback_data=f"prem_{user_id}_1min")],
        [InlineKeyboardButton("1 Day", callback_data=f"prem_{user_id}_1d")],
        [InlineKeyboardButton("1 Month", callback_data=f"prem_{user_id}_1m")],
        [InlineKeyboardButton("3 Months", callback_data=f"prem_{user_id}_3m")],
        [InlineKeyboardButton("1 Year", callback_data=f"prem_{user_id}_1y")]
    ])

# /prem {user_id} command
@Bot.on_message(filters.command("prem") & filters.user(ADMINS))
async def add_premium_menu(client, message: Message):
    if len(message.command) < 2:
        await message.reply("Usage: `/prem user_id`", parse_mode="markdown")
        return
    
    user_id = message.command[1]
    await message.reply(
        f"Select the duration for premium user `{user_id}`:",
        reply_markup=get_premium_buttons(user_id)
    )

# Handle premium button clicks
@Bot.on_callback_query(filters.regex(r"^prem_(\d+)_(\w+)$"))
async def handle_premium_button(client, query: CallbackQuery):
    user_id = int(query.matches[0].group(1))
    duration_key = query.matches[0].group(2)

    if duration_key not in time_map:
        await query.answer("Invalid duration selected!", show_alert=True)
        return

    minutes = time_map[duration_key]
    expiry_date = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)

    # Update database
    await user_data.update_one(
        {'user_id': user_id}, 
        {'$set': {'premium': True, 'expiry_date': expiry_date}}, 
        upsert=True
    )

    await query.answer("✅ User added to premium!", show_alert=True)
    await client.send_message(user_id, f"🎉 You have been added to premium for {duration_key}!")

# /remove_prem {user_id} command
@Bot.on_message(filters.command("remove_prem") & filters.user(ADMINS))
async def remove_premium(client, message: Message):
    if len(message.command) < 2:
        await message.reply("Usage: `/remove_prem user_id`", parse_mode="markdown")
        return

    user_id = int(message.command[1])
    await user_data.update_one({'user_id': user_id}, {'$set': {'premium': False, 'expiry_date': None}})
    await message.reply(f"✅ Removed user `{user_id}` from premium.")

# /all_prem command - List all premium users
@Bot.on_message(filters.command("all_prem") & filters.user(ADMINS))
async def list_premium_users(client, message: Message):
    users = user_data.find({'premium': True})
    premium_list = [f"`{doc['user_id']}` - Expires: {doc['expiry_date']}" async for doc in users]

    if premium_list:
        await message.reply("👑 **Premium Users:**\n\n" + "\n".join(premium_list))
    else:
        await message.reply("❌ No premium users found.")

# Notify user when premium expires
async def check_premium_expiry():
    while True:
        now = datetime.datetime.utcnow()
        expired_users = user_data.find({'premium': True, 'expiry_date': {'$lte': now}})

        async for user in expired_users:
            user_id = user['user_id']
            await user_data.update_one({'user_id': user_id}, {'$set': {'premium': False, 'expiry_date': None}})
            try:
                await Bot.send_message(user_id, "❌ Your premium has expired. Contact admin to renew.")
            except Exception:
                pass  # Ignore errors if user has blocked bot
        
        await asyncio.sleep(3600)  # Check every hour
