FROM python:3.7-slim

WORKDIR /usr/src/app
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 80

CMD python manage.py migrate && \
    gunicorn get_voice_server.wsgi:application --bind 0.0.0.0:80 --workers=4 --timeout=300
