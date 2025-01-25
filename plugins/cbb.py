#(©)Codexbotz

from pyrogram import __version__
from bot import Bot
from config import OWNER_ID
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":
        await query.message.edit_text(
            text = f"<b>╭━━━━━━━━━━━━━━━➣\n┣⪼ 𝙾𝚠𝚗𝚎𝚛 : <a href='tg://user?id={OWNER_ID}'>𝓢𝓐𝓝𝓓𝓗𝓤</a>\n┣⪼ 𝙾𝚝𝚝 𝙲𝚑𝚊𝚗𝚗𝚎𝚕 : <a href='https://t.me/OttSandhu'>𝓞𝓽𝓽 𝓢𝓪𝓷𝓭𝓱𝓾</a>\n┣⪼ 𝙾𝚝𝚝 𝙶𝚛𝚘𝚞𝚙 :<a href='https://t.me/+_-9trQQYYFczNTJl'>𝓞𝓽𝓽 𝓖𝓻𝓸𝓾𝓹</a>\n┣⪼ 𝙼𝚘𝚟𝚒𝚎𝚜 𝙲𝚑𝚊𝚗𝚗𝚎𝚕 :<a href='https://t.me/+MbS71p0fCIRhMTA1'>𝓟𝓾𝓷𝓳𝓪𝓫𝓲 𝓜𝓸𝓿𝓲𝓮</a>\n╰───────────────⍟</b>",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔒 Close", callback_data = "close")
                    ]
                ]
            )
        )
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
