import asyncio
from typing import Literal

from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramAPIError

from .long_texts import NO_FLOOD_RULES, CHATS, SERVICES, BLOGS
from . import logs
from ..utils.db import get_link
from ..utils.config import BOT_TOKEN, NO_FLOOD_CHANNEL_ID, NO_FLOOD_CHAT_ID, GIF_ID


router = Router()
bot = Bot(BOT_TOKEN)





async def welcome_with_utm(message: Message, link_text: str):
    monitored_link = get_link(link_text)
    await message.answer(
        'Проверка прошла успешно! '
        'Теперь ты можешь вступить в чат '
        f'{logs.chat_link_html(monitored_link)}',
        parse_mode='HTML',
    )
    await asyncio.sleep(60)
    await show_chats_and_services(message)


async def welcome_with_no_flood(message: Message, how: Literal['after_auth', 'ad'] = 'after_auth'):
    if how == 'after_auth':
        text = 'Проверка прошла успешно!\n' \
               'Пожалуйста, ознакомься с правилами чата <b>Phystech.No Flood ©</b>:\n'
    else:
        text = 'Правила чата <b>Phystech.No Flood ©</b>:\n'

    text += NO_FLOOD_RULES
    text += 'Нажми кнопку, чтобы подтвердить своё согласие.'

    await message.answer(
        text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Согласен', callback_data='agree')]]
        ),
        disable_web_page_preview=True
    )


@router.callback_query(F.data == 'agree')
async def accept_to_no_flood(query: CallbackQuery):
    link = await bot.create_chat_invite_link(
        NO_FLOOD_CHANNEL_ID,
        member_limit=2,
        name=f'for {query.from_user.id}'
    )
    await query.message.answer_animation(
        GIF_ID,
        caption = 'Добро пожаловать в канал Физтех.Важное.\n'
                  'Обрати внимание на гиф-инструкцию по переходу в <b>Phystech. No Flood ©</b> ☝',
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Физтех.Важное', url=link.invite_link)]]
        )
    )
    await query.message.edit_reply_markup()
    await query.answer()
    logs.no_flood_invite(query.from_user)


    await asyncio.sleep(60)
    await show_chats_and_services(query.message)



async def show_chats_and_services(message: Message):
    await message.answer(
        'Хотите посмотреть, какие есть чаты/сервисы/блоги у физтехов?',
        reply_markup=await chat_and_services_buttons(message.from_user.id)
    )


async def chat_and_services_buttons(user_id: int):

    inline_keyboard=[
            [InlineKeyboardButton(text='Чаты', callback_data='chats')],
            [InlineKeyboardButton(text='Сервисы', callback_data='services')],
            [InlineKeyboardButton(text='Блоги', callback_data='blogs')],
        ]

    is_in_no_flood = await is_in_chat(user_id, NO_FLOOD_CHAT_ID)

    if not is_in_no_flood:
        noflood = [[InlineKeyboardButton(text='Phystech.No Flood', callback_data='no_flood')]]
        inline_keyboard = noflood + inline_keyboard

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)



@router.callback_query(F.data == 'chats')
@router.callback_query(F.data == 'services')
@router.callback_query(F.data == 'blogs')
async def switch_chats_and_services(query: CallbackQuery):
    match query.data:
        case 'chats':
            text = CHATS
        case 'services':
            text = SERVICES
        case 'blogs':
            text = BLOGS

    buttons = await chat_and_services_buttons(query.from_user.id)

    try:
        await query.message.delete()
    except TelegramAPIError:
        pass

    await query.message.answer(text, reply_markup=buttons, parse_mode='HTML',
                               disable_web_page_preview=True)
    await query.answer()
    logs.button_pressed(query.from_user, query.data)



@router.callback_query(F.data == 'no_flood')
async def show_no_flood_rules(query: CallbackQuery):
    await welcome_with_no_flood(query.message, how='ad')
    await query.answer()
    logs.button_pressed(query.from_user, query.data)


async def is_in_chat(user_id: int, chat_id: int):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator', 'member']
    except TelegramAPIError:
        return False
