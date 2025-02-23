from pyrogram import filters
from pyrogram.types import Message
from bot import Bot
from config import ADMINS
from database.database import add_premium_user, remove_premium_user, get_premium_users, is_premium

@Bot.on_message(filters.private & filters.command("prem") & filters.user(ADMINS))
async def add_premium_command(bot, message: Message):
    if len(message.command) < 3:
        return await message.reply("Usage: /prem user_id time (1min, 1day, 1month)")
    
    user_id = int(message.command[1])
    duration = message.command[2]
    
    valid_durations = {"1min": "1min", "1day": "1d", "1month": "1m"}
    
    if duration not in valid_durations:
        return await message.reply("Invalid duration! Use: 1min, 1day, or 1month.")
    
    success = await add_premium_user(user_id, valid_durations[duration])
    if success:
        await message.reply("User successfully added to premium!")
        try:
            await bot.send_message(user_id, "🎉 You have been added to Premium! Enjoy your benefits!")
        except:
            pass
    else:
        await message.reply("Failed to add user to premium!")

@Bot.on_message(filters.private & filters.command("remove_prem") & filters.user(ADMINS))
async def remove_premium_command(bot, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /remove_prem user_id")
    
    user_id = int(message.command[1])
    await remove_premium_user(user_id)
    await message.reply("User removed from premium.")
    
    try:
        await bot.send_message(user_id, "❌ Your Premium access has been removed.")
    except:
        pass

@Bot.on_message(filters.private & filters.command("all_prem") & filters.user(ADMINS))
async def all_prem_command(bot, message: Message):
    users = await get_premium_users()
    if not users:
        return await message.reply("No premium users found.")
    
    text = "**Premium Users:**\n"
    for user in users:
        text += f"- {user['_id']} (Expires: {user['expiry_date']})\n"
    
    await message.reply(text)

@Bot.on_message(filters.private & filters.command("check_prem"))
async def check_prem_command(bot, message: Message):
    user_id = message.from_user.id
    premium = await is_premium(user_id)
    if premium:
        await message.reply("✅ You are a Premium user!")
    else:
        await message.reply("❌ You are not a Premium user.")
