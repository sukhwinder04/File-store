from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from database.database import add_premium_user, remove_premium_user, get_premium_users, is_premium

# Command to add a user to premium
@Bot.on_message(filters.private & filters.command('prem') & filters.user(ADMINS))
async def add_prem_user(client, message):
    try:
        command = message.text.split()
        if len(command) < 3:
            return await message.reply_text("Usage: /add_prem user_id duration (e.g., /add_prem 123456 1m)")
        
        user_id = int(command[1])
        duration = command[2]
        
        success = await add_premium_user(user_id, duration)
        if success:
            await message.reply_text(f"User {user_id} has been added to premium for {duration}.")
        else:
            await message.reply_text("Invalid duration format! Use: 1m (month), 1w (week), 1d (day), 1min (minute)")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

# Command to remove a user from premium
@Bot.on_message(filters.private & filters.command('remove_prem') & filters.user(ADMINS))
async def remove_prem_user_cmd(client, message):
    try:
        command = message.text.split()
        if len(command) < 2:
            return await message.reply_text("Usage: /remove_prem user_id")
        
        user_id = int(command[1])
        await remove_premium_user(user_id)
        await message.reply_text(f"User {user_id} has been removed from premium.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

# Command to see all premium users
@Bot.on_message(filters.private & filters.command('all_prem') & filters.user(ADMINS))
async def list_premium_users(client, message):
    try:
        premium_users = await get_premium_users()
        if not premium_users:
            return await message.reply_text("No premium users found.")
        
        text = "**Premium Users:**\n\n"
        for user in premium_users:
            text += f"User ID: {user['_id']} | Expiry: {user['expiry_date']}\n"
        
        await message.reply_text(text)
    except Exception as e:
        await message.reply_text(f"Error: {e}")

# Command to check if a user is premium
@Bot.on_message(filters.private & filters.command('check_prem'))
async def check_premium_status(client, message):
    try:
        user_id = message.from_user.id
        premium = await is_premium(user_id)
        if premium:
            await message.reply_text("✅ You are a premium user!")
        else:
            await message.reply_text("❌ You are not a premium user.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")
