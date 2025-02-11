from bot import Bot
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatMemberUpdated, ChatJoinRequest
from database.request import req_channel_exist, req_sent_user_exist, req_sent_user, del_req_sent_user

# This handler captures membership updates (when a user leaves or is banned)
@Bot.on_chat_member_updated()
async def handle_chat_members(client, chat_member_updated: ChatMemberUpdated):    
    chat_id = chat_member_updated.chat.id

    if await req_channel_exist(chat_id):  # Check if the channel exists in the DB
        old_member = chat_member_updated.old_chat_member

        if not old_member:
            return
    
        if old_member.status == ChatMemberStatus.MEMBER:
            user_id = old_member.user.id

            # Remove user from database if they were tracked before
            if await req_sent_user_exist(chat_id, user_id):
                await del_req_sent_user(chat_id, user_id)

# This handler captures join requests to channels/groups where the bot is an admin
@Bot.on_chat_join_request()
async def handle_join_request(client, chat_join_request: ChatJoinRequest):
    chat_id = chat_join_request.chat.id  

    if await req_channel_exist(chat_id):  # Check if the channel exists in DB
        user_id = chat_join_request.from_user.id 

        # Add user to database only if they haven't been tracked yet
        if not await req_sent_user_exist(chat_id, user_id):
            await req_sent_user(chat_id, user_id)
