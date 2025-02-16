
from pymongo import MongoClient
import asyncio
import base64
import logging
import os
import random
import re
import string
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from datetime import datetime, timedelta
from bot import Bot
from config import *
from helper_func import subscribed, encode, decode, get_messages, get_shortlink, get_verify_status, update_verify_status, get_exp_time
from database.database import add_user, del_user, full_userbase, present_user, is_premium, add_req, add_req2
from shortzy import Shortzy

client = MongoClient(DB_URI)  # Replace with your MongoDB URI
db = client[DB_NAME]  # Database name
phdlust = db["phdlust"]  # Collection for users
phdlust_tasks = db["phdlust_tasks"] 

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to add a delete task to the database
async def add_delete_task(chat_id, message_id, delete_at):
    phdlust_tasks.insert_one({
        "chat_id": chat_id,
        "message_id": message_id,
        "delete_at": delete_at
    })

# Function to delete the notification after a set delay
async def delete_notification(client, chat_id, notification_id, delay):
    await asyncio.sleep(delay)
    try:
        # Delete the notification message
        await client.delete_messages(chat_id=chat_id, message_ids=notification_id)
    except Exception as e:
        print(f"Error deleting notification {notification_id} in chat {chat_id}: {e}")
        
async def schedule_auto_delete(client, chat_id, message_id, delay):
    delete_at = datetime.now() + timedelta(seconds=int(delay))
    await add_delete_task(chat_id, message_id, delete_at)
    
    # Run deletion in the background to prevent blocking
    async def delete_message():
        await asyncio.sleep(int(delay))
        try:
            # Delete the original message
            await client.delete_messages(chat_id=chat_id, message_ids=message_id)
            phdlust_tasks.delete_one({"chat_id": chat_id, "message_id": message_id})  # Remove from DB
            
            # Send a notification about the deletion
            notification_text = DELETE_INFORM
            notification_msg = await client.send_message(chat_id, notification_text)
            
            # Schedule deletion of the notification after 60 seconds
            asyncio.create_task(delete_notification(client, chat_id, notification_msg.id, 40))
        
        except Exception as e:
            print(f"Error deleting message {message_id} in chat {chat_id}: {e}")

    asyncio.create_task(delete_message())  


async def delete_notification_after_delay(client, chat_id, message_id, delay):
    await asyncio.sleep(delay)
    try:
        # Delete the notification message
        await client.delete_messages(chat_id=chat_id, message_ids=message_id)
    except Exception as e:
        print(f"Error deleting notification {message_id} in chat {chat_id}: {e}")


