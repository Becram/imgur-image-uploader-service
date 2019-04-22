import os
import time
from celery import Celery
import logging
from logging.handlers import RotatingFileHandler
import requests
import sys
import json
from pprint import pprint
from datetime import datetime
from celery_once import QueueOnce


CELERY_BROKER_URL = os.environ.get(
    'CELERY_BROKER_URL', 'redis://localhost:6379'),
CELERY_RESULT_BACKEND = os.environ.get(
    'CELERY_RESULT_BACKEND', 'redis://localhost:6379')

UPLOAD_FOLDER = os.environ.get(
    'UPLOAD_FOLDER', '/upload_files')

ALLOWED_EXTENSIONS = set(['jpeg', 'png', 'jpg'])
Client_ID = 'e5451a6ff4ab502'

celery = Celery('tasks', broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)


def get_filename(image_url):
    if image_url.find('/'):
        return image_url.rsplit('/', 1)[1]

# Download image from url and save at $UPLOAD_FOLDER
def download_image(image_url):
    response = requests.get(image_url, stream=True)

    # print(response.text)
    # response.raise_for_status()
    with open(UPLOAD_FOLDER + "/" + get_filename(image_url), "wb") as imageFile:
        for chunk in response.iter_content(1024):
            imageFile.write(chunk)
    return UPLOAD_FOLDER + "/" + get_filename(image_url)

# Uploading image to the imgur api endpoint
def upload_imgur(image_name):

    data = {}
    imgur_upload_url = "https://api.imgur.com/3/image"
    files = {}
    payload = {'image': open(image_name, 'rb')}
    headers = {
        'Authorization': 'Client-ID {}'.format(Client_ID)
    }
    response = requests.request(
        'POST', imgur_upload_url, headers=headers, files=payload)

    response_data = response.json()
    if response.json()['success'] == True:
        data['id'] = response.json()['data']['id']
        data['status'] = response.json()['status']
        data['link'] = response.json()['data']['link']
        return data
    else:
        data['error'] = response.json()['data']['error']
        data['status'] = response.json()['status']

        return data


#Convert json into list
def get_urllist(data):
    urls_json = json.loads(data)
    url_list = []
    for value in urls_json['urls']:
        url_list.append(value)
    return url_list



#Ashynchronlusly upload image and get the status and send it to app.py
@celery.task(name='tasks.upload', bind=True)
def upload_task(self, urls):
    job_created= datetime.now()

    url_list=get_urllist(urls)
    completed_list=[]
    error_list=[]
    
    for url in url_list:
        self.update_state(state='in-progress',
                        meta={'pending': url, 'created':job_created})
        pprint(url)
        image_link = upload_imgur(download_image(url))
        
        if image_link['status'] == 200:
            completed_list.append(image_link['link'])
            
            self.update_state(state='in-progress',
                        meta={'completed': image_link['link'], 'created':job_created, 'pending': None})
            time.sleep(2)
        else:

            self.update_state(state='failed',
                        meta={'error':image_link['error']})
            error_list.append("ERROR URL {}".format(url)+"==> "+image_link['error']['message'])
        
    return {'status': 'completed', 'completed':completed_list, 'finished': datetime.now(), 'created': job_created,'error': error_list}