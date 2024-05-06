import asyncio

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

import telethon

from . import logs
from ..utils import db, db_addons
from ..utils.config import BOT_TOKEN, API_ID, API_HASH

bot = Bot(BOT_TOKEN)

client = telethon.TelegramClient('session', API_ID, API_HASH)

async def notify_users_of(chat_id: int, text: str, limit: int = 100):
    await client.start(bot_token=BOT_TOKEN)

    i = 0
    async for member in client.iter_participants(chat_id):
        if i >= limit:
            break

        if member.bot:
            continue

        bot_user = db.get_user_by_id(member.id)
        if bot_user is None:
            continue

        if bot_user.status == db.UserStatus.AUTHORIZED or bot_user.status == db.UserStatus.BANNED:
            continue

        notified_user = db_addons.get_notified_user(bot_user.id)
        if notified_user is not None:
            continue

        if db_addons.was_error_with(bot_user):
            continue

        try:
            await bot.send_message(bot_user.id, text, parse_mode='HTML')
            db_addons.save_notification(bot_user)
            logs.sent_notification(bot_user, text)
            i += 1

        except (TelegramBadRequest, TelegramForbiddenError) as error:
            db_addons.save_notification_error(bot_user, str(error))
            logs.error_notification(bot_user, error)

        await asyncio.sleep(3.1)

    await client.disconnect()




async def make_threatening_post_at(chat_id: int, text: str, starter = '\n', joiner = '.', ender = ''):
    await client.start(bot_token=BOT_TOKEN)
    members = await client.get_participants(chat_id)

    not_authorized = []
    for member in members:
        if member.bot:
            continue

        bot_user = db.get_user_by_id(member.id)

        if bot_user is not None and (
            bot_user.status == db.UserStatus.AUTHORIZED or bot_user.status == db.UserStatus.BANNED
        ):
            continue

        not_authorized.append(member)

    print(len(not_authorized))

    notification_string = starter + ''.join([f'<a href="tg://user?id={user.id}">{joiner}</a>' for user in not_authorized]) + ender
    await bot.send_message(chat_id, text + notification_string, parse_mode='HTML', disable_web_page_preview=True)

    await client.disconnect()