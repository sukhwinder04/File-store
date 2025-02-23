from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from bot import Bot
from config import ADMINS
from database.database import add_premium_user, remove_premium_user, get_premium_users, is_premium

@Bot.on_message(filters.private & filters.command("prem") & filters.user(ADMINS))
async def add_premium_command(bot, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /add_prem user_id")
    
    user_id = int(message.command[1])
    
    buttons = [[
        InlineKeyboardButton("1 Min", callback_data=f"prem_1min_{user_id}"),
        InlineKeyboardButton("1 Day", callback_data=f"prem_1day_{user_id}"),
        InlineKeyboardButton("1 Month", callback_data=f"prem_1month_{user_id}")
    ]]
    
    await message.reply(
        "Select the premium duration:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Bot.on_callback_query(filters.regex(r"prem_(.*)_(\d+)"))
async def premium_callback(bot, query):
    duration, user_id = query.data.split("_")[1:]
    
    if duration == "1min":
        time = "1min"
    elif duration == "1day":
        time = "1d"
    elif duration == "1month":
        time = "1m"
    else:
        return await query.answer("Invalid selection!", show_alert=True)
    
    success = await add_premium_user(int(user_id), time)
    if success:
        await query.message.edit("User successfully added to premium!")
        try:
            await bot.send_message(int(user_id), "🎉 You have been added to Premium! Enjoy your benefits!")
        except:
            pass
    else:
        await query.answer("Failed to add user to premium!", show_alert=True)

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
