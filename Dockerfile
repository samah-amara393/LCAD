# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y gunicorn vim

WORKDIR /app

COPY requirements.txt requirements.txt
#RUN pip install -r requirements.txt

COPY . .

CMD [ "gunicorn", "--bind" , "0.0.0.0:3400","app:app"]