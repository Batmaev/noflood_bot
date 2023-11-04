FROM python:3.11

WORKDIR /noflood-bot
COPY . .
RUN pip3 install -r requirements.txt
RUN python3 -m src.utils.db
