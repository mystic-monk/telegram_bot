FROM python:3.8.6

RUN pip install python-telegram-bot

RUN mkdir /app
ADD . /app
WORKDIR /app

CMD python /app/telegram_bot.py