import re

from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

from . import logs
from ..utils import db
from ..utils.config import BOT_TOKEN, ADMIN_FILTER

router = Router()
bot = Bot(BOT_TOKEN)

async def find_userid(message: Message):
    # for entity in message.entities:
    #     if entity.type == 'mention':
    #         return entity.user.id
    ids = re.findall(r'\d{4,}', message.text or message.caption)
    if ids:
        return int(ids[0])
    await message.answer('Не удалось распарсить id пользователя.')


async def chats_of_user_mentioned(user_id: int):
    for chat in db.get_all_monitored_chats():
        try:
            member = await bot.get_chat_member(chat.chat_id, user_id)
        except TelegramBadRequest:
            continue

        if member.status.value != 'left':
            yield chat, member


@router.message(Command('where'), ADMIN_FILTER)
async def list_user_chats(message: Message):
    user_id = await find_userid(message)
    if user_id is None:
        return

    bot_user = db.get_user_by_id(user_id)
    if bot_user is not None:
        text = logs.user_html(bot_user)
        text += f'\nEmail: <code>{bot_user.email}</code>'
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
    if user_id is None:
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
    if user_id is None:
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