@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    UBAN = BAN  # Fetch the owner's ID from config
    is_prem = await is_premium(id)
    # Schedule the initial message for deletion after 10 minutes
    #await schedule_auto_delete(client, message.chat.id, message.id, delay=600)

    # Check if the user is the owner
    if id == UBAN:
        sent_message = await message.reply("You are the U-BAN! Additional actions can be added here.")

    else:
        if not await present_user(id):
            try:
                await add_user(id)
            except:
                pass

        verify_status = await get_verify_status(id)
        if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
            await update_verify_status(id, is_verified=False)

        if "verify_" in message.text:
            _, token = message.text.split("_", 1)
            if verify_status['verify_token'] != token:
                return await message.reply("Your token is invalid or Expired. Try again by clicking /start")
            await update_verify_status(id, is_verified=True, verified_time=time.time())
            if verify_status["link"] == "":
                reply_markup = None
            await message.reply(f"Your token successfully verified and valid for: 24 Hour", reply_markup=reply_markup, protect_content=False, quote=True)

        elif len(message.text) > 7 and verify_status['is_verified'] or is_prem:
            try:
                base64_string = message.text.split(" ", 1)[1]
            except:
                return
            _string = await decode(base64_string)
            argument = _string.split("-")
            if len(argument) == 3:
                try:
                    start = int(int(argument[1]) / abs(client.db_channel.id))
                    end = int(int(argument[2]) / abs(client.db_channel.id))
                except:
                    return
                if start <= end:
                    ids = range(start, end+1)
                else:
                    ids = []
                    i = start
                    while True:
                        ids.append(i)
                        i -= 1
                        if i < end:
                            break
            elif len(argument) == 2:
                try:
                    ids = [int(int(argument[1]) / abs(client.db_channel.id))]
                except:
                    return
            temp_msg = await message.reply("Please wait...")
            try:
                messages = await get_messages(client, ids)
            except:
                await message.reply_text("Something went wrong..!")
                return
            await temp_msg.delete()
            
            phdlusts = []
            messages = await get_messages(client, ids)
            for msg in messages:
                if bool(CUSTOM_CAPTION) & bool(msg.document):
                    caption = CUSTOM_CAPTION.format(previouscaption = "" if not msg.caption else msg.caption.html, filename = msg.document.file_name)
                else:
                    caption = "" if not msg.caption else msg.caption.html

                if DISABLE_CHANNEL_BUTTON:
                    reply_markup = msg.reply_markup
                else:
                    reply_markup = None
                
                try:
                    messages = await get_messages(client, ids)
                    phdlust = await msg.copy(chat_id=message.from_user.id, caption=caption, reply_markup=reply_markup , protect_content=PROTECT_CONTENT)
                    phdlusts.append(phdlust)
                    if AUTO_DELETE == True:
                        #await message.reply_text(f"The message will be automatically deleted in {delete_after} seconds.")
                        asyncio.create_task(schedule_auto_delete(client, phdlust.chat.id, phdlust.id, delay=DELETE_AFTER))
                    await asyncio.sleep(0.2)      
                    #asyncio.sleep(0.2)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    phdlust = await msg.copy(chat_id=message.from_user.id, caption=caption, reply_markup=reply_markup , protect_content=PROTECT_CONTENT)
                    phdlusts.append(phdlust)    

            if AUTO_DELETE == True:
                delete_notification = await message.reply(NOTIFICATION)
                asyncio.create_task(delete_notification_after_delay(client, delete_notification.chat.id, delete_notification.id, delay=NOTIFICATION_TIME))
                
        elif is_prem or verify_status['is_verified']:
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("𝗔𝗯𝗼𝘂𝘁 𝗠𝗲", callback_data="about"),
                  InlineKeyboardButton("𝗖𝗹𝗼𝘀𝗲", callback_data="close")]]
            )
            await message.reply_text(
                text=START_MSG.format(
                    first=message.from_user.first_name,
                    last=message.from_user.last_name,
                    username=None if not message.from_user.username else '@' + message.from_user.username,
                    mention=message.from_user.mention,
                    id=message.from_user.id
                ),
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                quote=True
            )

        else:
            verify_status = await get_verify_status(id)
            if IS_VERIFY and not verify_status['is_verified']:
                short_url = f"adrinolinks.in"
                # TUT_VID = f"https://t.me/ultroid_official/18"
                token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                await update_verify_status(id, verify_token=token, link="")
                link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API,f'https://telegram.dog/{client.username}?start=verify_{token}')
                btn = [
                    [InlineKeyboardButton("𝗖𝗹𝗶𝗰𝗸 𝗵𝗲𝗿𝗲", url=link)],
                    [InlineKeyboardButton('𝗛𝗼𝘄 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗲 𝗯𝗼𝘁', url=TUT_VID)]
                ]
                await message.reply(f"𝗔𝘁𝘁𝗲𝗻𝘁𝗶𝗼𝗻!\n𝗬𝗼𝘂𝗿 𝗮𝗰𝗰𝗲𝘀𝘀 𝘁𝗼𝗸𝗲𝗻 𝗵𝗮𝘀 𝗲𝘅𝗽𝗶𝗿𝗲𝗱. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗿𝗲𝗳𝗿𝗲𝘀𝗵 𝘆𝗼𝘂𝗿 𝘁𝗼𝗸𝗲𝗻 𝘁𝗼 𝗰𝗼𝗻𝘁𝗶𝗻𝘂𝗲 𝗲𝗻𝗷𝗼𝘆𝗶𝗻𝗴 𝗼𝘂𝗿 𝘀𝗲𝗿𝘃𝗶𝗰𝗲𝘀.\n𝗧𝗼𝗸𝗲𝗻 𝗧𝗶𝗺𝗲𝗼𝘂𝘁: {get_exp_time(VERIFY_EXPIRE)}\n𝗪𝗵𝗮𝘁 𝗶𝘀 𝘁𝗵𝗶𝘀 𝘁𝗼𝗸𝗲𝗻?\n𝐓𝐡𝐢𝐬 𝐢𝐬 𝐚𝐧 𝐚𝐝𝐬 𝐭𝐨𝐤𝐞𝐧. 𝐁𝐲 𝐰𝐚𝐭𝐜𝐡𝐢𝐧𝐠 𝐚 𝐬𝐢𝐧𝐠𝐥𝐞 𝐚𝐝, 𝐲𝐨𝐮 𝐜𝐚𝐧 𝐠𝐚𝐢𝐧 𝐮𝐧𝐢𝐧𝐭𝐞𝐫𝐫𝐮𝐩𝐭𝐞𝐝 𝐚𝐜𝐜𝐞𝐬𝐬 𝐭𝐨 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐟𝐨𝐫 𝐭𝐡𝐞 𝐧𝐞𝐱𝐭 24 𝐡𝐨𝐮𝐫𝐬.\n𝗥𝗲𝗳𝗿𝗲𝘀𝗵 𝘆𝗼𝘂𝗿 𝘁𝗼𝗸𝗲𝗻 𝗻𝗼𝘄 𝗮𝗻𝗱 𝗰𝗼𝗻𝘁𝗶𝗻𝘂𝗲 𝘆𝗼𝘂𝗿 𝗰𝗶𝗻𝗲𝗺𝗮𝘁𝗶𝗰 𝗷𝗼𝘂𝗿𝗻𝗲𝘆!", reply_markup=InlineKeyboardMarkup(btn), protect_content=False, quote=True)

        
