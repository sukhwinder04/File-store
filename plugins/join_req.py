from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatJoinRequest, ChatMemberUpdated
from database.database import remove_req, remove_req2, add_req, add_req2
from config import FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2
from bot import Bot

@Bot.on_chat_member_updated()
async def handle_chat_members(client, chat_member_updated: ChatMemberUpdated):
    """Handles when users leave or get banned from the chat."""
    if chat_member_updated.old_chat_member:  # Ensure old_chat_member is not None
        user_id = chat_member_updated.old_chat_member.user.id
        if chat_member_updated.old_chat_member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.LEFT, ChatMemberStatus.MEMBER]:
            await remove_req(user_id)

@Bot.on_chat_join_request(filters.chat(Config.CHANNEL_ONE) | filters.chat(Config.CHANNEL_TWO))
async def join_reqs(client, join_req: ChatJoinRequest):
    user_id = join_req.from_user.id
    if join_req.chat.id == FORCE_SUB_CHANNEL:
        try:
            await add_req(user_id)
        except Exception as e:
            print(f"Error adding join request to req_one: {e}")
    elif join_req.chat.id == FORCE_SUB_CHANNEL2:
        try:
            await add_req2(user_id)
        except Exception as e:
            print(f"Error adding join request to req_two: {e}")


@Bot.on_chat_member_updated()
async def handle_chat_members_2(client, chat_member_updated: ChatMemberUpdated):
    """Handles when users leave or get banned from FORCE_SUB_CHANNEL2."""
    if chat_member_updated.old_chat_member:  # Ensure old_chat_member is not None
        user_id = chat_member_updated.old_chat_member.user.id
        if chat_member_updated.old_chat_member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.LEFT, ChatMemberStatus.MEMBER]:
           await remove_req2(user_id)
