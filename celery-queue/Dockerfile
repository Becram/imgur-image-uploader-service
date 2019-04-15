FROM python:3.6-alpine

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true
COPY requirements.txt /requirements.txt
# install requirements
RUN pip install -r /requirements.txt


RUN mkdir -p /upload_files
COPY . /queue
WORKDIR /queue



ENTRYPOINT celery -A tasks worker --loglevel=info