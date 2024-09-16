# Telegram-бот для физтех-only чатов

[@phystech_bot](https://t.me/phystech_bot) — это бот для физтех-only чатов в Телеграме. Он создаёт защищённые ссылки-приглашения. Чтобы присоединиться по такой ссылке, нужно подтвердить физтеховскую почту.

Бот не зависит от администрации МФТИ.

Подробнее: https://telegra.ph/phystech-bot-04-19


## Использованные технологии

Python, Docker, SQLite, SQLAlchemy, asyncio, aiogram, telethon, SMTPlib, pandas


## Как запустить

1. Переименуйте `config.template.py` в `config.py`; `long_texts.template.py` в `long_texts.py`. Эти файлы расположены в `src/utils` и `src/messaging`. Заполните их. Понадобится токен бота, ID служебных чатов и данные почты для рассылок.

2. Если сохранилась база данных `db.db`, то добавьте её в корневую папку.

3. `docker compose up -d`