#=====================================================================================##

WAIT_MSG = """"<b>Processing ...</b>"""

REPLY_ERROR = """<code>Use this command as a replay to any telegram message with out any spaces.</code>"""

#=====================================================================================##

    
    
@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    userss = message.from_user.id
    if bool(JOIN_REQUEST_ENABLE):
        invite = await client.create_chat_invite_link(
            chat_id=FORCE_SUB_CHANNEL,
            creates_join_request=True
        )
        ButtonUrl = invite.invite_link
    else:
        ButtonUrl = client.invitelink
    if bool(JOIN_REQUEST_ENABLE):
        invite2 = await client.create_chat_invite_link(
            chat_id=FORCE_SUB_CHANNEL2,
            creates_join_request=True
        )
        await add_req2(userss)
        ButtonUrl2 = invite2.invite_link
    else:
        ButtonUrl2 = client.invitelink2
    buttons = [
        [
            InlineKeyboardButton(
                "⚡𝗝𝗼𝗶𝗻 𝗖𝗵𝗮𝗻𝗻𝗲𝗹1⚡",
                url = ButtonUrl)
            await add_req(userss),
            InlineKeyboardButton(
                "⚡𝗝𝗼𝗶𝗻 𝗖𝗵𝗮𝗻𝗻𝗲𝗹2⚡",
                url = ButtonUrl2,)
            await add_req2(userss)
        ]
    ]
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text = '𝗧𝗿𝘆 𝗔𝗴𝗮𝗶𝗻',
                    url = f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass

    await message.reply(
        text = FORCE_MSG.format(
                first = message.from_user.first_name,
                last = message.from_user.last_name,
                username = None if not message.from_user.username else '@' + message.from_user.username,
                mention = message.from_user.mention,
                id = message.from_user.id
            ),
        reply_markup = InlineKeyboardMarkup(buttons),
        quote = True,
        disable_web_page_preview = True
    )

@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1
        
        status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""
        
        return await pls_wait.edit(status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()
