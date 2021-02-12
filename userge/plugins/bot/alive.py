"""Fun plugin"""

import asyncio
from re import search

from pyrogram import filters
from pyrogram.errors import BadRequest, Forbidden
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from userge import Config, Message, get_version, userge, versions
from userge.core.ext import RawClient
from userge.utils import get_file_id, rand_array

CACHED_MEDIA = None


@userge.on_cmd("alive", about={"header": "Just For Fun"}, allow_channels=False)
async def alive_inline(message: Message):
    global CACHED_MEDIA
    if message.client.is_bot:
        if Config.ALIVE_MEDIA:
            url_ = Config.ALIVE_MEDIA.strip()
            if url_.lower() == "false":
                await userge.bot.send_message(
                    message.chat.id,
                    Bot_Alive.alive_info(),
                    reply_markup=Bot_Alive.alive_buttons(),
                    disable_web_page_preview=True,
                )
            else:
                type_, media_ = await Bot_Alive.check_media_link(Config.ALIVE_MEDIA)
                if type_ == "url_gif":
                    await userge.bot.send_animation(
                        message.chat.id,
                        animation=url_,
                        caption=Bot_Alive.alive_info(),
                        reply_markup=Bot_Alive.alive_buttons(),
                    )
                elif type_ == "url_image":
                    await userge.bot.send_photo(
                        message.chat.id,
                        photo=url_,
                        caption=Bot_Alive.alive_info(),
                        reply_markup=Bot_Alive.alive_buttons(),
                    )
                elif type_ == "tg_media" and isinstance(media_, list):
                    if not CACHED_MEDIA:
                        try:
                            CACHED_MEDIA = get_file_id(
                                await userge.bot.get_messages(media_[0], media_[1])
                            )
                        except Exception as er:
                            await message.err(er, del_in=7)
                            return
                    await userge.bot.send_cached_media(
                        message.chat.id,
                        file_id=CACHED_MEDIA,
                        caption=Bot_Alive.alive_info(),
                        reply_markup=Bot_Alive.alive_buttons(),
                    )
        else:
            await userge.bot.send_photo(
                message.chat.id,
                photo=Bot_Alive.alive_default_imgs(),
                caption=Bot_Alive.alive_info(),
                reply_markup=Bot_Alive.alive_buttons(),
            )
    else:
        bot = await userge.bot.get_me()
        try:
            x = await userge.get_inline_bot_results(bot.username, "alive")
            y = await userge.send_inline_bot_result(
                chat_id=message.chat.id, query_id=x.query_id, result_id=x.results[0].id
            )
        except (Forbidden, BadRequest) as ex:
            return await message.err(str(ex), del_in=5)
        await message.delete()
        await asyncio.sleep(120)
        await userge.delete_messages(message.chat.id, y.updates[0].id)


if userge.has_bot:

    @userge.bot.on_callback_query(filters.regex(pattern=r"^settings_btn$"))
    async def alive_cb(_, callback_query: CallbackQuery):
        alive_s = f"𝗨𝗣𝗧𝗜𝗠𝗘 :  {userge.uptime}\n"
        alive_s += "➕ 𝗘𝘅𝘁𝗿𝗮 𝗣𝗹𝘂𝗴𝗶𝗻𝘀 : {}\n".format(
            _parse_arg(Config.LOAD_UNOFFICIAL_PLUGINS)
        )
        alive_s += f"👥 𝗦𝘂𝗱𝗼 : {_parse_arg(Config.SUDO_ENABLED)}\n"
        alive_s += f"🚨 𝗔𝗻𝘁𝗶𝘀𝗽𝗮𝗺 : {_parse_arg(Config.ANTISPAM_SENTRY)}\n"
        if Config.HEROKU_APP and Config.RUN_DYNO_SAVER:
            alive_s += f"⛽️ 𝗗𝘆𝗻𝗼 𝗦𝗮𝘃𝗲𝗿 :  𝙴𝚗𝚊𝚋𝚕𝚎𝚍\n"
        alive_s += f"💬 𝗕𝗼𝘁 𝗙𝗼𝗿𝘄𝗮𝗿𝗱𝘀 : {_parse_arg(Config.BOT_FORWARDS)}\n"
        alive_s += f"📝 𝗣𝗠 𝗟𝗼𝗴𝗴𝗲𝗿 : {_parse_arg(Config.PM_LOGGING)}"
        await callback_query.answer(alive_s, show_alert=True)


def _parse_arg(arg: bool) -> str:
    return "𝙴𝚗𝚊𝚋𝚕𝚎𝚍" if arg else "𝙳𝚒𝚜𝚊𝚋𝚕𝚎𝚍"


