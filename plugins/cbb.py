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
            text = f"<b>╭━━━━━━━━━━━━━━━➣\n┣⪼ 𝙾𝚠𝚗𝚎𝚛 : <a href='tg://user?id={OWNER_ID}'>𝑽𝒊𝒔𝒉𝒂𝒍</a>\n┣⪼ 𝙾𝚝𝚝 𝙲𝚑𝚊𝚗𝚗𝚎𝚕 : <a href='https://t.me/OttSandhu'>𝙊𝙩𝙩 𝙎𝙖𝙣𝙙𝙝𝙪</a>\n┣⪼ 𝙾𝚝𝚝 𝙶𝚛𝚘𝚞𝚙 : <a href='https://t.me/+_-9trQQYYFczNTJl'>𝙊𝙩𝙩 𝙂𝙧𝙤𝙪𝙥</a>\n┣⪼ 𝙼𝚘𝚟𝚒𝚎𝚜 𝙲𝚑𝚊𝚗𝚗𝚎𝚕 : <a href='https://t.me/+MbS71p0fCIRhMTA1'>𝙋𝙪𝙣𝙟𝙖𝙗𝙞 𝙈𝙤𝙫𝙞𝙚</a>\n╰───────────────⍟</b>",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("𝗖𝗹𝗼𝘀𝗲", callback_data = "close")
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
