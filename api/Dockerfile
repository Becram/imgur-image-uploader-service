FROM python:3.6-alpine

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true

WORKDIR /api

COPY requirements.txt /requirements.txt
# install requirements
RUN pip install -r /requirements.txt

# expose the app port
EXPOSE 8080

RUN pip install gunicorn

# run the app server
# CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "3", "app:app"]
CMD [ "python", "api/app.py", "runserver" ]