class Bot_Alive:
    @staticmethod
    async def check_media_link(media_link: str):
        alive_regex_ = r"http[s]?://(i\.imgur\.com|telegra\.ph/file|t\.me)/(\w+)(?:\.|/)(gif|jpg|png|jpeg|[0-9]+)(?:/([0-9]+))?"
        match = search(alive_regex_, media_link)
        if not match:
            return None, None
        if match.group(1) == "i.imgur.com":
            link = match.group(0)
            link_type = "url_gif" if match.group(3) == "gif" else "url_image"
        elif match.group(1) == "telegra.ph/file":
            link = match.group(0)
            link_type = "url_image"
        else:
            link_type = "tg_media"
            if match.group(2) == "c":
                chat_id = int("-100" + str(match.group(3)))
                message_id = match.group(4)
            else:
                chat_id = match.group(2)
                message_id = match.group(3)
            link = [chat_id, int(message_id)]
        return link_type, link

    @staticmethod
    def alive_info():
        alive_info = f"""
<b>[Paimon](tg://openmessage?user_id=1486647366) is Up and Running...

  🐍 Python</b> :           <code>v{versions.__python_version__}</code>
  🔥 <b>Pyrogram</b> :      <code>v{versions.__pyro_version__}-X-158</code>
  🧬 Bot Version :   <code>v0.4.0-ROGUE-LOGAN.5</code> 
  🦋 Maintainer :    [Alícia Dark](tg://openmessage?user_id=1360435532)
  ✨ <b>Bot Mode  :     {Bot_Alive._get_mode()}</b>   |   {userge.uptime}
"""
        return alive_info

    @staticmethod
    def _get_mode() -> str:
        if RawClient.DUAL_MODE:
            return "DUAL"
        if Config.BOT_TOKEN:
            return "BOT"
        return "USER"

    @staticmethod
    def alive_buttons():
        buttons = [
            [
                InlineKeyboardButton("SETTINGS", callback_data="settings_btn"),
                InlineKeyboardButton(text="REPO", url=Config.UPSTREAM_REPO),
            ]
        ]
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def alive_default_imgs():
        alive_imgs = [
            "https://telegra.ph/file/6f8aa08193c4a26d32c8f.jpg",
            "https://telegra.ph/file/f31cf4721636102bba528.jpg",
            "https://telegra.ph/file/7b93eb9f3a71d4a009961.jpg",
            "https://telegra.ph/file/59aefb8f199af9e4ce214.jpg",
            "https://telegra.ph/file/e7b569283c9484c280242.jpg",
            "https://telegra.ph/file/fccccf1269bd28a22dd24.jpg",
            "https://telegra.ph/file/ea4adcad104ec3421f9cc.jpg",
            "https://telegra.ph/file/377e047a87f9fd7e8b4fc.jpg",
            "https://telegra.ph/file/6f63195d08df591bc4388.jpg",
            "https://telegra.ph/file/87911231dfc1137c145ef.jpg",
            "https://telegra.ph/file/0cdff991a8c31dc6eb5e2.jpg",
            "https://telegra.ph/file/43c24db2b9f7211cdc559.jpg",
            "https://telegra.ph/file/df2e8a2c5532df9db458d.jpg",
            "https://telegra.ph/file/c46511ea3f56d287e8c82.jpg",
            "https://telegra.ph/file/f93b692f0ff3719abe497.jpg",
            "https://telegra.ph/file/c13c205edd80e06abf440.jpg",
            "https://telegra.ph/file/5536eee05b34240538491.jpg",
            "https://telegra.ph/file/9e2f4efa63ffede41528a.jpg",
            "https://telegra.ph/file/92da4c48a812dff03d338.jpg",
            "https://telegra.ph/file/92da4c48a812dff03d338.jpg",
            "https://telegra.ph/file/24062dabe6904a3be2c6f.jpg",
            "https://telegra.ph/file/ad0489b333dfff59c7d90.jpg",
            "https://telegra.ph/file/226c91584f99d2850d4c5.jpg",
            "https://telegra.ph/file/e1bcdeaa8b65f93a2b2c7.jpg",
            "https://telegra.ph/file/05bec6e7375a8a4eb33f9.jpg",
            "https://telegra.ph/file/4443de8b0fcfd6dccd65e.jpg",
            "https://telegra.ph/file/26252450e097240040285.jpg",
            "https://telegra.ph/file/03ec8ed814ee02625b896.jpg",
            "https://telegra.ph/file/9a3f71393836a752c6b41.jpg",
            "https://telegra.ph/file/a480d0a9f97a4e8891688.jpg",
            "https://telegra.ph/file/75990831f9befadf43862.jpg",
            "https://telegra.ph/file/f4e9726bc287f3a746c90.jpg"
        ]
        return rand_array(alive_imgs)
