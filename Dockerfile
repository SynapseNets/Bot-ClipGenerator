FROM python:3.12-alpine

COPY requirements.txt .
RUN apk update
RUN apk add --no-cache ffmpeg pkgconfig
RUN pip install --no-cache-dir -r requirements.txt

COPY . /bot
WORKDIR /bot
RUN mkdir -p temp
RUN mkdir -p videos
RUN mkdir -p music

CMD ["python", "bot.py"]