FROM python:3.6.3

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

ENV PYTHONUNBUFFERED=1

WORKDIR /consumer_bot

COPY ./consumer_bot.py /consumer_bot.py

CMD [ "python", "/consumer_bot.py" ]
