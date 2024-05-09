import re

from aiogram import Router, Bot, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

import telethon
from telethon.errors.rpcerrorlist import UsernameInvalidError

from . import logs
from ..utils import db
from ..utils.config import BOT_TOKEN, ADMIN_FILTER, ADMIN_CHAT_ID, API_ID, API_HASH

router = Router()
bot = Bot(BOT_TOKEN)

client = telethon.TelegramClient('session', API_ID, API_HASH)

class NoUserSpecifiedError(Exception):
    pass


async def find_userid(message: Message) -> int | Exception:
    for entity in message.entities:
        if entity.type == 'mention':
            username = message.text[entity.offset + 1:entity.offset + entity.length]
            try:
                await client.start(bot_token=BOT_TOKEN)
                user_id = await client.get_peer_id(username)
                return user_id
            except UsernameInvalidError as error:
                return error
            finally:
                await client.disconnect()

    ids = re.findall(r'\d{4,}', message.text or message.caption)
    if ids:
        return int(ids[0])

    if message.reply_to_message:
        if message.reply_to_message.forward_from:
            return message.reply_to_message.forward_from.id
        return message.reply_to_message.from_user.id

    return NoUserSpecifiedError()


async def chats_of_user_mentioned(user_id: int):
    for chat in db.get_all_monitored_chats():
        try:
            member = await bot.get_chat_member(chat.chat_id, user_id)
        except (TelegramBadRequest, TelegramForbiddenError):
            continue

        if member.status.value != 'left':
            yield chat, member



@router.message(Command('where'), ADMIN_FILTER | (F.chat.id == ADMIN_CHAT_ID))
async def list_user_chats(message: Message):
    user_id = await find_userid(message)
    if isinstance(user_id, UsernameInvalidError):
        await message.reply('Юзернейм никому не принадлежит')
        return
    if isinstance(user_id, NoUserSpecifiedError):
        await message.reply(
            'Использование:\n'
            '• /where @username\n'
            '• /where 1234567890\n'
            '• или ответом на сообщение пользователя'
        )
        return

    bot_user = db.get_user_by_id(user_id)
    if bot_user is not None:
        text = logs.user_html(bot_user)
        text += f'\nEmail: <code>{bot_user.email}</code>'
        text += f'\nРегистрация: {bot_user.created_at}'
        text += f'\nСтатус в боте: {bot_user.status.name}\n\n'
    else:
        text = f'Пользователь <code>{user_id}</code> не контактировал с ботом\n\n'

    text += 'Статус в чатах:\n'
    async for chat, member in chats_of_user_mentioned(user_id):
        text += f'{chat.chat_name}: {member.status.value}\n'

    await message.answer(text, parse_mode='HTML')

@router.message(Command('ban'), ADMIN_FILTER)
async def ban(message: Message):
    user_id = await find_userid(message)
    if isinstance(user_id, UsernameInvalidError):
        await message.reply('Юзернейм никому не принадлежит')
        return
    if isinstance(user_id, NoUserSpecifiedError):
        await message.reply(
            'Использование:\n'
            '• /ban @username\n'
            '• /ban 1234567890\n'
            '• или ответом на сообщение пользователя'
        )
        return

    db.ban_user(user_id)

    text = ''
    async for chat, member in chats_of_user_mentioned(user_id):
        if member.status.value != 'kicked':
            try:
                await bot.ban_chat_member(chat.chat_id, member.user.id)
                text += f'{chat.chat_name}: забанили\n'
            except TelegramBadRequest:
                text += f'{chat.chat_name}: не хватает прав\n'
    if not text:
        text = 'Пользователя нет ни в одном чате'

    await message.answer(text)


@router.message(Command('unban'), ADMIN_FILTER)
async def unban(message: Message):
    user_id = await find_userid(message)
    if isinstance(user_id, UsernameInvalidError):
        await message.reply('Юзернейм никому не принадлежит')
        return
    if isinstance(user_id, NoUserSpecifiedError):
        await message.reply(
            'Использование:\n'
            '• /unban @username\n'
            '• /unban 1234567890\n'
            '• или ответом на сообщение пользователя'
        )
        return

    db.unban_user(user_id)

    text = ''
    async for chat, member in chats_of_user_mentioned(user_id):
        if member.status.value == 'kicked':
            try:
                await bot.unban_chat_member(chat.chat_id, member.user.id, only_if_banned=True)
                text += f'{chat.chat_name}: разбанили\n'
            except TelegramBadRequest:
                text += f'{chat.chat_name}: не хватает прав\n'
    if text:
        await message.answer(text)
    else:
        await message.answer('Пользователь не был забанен ни в одном чате')


@router.message(Command('is'))
async def check_status(message: Message):
    user_id = await find_userid(message)
    if isinstance(user_id, UsernameInvalidError):
        await message.reply('Юзернейм никому не принадлежит')
        return
    if isinstance(user_id, NoUserSpecifiedError):
        await message.reply(
            'Использование:\n'
            '• /is @username\n'
            '• /is 1234567890\n'
            '• или ответом на сообщение пользователя'
        )
        return

    bot_user = db.get_user_by_id(user_id)

    if bot_user is None:
        await message.reply('Этот пользователь не регистрировался в боте')
        return

    match bot_user.status:
        case db.UserStatus.NOT_AUTHORIZED | db.UserStatus.AUTHORIZING:
            await message.reply('Пользователь начинал регистрацию в боте, но не завершил её')
            return
        case db.UserStatus.AUTHORIZED:
            await message.reply('Пользователь подтвердил свой статус физтеха')
            return
        case db.UserStatus.BANNED:
            await message.reply('Пользователь забанен админами бота')
            return


@router.message(Command('strangers'), F.chat.type == 'private')
async def list_strangers(message: Message):
    admin = await bot.get_chat_member(ADMIN_CHAT_ID, message.from_user.id)
    if admin.status in ('kicked', 'left'):
        await message.reply('Вам недоступна эта команда')
        return

    chat_link = message.text.split()[1]
    monitored_link = db.get_link(chat_link)

    if monitored_link is None:
        await message.reply('Чат не отслеживается')
        return

    text = f'Неавторизованные в {monitored_link.chat_name}:\n'

    await client.start(bot_token=BOT_TOKEN)

    i = 1
    I_MAX = 100
    async for member in client.iter_participants(monitored_link.chat_id):
        if member.bot:
            continue

        if member.username:
            mention_str = f'@{member.username}'
        else:
            if member.last_name:
                full_name = f'{member.first_name} {member.last_name}'
            else:
                full_name = member.first_name
            mention_str = f'<a href="tg://user?id={member.id}">{full_name}</a>'

        mention_str += f' <code>{member.id}</code>'

        bot_user = db.get_user_by_id(member.id)

        if bot_user is None:
            text += f'{i}. {mention_str} STRANGER\n'
        elif bot_user.status == db.UserStatus.AUTHORIZED:
            continue
        elif bot_user.status == db.UserStatus.NOT_AUTHORIZED:
            text += f'{i}. {mention_str} AUTHORIZING\n'
        else:
            text += f'{i}. {mention_str} {bot_user.status.name}\n'

        i += 1

        if i % I_MAX == 0:
            await message.answer(text, parse_mode='HTML', disable_web_page_preview=True)
            text = ''

    if text != '':
        await message.answer(text, parse_mode='HTML', disable_web_page_preview=True)

    await client.disconnect()
