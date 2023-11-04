from aiogram import Router, Bot
from aiogram.types import Message, ChatJoinRequest
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

from ..utils.config import BOT_TOKEN
from ..utils.db import UserStatus, MonitoredLink, save_link, get_link, save_user, get_user
from . import logs

router = Router()
bot = Bot(BOT_TOKEN)


@router.message(Command('make_link'))
async def make_link(message: Message):
    try:
        link = await bot.create_chat_invite_link(message.chat.id, creates_join_request=True)
    except TelegramBadRequest as error:
        await message.reply(str(error))
        return

    save_link(link.invite_link, message.chat.title)
    await message.reply(f'Ссылка с подтверждением создана: {link.invite_link}\n\n'
                        'Бот будет автоматически принимать тех, кто подтвердил физтеховскую почту, '
                        'и предлагать авторизоваться остальным.')

@router.chat_join_request()
async def accept_or_decline(request: ChatJoinRequest):
    monitored_link = get_link(request.invite_link.invite_link)
    if monitored_link is None:
        return

    bot_user = get_user(request.from_user)
    if bot_user is None or bot_user.status != UserStatus.AUTHORIZED:
        save_user(request.from_user, monitored_link)
        await request.decline()
        await talk_to_user(request, monitored_link)

    else:
        await request.approve()
        await congrats_user(request, monitored_link)
        logs.chat_join(request.from_user, monitored_link)


async def talk_to_user(request: ChatJoinRequest, monitored_link: MonitoredLink):
    await request.answer_pm(
    f'Привет! Ты попытался вступить в {monitored_link.chat_name}.\n\n'
    'Этот чат доступен только для физтехов. '
    'Авторизуйся в этом боте и попробуй вступить снова.\n\n'
    'Используй команду /start'
)

async def congrats_user(request: ChatJoinRequest, monitored_link: MonitoredLink):
    await request.answer_pm(
    f'Твоя заявка на вступление в {logs.chat_link_html(monitored_link)} принята 🎉',
    parse_mode='HTML',
    disable_web_page_preview=True
)


@router.message(Command('error'))
async def test_error(message: Message):
    raise ValueError('test error')
