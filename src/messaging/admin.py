import re

from aiogram import Router, Bot, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

from ..utils.db import get_all_monitored_chats
from ..utils.config import BOT_TOKEN, SUPPORT_IDS

router = Router()
bot = Bot(BOT_TOKEN)

ADMIN_FILTER = F.from_user.id.in_(SUPPORT_IDS)

def find_userid(message: Message):
    # for entity in message.entities:
    #     if entity.type == 'mention':
    #         return entity.user.id
    ids = re.findall(r'\d{4,}', message.text or message.caption)
    if ids:
        return int(ids[0])


async def chats_of_user_mentioned(message: Message):
    user_id = find_userid(message)
    if user_id is None:
        await message.answer('Не удалось распарсить id пользователя.')
        return

    for chat in get_all_monitored_chats():
        try:
            member = await bot.get_chat_member(chat.chat_id, user_id)
        except TelegramBadRequest:
            continue

        if member.status.value != 'left':
            yield chat, member

@router.message(Command('where'), ADMIN_FILTER)
async def list_user_chats(message: Message):
    text = ''
    async for chat, member in chats_of_user_mentioned(message):
        text += f'{chat.chat_name}: {member.status.value}\n'
    if text:
        await message.answer(text)
    else:
        await message.answer('Пользователя нет ни в одном чате')

@router.message(Command('ban'), ADMIN_FILTER)
async def ban(message: Message):
    text = ''
    async for chat, member in chats_of_user_mentioned(message):
        if member.status.value != 'kicked':
            try:
                await bot.ban_chat_member(chat.chat_id, member.user.id)
                text += f'{chat.chat_name}: забанили\n'
            except TelegramBadRequest:
                text += f'{chat.chat_name}: не хватает прав\n'
    if text:
        await message.answer(text)
    else:
        await message.answer('Пользователя нет ни в одном чате')

@router.message(Command('unban'), ADMIN_FILTER)
async def unban(message: Message):
    text = ''
    async for chat, member in chats_of_user_mentioned(message):
        if member.status.value == 'kicked':
            try:
                await bot.unban_chat_member(chat.chat_id, member.user.id, only_if_banned=True)
                text += f'{chat.chat_name}: разбанили\n'
            except TelegramBadRequest:
                text += f'{chat.chat_name}: не хватает прав\n'
    if text:
        await message.answer(text)
    else:
        await message.answer('Пользователя не забанен ни в одном чате')
