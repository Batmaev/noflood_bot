from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from .ads import welcome_with_utm, welcome_with_no_flood, show_chats_and_services
from ..utils.db import save_user, save_email, save_code, get_user, authorize, UserStatus
from ..utils.mailing import send_code


router = Router()


authorize_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Авторизоваться 👉👌🏻', callback_data='authorize')]
    ]
)


@router.message(CommandStart())
async def start(message: Message):
    await message.answer('👋')
    await message.answer(
        'Этот бот позволит вам добавиться в общий чат физтехов, даст информацию о том, какие есть '
        'чаты, каналы и сервисы в телеграме на Физтехе.',
        reply_markup=authorize_keyboard
    )
    save_user(message.from_user)



class EmailStatus(StatesGroup):
    WAITING_FOR_EMAIL = State()
    WAITING_FOR_CODE = State()


@router.callback_query(F.data == 'authorize')
async def ask_for_email(update: CallbackQuery | Message, state: FSMContext):
    if isinstance(update, CallbackQuery):
        await update.answer()
        message = update.message
    else:
        message = update

    await message.answer(
        'Давай удостоверимся, что ты из МФТИ. '
        'Hапиши свою почту на домене <code>@phystech.edu</code> '
        'и мы вышлем на неё секретный код. '
        'Отправь сюда код с электронной почты '
        'и ты получишь уникальный доступ к чатикам 😉',
        parse_mode='HTML'
    )
    await state.set_state(EmailStatus.WAITING_FOR_EMAIL)


@router.message(EmailStatus.WAITING_FOR_EMAIL)
async def process_email(message: Message, state: FSMContext):
    if not message.text.endswith('@phystech.edu'):
        await message.answer('Не могу разобрать, что-то на физтеховском. '
                             'Попробуйте ещё раз.')
        return

    save_email(message.from_user, message.text)
    code = send_code(message.text)

    if code is None:
        await message.answer('Не удалось отправить код. Админы уведомлены о проблеме. '
                             'Спустя время, попробуйте ещё раз.')
        return

    save_code(message.from_user, code)

    await message.answer(f'Мы отправили письмо на почту <code>{message.text}</code>. '
                         'Пришлите код сообщением сюда.',
                         parse_mode='HTML')

    await state.set_state(EmailStatus.WAITING_FOR_CODE)


@router.message(EmailStatus.WAITING_FOR_CODE)
async def process_code(message: Message, state: FSMContext):
    bot_user = get_user(message.from_user)

    if bot_user.code != message.text:
        await message.answer('Где-то ошибка, введите ещё раз, пожалуйста.')
        return

    authorize(message.from_user)

    if bot_user.utm_source_id is not None:
        await welcome_with_utm(message, bot_user.utm_source_id)
    else:
        await welcome_with_no_flood(message)

    await state.clear()


@router.message(F.chat.type == 'private')
async def default_message(message: Message, state: FSMContext):
    bot_user = get_user(message.from_user)

    if bot_user is None:
        await start(message)
    elif bot_user.status != UserStatus.AUTHORIZED:
        await ask_for_email(message, state)
    else:
        await show_chats_and_services(message)
