from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatJoinRequest, ChatMemberUpdated
from bot import Bot

# Store user IDs in a list instead of MongoDB
approved_users = set()
banned_users = set()  # Track banned users

def oprate_user(user_id: int):
    """Add a user if they are not banned and not already in the list."""
    if user_id in banned_users:
        return False  # Do not add banned users
    if user_id not in approved_users:
        approved_users.add(user_id)
        return True  # User added successfully
    return False  # User already exists

def remove_user(user_id: int):
    """Remove a user from the list."""
    approved_users.discard(user_id)

def ban_user(user_id: int):
    """Ban a user and remove them from the approved list."""
    banned_users.add(user_id)
    remove_user(user_id)


@Bot.on_chat_member_updated()
async def handle_chat_members(client, chat_member_updated: ChatMemberUpdated):
    """Handles when users leave or get banned from the chat."""
    user_id = chat_member_updated.old_chat_member.user.id
    if chat_member_updated.old_chat_member.status == ChatMemberStatus.BANNED:
        ban_user(user_id)
    elif chat_member_updated.old_chat_member.status == ChatMemberStatus.LEFT:
        remove_user(user_id)
