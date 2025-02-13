from bot import Bot
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatMemberUpdated, ChatJoinRequest
from database.request import req_sent_user_exist, req_sent_user, del_req_sent_user
from config import FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2

# This handler captures membership updates (when a user leaves or is banned)
@Bot.on_chat_member_updated()
async def handle_chat_members(client, chat_member_updated: ChatMemberUpdated):
    chat_id = chat_member_updated.chat.id
    user_id = chat_member_updated.old_chat_member.user.id

    if chat_id in [FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2]:  # ✅ Check both channels
        old_member = chat_member_updated.old_chat_member

        if old_member and old_member.status == ChatMemberStatus.MEMBER:
            # Remove user from database if they were tracked before
            if await req_sent_user_exist(user_id):
                await del_req_sent_user(user_id)

# This handler captures join requests to channels where the bot is an admin
@Bot.on_chat_join_request()
async def handle_join_request(client, chat_join_request: ChatJoinRequest):
    chat_id = chat_join_request.chat.id
    user_id = chat_join_request.from_user.id

    if chat_id in [FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2]:  # ✅ Check both channels
        # Add user to database only if they haven't been tracked yet
        if not await req_sent_user_exist(user_id):
            await req_sent_user(user_id)
