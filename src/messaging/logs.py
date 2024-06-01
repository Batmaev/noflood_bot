import asyncio
import traceback
import html

from aiogram import Bot
from aiogram.types import User, Chat, ErrorEvent

from ..utils.config import BOT_TOKEN, LOGS_CHAT_ID, NOTIFICATIONS_LOGS_CHAT_ID, SUPPORT_CALL

bot = Bot(BOT_TOKEN)


async def error_handler(event: ErrorEvent):
    text = '🚨 #UNCAUGHT_EXCEPTION\n\n'
    text += SUPPORT_CALL + '\n\n'
    text += f'<b>{event.exception}</b>\n\n'
    tb = html.escape(''.join(traceback.format_tb(event.exception.__traceback__)[-1]))
    text += f'<pre><code class="language-python">{tb}</code></pre>\n'
    update = html.escape(event.update.model_dump_json(exclude_defaults=True))[:3000]
    text += f'<pre><code class="language-json">{update}</code></pre>'

    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )
    if event.update.message:
        await event.update.message.reply('Бот сломался) Мы попробуем его починить.')
    if event.update.callback_query:
        await event.update.callback_query.answer('Бот сломался) Мы попробуем его починить.', show_alert=True)

    raise event.exception


def warn(msg: str, notify: bool = False):
    text = '⚠️ #WARNING\n\n'
    if notify:
        text += SUPPORT_CALL + '\n\n'
    text += msg

    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )


def user_html(user: User):
    return f'@{user.username or ""} <a href="tg://user?id={user.id}">{html.escape(user.full_name)}</a> <code>{user.id}</code>'

def chat_link_html(monitored_link):
    return f'<a href="{monitored_link.link}">{html.escape(monitored_link.chat_name)}</a>'


def new_user(user: User, utm_source):
    text = '👤 #new_user\n'
    text += user_html(user)
    if utm_source:
        text += f'\nUTM Source: {chat_link_html(utm_source)}'

    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )

def new_link(monitored_link):
    text = '🔗 #new_link\n'
    text += chat_link_html(monitored_link)
    text += f'\n<code>{monitored_link.chat_id}</code>'
    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )

def new_code(user: User, email: str, code: str):
    text = '💌 #new_code\n'
    text += user_html(user)
    text += f'\nEmail: <code>{email}</code>'
    text += f'\nCode: <code>{code}</code>'
    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )

def finished_authorization(user: User, utm_source):
    text = '✨ #finished_authorization\n'
    text += user_html(user)
    if utm_source:
        text += f'\nUTM Source: {chat_link_html(utm_source)}'
    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )

def chat_join(user: User, monitored_link):
    text = '👁️‍🗨️ #chat_join\n'
    text += user_html(user)
    text += f'\n{chat_link_html(monitored_link)}'
    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )


def bot_kicked(chat: Chat, user: User):
    text = '👢 #bot_kicked\n'
    text += f'from {chat.title} <code>{chat.id}</code>\n'
    text += 'by ' + user_html(user)
    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )

def manual_authorization(user: User, email: str | None):
    text = '🔐 #manual_authorization\n'
    text += user_html(user)
    if email:
        text += f'\n<code>{email}</code>'
    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )

def button_pressed(user: User, button: str):
    text = f'🔘 #button_pressed {button}\n'
    text += user_html(user)
    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )

def malicious_user(user: User, email: str):
    text = '🚷 #malicious_user\n'
    text += user_html(user)
    text += f'\n<code>{email}</code>'
    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )

def email_reuse(user: User, bot_users, email: str):
    text = '🤔 #email_reuse\n'
    text += user_html(user)
    text += f'\n<code>{email}</code>\n\n'
    text += 'User(s) with the same email:\n'
    for bot_user in bot_users:
        text += f'- {user_html(bot_user)} ({bot_user.status.name})\n'
    text += '\n// ' + SUPPORT_CALL
    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )

def ban_user(bot_user):
    text = '🚫 #ban_user\n'
    text += user_html(bot_user)
    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )

def unban_user(bot_user):
    text = '🕊️ #unban_user\n'
    text += user_html(bot_user)
    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )


def sent_notification(bot_user, content: str):
    text = '🪶 #sent_notification\n'
    text += user_html(bot_user)
    text += '\n\n' + content
    asyncio.create_task(
        bot.send_message(NOTIFICATIONS_LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )

def error_notification(bot_user, error: Exception):
    text = '📭 #error_notification\n'
    text += user_html(bot_user)
    text += f'\n{error}'
    asyncio.create_task(
        bot.send_message(NOTIFICATIONS_LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )

def status_checked(user, bot_user, user_id):
    text = '🔍 #status_checked\n'
    text += user_html(user)
    text += '\n\nhas checked status of\n'

    if bot_user is None:
        text += f'<code>{user_id}</code>\n'
        text += 'User not found in DB'
    else:
        text += user_html(bot_user)
        text += f'\n({bot_user.status.name})'

    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )

def strangers_listed(user, monitored_link, n):
    text = '🕵️‍♂️ #strangers_listed\n'
    text += user_html(user)
    text += f'\n\nlisted strangers in {chat_link_html(monitored_link)}'
    text += f'\nresult: {n}'
    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )

def clean_requested(user, monitored_link, n):
    text = '💣 #clean_requested\n'
    text += 'by ' + user_html(user)
    text += f'\nof {chat_link_html(monitored_link)} <code>{monitored_link.chat_id}</code>'
    text += f'\n(up to {n} unauthorized users)'
    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )


def file_received(user, monitored_link, file, n):
    text = '📁 #file_received\n'
    text += 'from ' + user_html(user)
    text += f'\nwith {n} users to delete'
    text += f'\nin {chat_link_html(monitored_link)} <code>{monitored_link.chat_id}</code>'
    text += f'\n\n{file.file_size / 1024:.2f} KB'
    text += f'\n<code>{file.file_id}</code>'
    text += f'\n<code>{file.file_unique_id}</code>'
    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )


def clean_finished(user, monitored_link, banned, not_banned):
    text = '😵 #clean_finished\n'
    text += 'by ' + user_html(user)
    text += f'\nin {chat_link_html(monitored_link)} <code>{monitored_link.chat_id}</code>'
    text += f'\nresult: {len(banned)} banned, {len(not_banned)} not banned'
    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )

def clean_cancelled(user):
    text = '🙄 #clean_cancelled\n'
    text += 'by ' + user_html(user)
    asyncio.create_task(
        bot.send_message(LOGS_CHAT_ID, text, parse_mode='HTML', disable_web_page_preview=True)
    )
