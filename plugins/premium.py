from pyrogram import filters
from pyrogram.types import Message
from bot import Bot
from config import ADMINS
from database.database import add_premium_user, remove_premium_user, get_premium_users

@Bot.on_message(filters.private & filters.command('prem') & filters.user(ADMINS))
async def add_premium(bot, message: Message):
    args = message.text.split()
    
    if len(args) != 3:
        return await message.reply_text("Usage: /prem {user_id} {time}\nExample: /prem 123456 1m")

    try:
        user_id = int(args[1])
        duration = args[2]

        if await add_premium_user(user_id, duration):
            await message.reply_text(f"✅ User {user_id} has been added to premium for {duration}.")
            
            # Notify the user
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=f"🎉 **Congratulations!**\n\nYou have been added to **Premium** for `{duration}`.\n\nEnjoy your premium benefits! 🚀"
                )
            except Exception as e:
                await message.reply_text(f"⚠️ Could not notify the user. Error: {e}")
        else:
            await message.reply_text("❌ Invalid time format. Use min, d, w, or m.")
    except ValueError:
        await message.reply_text("❌ Invalid user ID.")

@Bot.on_message(filters.private & filters.command('remove_prem') & filters.user(ADMINS))
async def remove_premium(bot, message: Message):
    args = message.text.split()
    
    if len(args) != 2:
        return await message.reply_text("Usage: /remove_prem {user_id}")

    try:
        user_id = int(args[1])
        await remove_premium_user(user_id)
        await message.reply_text(f"❌ User {user_id} has been removed from premium.")

        # Notify the user
        try:
            await bot.send_message(
                chat_id=user_id,
                text="⚠️ **Your Premium Membership Has Expired**\n\nYour premium access has been removed. Contact an admin if you want to renew it."
            )
        except Exception as e:
            await message.reply_text(f"⚠️ Could not notify the user. Error: {e}")

    except ValueError:
        await message.reply_text("❌ Invalid user ID.")

@Bot.on_message(filters.private & filters.command('prem_users') & filters.user(ADMINS))
async def list_premium_users(bot, message: Message):
    users = await get_premium_users()

    if not users:
        return await message.reply_text("🚫 No premium users found.")

    text = "👑 **Premium Users:**\n\n"
    for user in users:
        text += f"👤 **User ID:** `{user['_id']}`\n⏳ **Expires:** {user['expiry_date']}\n\n"

    await message.reply_text(text)
