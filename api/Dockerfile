FROM python:3.6.1
MAINTAINER Bikram Dhoju <itsbecram@gmail.com>



# Create the group and user to be used in this container
RUN groupadd flaskgroup && useradd -m -g flaskgroup -s /bin/bash flask


ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
# ENV C_FORCE_ROOT true

WORKDIR /api

COPY requirements.txt /requirements.txt

# install requirements
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt

# expose the app port
EXPOSE 8080

#Code ownership
RUN chown -R flask:flaskgroup /api

USER flask

# run the app server in development mode
ENTRYPOINT ["/api/entrypoint.sh"]
CMD [ "development" ]