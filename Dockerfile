FROM python:3.8-alpine

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000

CMD python manage.py migrate && \
    gunicorn get_voice_server.wsgi:application --bind 0.0.0.0:8000 --workers=4
