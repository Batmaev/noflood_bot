from aiogram import F

DATABASE_FILE = 'db.db'

BOT_TOKEN = '0000000000:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'

SMTP_SERVER = 'smtp.yandex.ru'
SMTP_PORT = 587
EMAIL = 'aaaaaaaaaaa@aaaaaa.aaa'
EMAIL_PASSWORD = 'aaaaaaaaaaaaaaaa'

LOGS_CHAT_ID = -1003333333333

SUPPORT_CALL = '@........'

SUPPORT_IDS = [11111111, 22222222]

SUPPORT_CHAT_ID = -1004444444444

ADMIN_CHAT_ID = -1005555555555

ADMIN_FILTER = \
    F.from_user.id.in_(SUPPORT_IDS) \
    | (F.chat.id == ADMIN_CHAT_ID) \
    | (F.sender_chat.id == SUPPORT_CHAT_ID)

BANNED_IDS = [333333333333]

BANNED_EMAILS = ['evil@phystech.edu']
