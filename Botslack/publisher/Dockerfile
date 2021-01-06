FROM python:3.6.3

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

ENV PYTHONUNBUFFERED=1

WORKDIR /publisher_bot

COPY ./publisher_bot.py /publisher_bot.py

CMD [ "python", "/publisher_bot.py" ]
