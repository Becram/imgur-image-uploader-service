import os
import time
from celery import Celery
from celery import group
from celery import chord
from celery import shared_task
import logging
from logging.handlers import RotatingFileHandler
import requests
import sys
import json


CELERY_BROKER_URL = os.environ.get(
    'CELERY_BROKER_URL', 'redis://localhost:6379'),
CELERY_RESULT_BACKEND = os.environ.get(
    'CELERY_RESULT_BACKEND', 'redis://localhost:6379')

UPLOAD_FOLDER = "/upload_files"

ALLOWED_EXTENSIONS = set(['json', 'jpeg', 'png', 'jpg'])
Client_ID = 'e5451a6ff4ab502'

celery = Celery('tasks', broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)


def get_filename(image_url):
    if image_url.find('/'):
        return image_url.rsplit('/', 1)[1]


def download_image(image_url):
    DEST = "/upload_files"
    response = requests.get(image_url, stream=True)

    # print(response.text)
    # response.raise_for_status()
    with open(DEST + "/" + get_filename(image_url), "wb") as imageFile:
        for chunk in response.iter_content(1024):
            imageFile.write(chunk)
    return DEST + "/" + get_filename(image_url)


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
    try:
        response_data = response.json()
        data['id'] = response.json()['data']['id']
        data['status'] = response.json()['status']
        data['link'] = response.json()['data']['link']
        json_data = data
        # logger.info(str(json_data))
        return str(json_data)
    except KeyError:
        link = "Failed"
        return link


def get_urllist(data):
    urls_json = json.loads(data)
    url_list = []
    for value in urls_json['urls']:
        url_list.append(value)
    return url_list


@celery.task(name='tasks.add')
def add(x: int, y: int) -> int:
    time.sleep(5)
    return x + y



def get_url(x: str) -> str:
	group_urls = []
	url_list = get_urllist(x)
	for url in url_list:
		group_urls.append('upload_image({})'.format(url))
	fetch_jobs = group(group_urls)
	return chord(fetch_jobs).get()

# @celery.task(name='tasks.upload')
# def upload_image(url: str) -> str:
#     img_url = "https://cdn0.tnwcdn.com/wp-content/blogs.dir/1/files/2018/06/instagram-796x431.png"
#     image_link = upload_imgur(download_image(url))
#     return image_link


@celery.task(name='tasks.upload', bind=True)
def upload_task(self, urls):
    url_list=get_urllist(urls)

    for url in url_list:
        self.update_state(state='in-progress',
                        meta={'pending': url })
        image_link = upload_imgur(download_image(url))
        
        self.update_state(state='in-progress',
                          meta={'completed': image_link })


    
        time.sleep(1)
    return {'total': 100, 'completed': 'completed!'}