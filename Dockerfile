FROM python:3.8-alpine

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000

CMD python manage.py runserver 0:8000
