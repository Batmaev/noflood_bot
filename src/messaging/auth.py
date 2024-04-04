from aiogram import Router, F
from aiogram.types import Message, Chat, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ChatMemberUpdated
from aiogram.filters import CommandStart, Command, ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from .ads import welcome, ad_after_auth
from ..utils import db
from ..utils.config import SUPPORT_CHAT_ID, ADMIN_FILTER
from ..utils.mailing import send_code
from . import logs
from .long_texts import ASK_FOR_EMAIL


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
    db.save_user(message.from_user)
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
    db.save_email(message.from_user, email)

    if '+' in email:
        await message.answer('Почта не должна содержать символ "+"')
        return

    if not email.endswith('@phystech.edu'):
        await message.answer('Не могу разобрать, что-то на физтеховском. '
                             'Попробуйте ещё раз.')
        return

    existing_users = db.get_users_with_email(email)
    if len(existing_users) > 1 or (len(existing_users) == 1 and
                                   existing_users[0].id != message.from_user.id):
        logs.email_reuse(message.from_user, existing_users, email)

    if any(user.status == db.UserStatus.BANNED for user in existing_users):
        await message.answer('Извините, но вы не можете авторизоваться.')
        logs.malicious_user(message.from_user, email)

        bot_user = db.get_user(message.from_user)
        if bot_user.status != db.UserStatus.BANNED:
            db.ban_user(message.from_user.id)
        return

    code = send_code(email)

    if code is None:
        await message.answer('Не удалось отправить код. Админы уведомлены о проблеме. '
                             'Спустя время, попробуйте ещё раз.')
        return

    db.save_code(message.from_user, code)

    await message.answer(f'Мы отправили письмо на почту <code>{message.text}</code>. '
                         'Пришлите код сообщением сюда.\n\n'
                         'Если письмо не приходит, то, скорее всего, в почте опечатка. '
                         'Тогда нажмите на кнопку "Авторизоваться" ещё раз.',
                         parse_mode='HTML')

    await state.set_state(EmailStatus.WAITING_FOR_CODE)


@router.message(EmailStatus.WAITING_FOR_CODE, F.chat.type == 'private')
async def process_code(message: Message, state: FSMContext):
    bot_user = db.get_user(message.from_user)

    if bot_user.code != message.text:
        await message.answer('Где-то ошибка, введите ещё раз, пожалуйста.')
        return

    await finalize_registration(bot_user, message)
    await state.clear()


async def finalize_registration(bot_user: db.BotUser, message: Message):
    db.authorize(message.from_user)
    await welcome(message, bot_user.utm_source_id)


@router.chat_member(F.chat.id == SUPPORT_CHAT_ID, ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def suggest_support(update: ChatMemberUpdated):
    mention = update.new_chat_member.user.mention_html()
    await update.answer(
        f'Привет, {mention}!\n\n'
        'Чаще всего в этот чат попадают люди, у которых нет физтеховской почты. '
        'Если это твой случай, то то пришли, пожалуйста:\n'
        '• актуальную почту\n'
        '• подтверждение, что ты физтех (например, диплом)',
        parse_mode='HTML'
    )


@router.message(Command('auth'), ADMIN_FILTER)
async def manual_auth(message: Message):

    if message.reply_to_message is None:
        await message.answer('Ответьте этой командой на сообщение пользователя, '
                             'которого нужно авторизовать.')
        return

    bot_user = db.get_user(message.reply_to_message.from_user)
    if bot_user is None:
        await message.answer('Пусть пользователь сначала напишет боту /start')
        return

    email = get_email(message.reply_to_message)
    db.save_email(message.reply_to_message.from_user, email)

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
    bot_user = db.get_user(message.from_user)

    if bot_user is None:
        await start(message, state)
    elif bot_user.status != db.UserStatus.AUTHORIZED:
        await ask_for_email(message, state)
    else:
        await ad_after_auth(message)
