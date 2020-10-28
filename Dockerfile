FROM python:3.9.0-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R nobody:nogroup .

USER nobody

CMD [ "python", "./l5r-discord-bot.py" ]