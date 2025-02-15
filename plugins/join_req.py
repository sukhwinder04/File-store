from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatJoinRequest, ChatMemberUpdated
from database.database import remove_req, remove_req2
from bot import Bot

# Store user IDs in a list instead of MongoDB

@Bot.on_chat_member_updated()
async def handle_chat_members(client, chat_member_updated: ChatMemberUpdated):
    """Handles when users leave or get banned from the chat."""
    user_id = chat_member_updated.old_chat_member.user.id  # Use `user` instead of `from_user`
    if chat_member_updated.old_chat_member.status == ChatMemberStatus.BANNED:
        remove_req(user_id)
    elif chat_member_updated.old_chat_member.status == ChatMemberStatus.LEFT:
        remove_req(user_id)
    elif chat_member_updated.old_chat_member.status == ChatMemberStatus.MEMBER:
        remove_req(suer_id)

####################################################################################################################
#############################################################################################################
#####################################################################################################
#############################################################################################



@Bot.on_chat_member_updated()
async def handle_chat_members_2(client, chat_member_updated: ChatMemberUpdated):
    """Handles when users leave or get banned from FORCE_SUB_CHANNEL2."""
    user_id = chat_member_updated.old_chat_member.user.id  # Use `user` instead of `from_user`
    if chat_member_updated.old_chat_member.status == ChatMemberStatus.BANNED:
        remove_req2(user_id)
    elif chat_member_updated.old_chat_member.status == ChatMemberStatus.LEFT:
        remove_req2(user_id)
    elif chat_member_updated.old_chat_member.status == ChatMemberStatus.MEMBER:
        remove_req2(user_id)
