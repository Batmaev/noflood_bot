import asyncio

from aiogram import Bot, Dispatcher

from .utils.config import BOT_TOKEN
from .messaging import entry, auth, ads, admin
from .messaging.logs import error_handler

bot = Bot(BOT_TOKEN)
dispatcher = Dispatcher()
dispatcher.include_routers(admin.router, entry.router, ads.router, auth.router)
dispatcher.error()(error_handler)


if __name__ == '__main__':
    asyncio.run(dispatcher.start_polling(bot))
