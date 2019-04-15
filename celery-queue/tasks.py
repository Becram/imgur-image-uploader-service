import os
import time
from celery import Celery
import logging
from logging.handlers import RotatingFileHandler
import requests
import sys


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
	with open(DEST+"/"+get_filename(image_url), "wb") as imageFile:
		for chunk in response.iter_content(1024):
			imageFile.write(chunk)
	return DEST+"/"+get_filename(image_url)



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
		response_data=response.json()
		data['id'] = response.json()['data']['id']
		data['status'] = response.json()['status']
		data['link'] = response.json()['data']['link']
		json_data = data
		# logger.info(str(json_data))
		return str(json_data)
	except KeyError:
		link = "Failed"
		return link




@celery.task(name='tasks.add')
def add(x: int, y: int) -> int:
	time.sleep(5)
	return x + y


@celery.task(name='tasks.upload')
def upload() -> str:
    img_url= "https://cdn0.tnwcdn.com/wp-content/blogs.dir/1/files/2018/06/instagram-796x431.png"
    image_link = upload_imgur(download_image(img_url))    
    return image_link

