from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime, timedelta
from config import ADMINS
from database.database import add_premium_user, is_premium, remove_premium_user, get_premium_users

@Client.on_message(filters.command("prem") & filters.user(ADMINS))
async def add_premium_handler(client, message):
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        return await message.reply("Usage: /prem {user_id}")
    
    user_id = int(args[1])
    
    # Generate duration selection buttons
    buttons = [
        [InlineKeyboardButton("1 Min", callback_data=f"prem:{user_id}:1min")],
        [InlineKeyboardButton("1 Day", callback_data=f"prem:{user_id}:1d")],
        [InlineKeyboardButton("1 Month", callback_data=f"prem:{user_id}:1m")],
        [InlineKeyboardButton("3 Months", callback_data=f"prem:{user_id}:3m")],
        [InlineKeyboardButton("1 Year", callback_data=f"prem:{user_id}:12m")]
    ]
    
    await message.reply(
        f"Select premium duration for user {user_id}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex(r"prem:(\d+):(\d*[a-z]+)"))
async def premium_callback(client, callback_query: CallbackQuery):
    user_id, duration = callback_query.data.split(":")[1:]
    user_id = int(user_id)
    
    # Add user to premium
    success = await add_premium_user(user_id, duration)
    
    if success:
        expiry_date = datetime.utcnow() + timedelta(minutes=1) if duration == "1min" else timedelta(days=1) if duration == "1d" else timedelta(days=30) if duration == "1m" else timedelta(days=90) if duration == "3m" else timedelta(days=365)
        expiry_date = datetime.utcnow() + expiry_date
        
        await callback_query.message.edit_text(f"User {user_id} is now premium until {expiry_date.strftime('%Y-%m-%d %H:%M:%S')} UTC.")
        
        # Notify the user
        try:
            await client.send_message(
                user_id,
                f"🎉 Congratulations! You have been upgraded to premium.\n\n✅ Plan: {duration}\n📅 Expiry: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')} UTC\n\nEnjoy your benefits!"
            )
        except:
            pass  # User might have blocked the bot
    else:
        await callback_query.answer("Failed to add user to premium!", show_alert=True)

# Function to check expired users and notify them (to be run periodically)
async def check_expired_premium(client):
    premium_users = await get_premium_users()
    now = datetime.utcnow()
    
    for user in premium_users:
        expiry_date = user["expiry_date"]
        if expiry_date and expiry_date < now:
            user_id = user["_id"]
            await remove_premium_user(user_id)
            
            # Notify user
            try:
                await client.send_message(
                    user_id,
                    "⏳ Your premium subscription has expired. Contact admin to renew."
                )
            except:
                pass  # User might have blocked the bot

@Client.on_message(filters.command("remove_prem") & filters.user(ADMINS))
async def remove_premium_handler(client, message):
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        return await message.reply("Usage: /remove_prem {user_id}")
    
    user_id = int(args[1])
    await remove_premium_user(user_id)
    await message.reply(f"User {user_id} has been removed from premium.")

@Client.on_message(filters.command("all_prem") & filters.user(ADMINS))
async def all_premium_users_handler(client, message):
    premium_users = await get_premium_users()
    if not premium_users:
        return await message.reply("No premium users found.")
    
    user_list = "\n".join([f"User ID: {user['_id']} | Expiry: {user['expiry_date'].strftime('%Y-%m-%d %H:%M:%S')} UTC" for user in premium_users])
    await message.reply(f"📜 List of Premium Users:\n{user_list}")
