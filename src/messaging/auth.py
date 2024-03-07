from aiogram import Router, F
from aiogram.types import Message, Chat, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from .ads import welcome, ad_after_auth
from ..utils.db import save_user, save_email, get_users_with_email, save_code, get_user, authorize, UserStatus, BotUser
from ..utils.config import SUPPORT_IDS, SUPPORT_CHAT_ID, BANNED_IDS, BANNED_EMAILS
from ..utils.mailing import send_code
from . import logs
from .long_texts import ASK_FOR_EMAIL, EMAIL_ALREADY_USED


router = Router()


authorize_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Авторизоваться 👉👌🏻', callback_data='authorize')]
    ]
)


@router.message(CommandStart(), F.chat.type == 'private')
async def start(message: Message, state: FSMContext):
    await message.answer('👋')
    await message.answer(
        'Этот бот позволит вам добавиться в общие чаты физтехов, даст информацию о том, какие есть '
        'чаты, каналы и сервисы в телеграме на Физтехе.',
        reply_markup=authorize_keyboard
    )
    save_user(message.from_user)
    await state.clear()



class EmailStatus(StatesGroup):
    WAITING_FOR_EMAIL = State()
    WAITING_FOR_CODE = State()


@router.callback_query(F.data == 'authorize', F.message.chat.type == 'private')
async def ask_for_email(update: CallbackQuery | Message, state: FSMContext):
    if isinstance(update, CallbackQuery):
        await update.answer()
        message = update.message
    else:
        message = update

    await message.answer(ASK_FOR_EMAIL, parse_mode='HTML', disable_web_page_preview=True)
    await state.set_state(EmailStatus.WAITING_FOR_EMAIL)


@router.message(EmailStatus.WAITING_FOR_EMAIL, F.chat.type == 'private')
async def process_email(message: Message, state: FSMContext):
    email = message.text.strip().lower()

    if '+' in email:
        await message.answer('Почта не должна содержать символ "+"')
        return

    if not email.endswith('@phystech.edu'):
        await message.answer('Не могу разобрать, что-то на физтеховском. '
                             'Попробуйте ещё раз.')
        return

    existing_users = get_users_with_email(email)
    if len(existing_users) > 1 or (len(existing_users) == 1 and
                                   existing_users[0].id != message.from_user.id):
        logs.email_reuse(message.from_user, existing_users, email)
        await message.answer(EMAIL_ALREADY_USED, parse_mode='HTML', disable_web_page_preview=True)
        return

    if message.from_user.id in BANNED_IDS or email in BANNED_EMAILS:
        await message.answer('Извините, но вы не можете авторизоваться.')
        logs.malicious_user(message.from_user, email)
        return

    save_email(message.from_user, email)
    code = send_code(email)

    if code is None:
        await message.answer('Не удалось отправить код. Админы уведомлены о проблеме. '
                             'Спустя время, попробуйте ещё раз.')
        return

    save_code(message.from_user, code)

    await message.answer(f'Мы отправили письмо на почту <code>{message.text}</code>. '
                         'Пришлите код сообщением сюда.\n\n'
                         'Если письмо не приходит, то, скорее всего, в почте опечатка. '
                         'Тогда нажмите на кнопку "Авторизоваться" ещё раз.',
                         parse_mode='HTML')

    await state.set_state(EmailStatus.WAITING_FOR_CODE)


@router.message(EmailStatus.WAITING_FOR_CODE, F.chat.type == 'private')
async def process_code(message: Message, state: FSMContext):
    bot_user = get_user(message.from_user)

    if bot_user.code != message.text:
        await message.answer('Где-то ошибка, введите ещё раз, пожалуйста.')
        return

    await finalize_registration(bot_user, message)
    await state.clear()


async def finalize_registration(bot_user: BotUser, message: Message):
    authorize(message.from_user)
    await welcome(message, bot_user.utm_source_id)


@router.message(Command('auth'))
async def manual_auth(message: Message):
    is_support_user = message.from_user.id in SUPPORT_IDS
    is_support_chat = message.sender_chat is not None and message.sender_chat.id == SUPPORT_CHAT_ID

    if not (is_support_user or is_support_chat):
        await message.answer('Недостаточно прав.')
        return

    if message.reply_to_message is None:
        await message.answer('Ответьте этой командой на сообщение пользователя, '
                             'которого нужно авторизовать.')
        return

    bot_user = get_user(message.reply_to_message.from_user)
    if bot_user is None:
        await message.answer('Пусть пользователь сначала напишет боту /start')
        return

    email = get_email(message.reply_to_message)

    mock_message = message.reply_to_message.model_copy(
        update = {
            'chat': Chat(id=message.reply_to_message.from_user.id, type='private'),
        }
    )

    await finalize_registration(bot_user, mock_message)
    await message.answer('Авторизовали.')
    logs.manual_authorization(mock_message.from_user, email)

def get_email(message: Message):
    if message.entities is not None:
        for entity in message.entities:
            if entity.type == 'email':
                return message.text[entity.offset:entity.offset + entity.length]
    if message.caption_entities is not None:
        for entity in message.caption_entities:
            if entity.type == 'email':
                return message.caption[entity.offset:entity.offset + entity.length]
    return None


@router.message(F.chat.type == 'private')
async def default_message(message: Message, state: FSMContext):
    bot_user = get_user(message.from_user)

    if bot_user is None:
        await start(message, state)
    elif bot_user.status != UserStatus.AUTHORIZED:
        await ask_for_email(message, state)
    else:
        await ad_after_auth(message)
