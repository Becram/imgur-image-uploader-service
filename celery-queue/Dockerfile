FROM python:3.6.1
MAINTAINER Bikram Dhoju <itsbecram@gmail.com>


ARG UPLOAD_FOLDER
ENV UPLOAD_FOLDER $UPLOAD_FOLDER
RUN mkdir -p $UPLOAD_FOLDER

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0

# install requirements
RUN groupadd celerygroup && useradd -m -g celerygroup -s /bin/bash celery
COPY requirements.txt /requirements.txt



RUN pip install --upgrade pip
RUN pip install -r /requirements.txt



COPY . /queue

RUN chown -R celery:celerygroup /queue
RUN chown -R celery:celerygroup $UPLOAD_FOLDER

WORKDIR /queue

USER celery

ENTRYPOINT celery -A tasks worker --loglevel=info