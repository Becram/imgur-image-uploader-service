# Imgur REST Image Uploader

| SN |      Stack   | Technology        | 
|--| ------------- |:-------------:|
| 1 | Language     | Python | 
| 2 |Framework      | Flask      | 
| 3| Container | Docker      |  
| 4|Orchestrator | Docker Compose      |  


This is a service to upload images to imgur.com via its api endpoints. It tasks json object to upload the image ashychronosly. It implements [celery](http://www.celeryproject.org/) queue with [Redis](https://redis.io/) to perform the ashynchronity of the tasks. 

First of register an app in [imgur](https://api.imgur.com/oauth2/addclient) and get a **Client-ID** and the id to [celery-queue/tasks.py](celery-queue/tasks.py)

```python
...
Client_ID = 'XXXXXXXX'

celery = Celery('tasks', broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)

...                
```


### Installation


```bash
git clone https://github.com/becram/imgur-image-uploader-service
```

### Build & Launch
```bash
cd imgur-image-uploader-service
docker-compose  up --build
```


This will expose the Flask application's endpoints on port `8080` as well as a [Flower](https://github.com/mher/flower) server for monitoring workers on port `5555`

To add more workers:
```bash
docker-compose up -d --scale worker=5 --no-recreate
```


## Rest API Image upload endpoints

### Submit image URLs for upload
Submits a request to upload a set of image URLs to Imgur. The images will be uploaded to the configured Imgur, viewable by anyone with the link.
Request
```
POST /v1/images/upload
```
The request is just a JSON body, no query parameters.
Request body
Attributes:
* urls: An array of URLs to images that will be uploaded. Duplicates should be stripped out.

Example request body:
```json
{
"urls": [
    "https://farm3.staticflickr.com/2879/11234651086_681b3c2c00_b_d.jpg",
    "https://farm4.staticflickr.com/3790/11244125445_3c2f32cd83_k_d.jpg",     
     "https://www.rollingstone.com/wp-content/uploads/2019/04/notre-dame-rebuild.jpg",
     "https://media2.s-nbcnews.com/j/newscms/2019_16/2823376/190416-notre-dame-fire-mn-0740_4917dcab40d35a0c8da7db09fc8a0aa8.f-760w.jpg",
     "https://www.welcomenepal.com/uploads/slider/visit-nepal-year-2020-ntb-dmo-site-banner.jpeg",
     "https://www.welcomenepal.com/uploads/activity/pashupatinath-pilgrimage-tour-in-kathmandu-nepal.jpeg",
     "https://www.welcomenepal.com/uploads/slider/kathmandu-valley-nepal.jpeg",
     "http://www.welcomenepal.com/uploads/art_oy_kathmandu.jpg"
 
]
}
```
Response
On success, returns immediately with an appropriate status code with the id of the job.

Response body
Attributes:
* jobId: The id of the upload job that was just submitted.

Example response body:
```json
{
"jobId": "55355b7c-9b86-4a1a-b32e-6cdd6db07183",
}
```



## Gets the status of an upload images job.
Request
```
GET /v1/images/upload/:jobId
```
The request has no body and no query parameters. :jobId is an ID returned from the POST upload images API.

Request body: None

Response
On success, returns immediately with an appropriate status code with the id of the job.

Response body
Attributes:
* id: The id of the upload job.
* created: When job was created. In ISO8601 format (YYYY-MM-DDTHH:mm:ss.sssZ) for GMT.
* finished: When job was completed. In same format as created. Is null, if status is not complete.
* status: The status of the entire upload job. Is one of:
* pending: indicates job has not started processing.
* in-progress: job has started processing.
* complete: job is complete.
* uploaded: An object of arrays containing the set of URLs submitted, in several arrays indicating the status of that image URL upload (pending, complete, failed).

Example response body:

```json
{
  "created": "2019-04-22T03:00:49.447098",
  "finished": null,
  "id": "470f0516-b31f-4d14-8f87-77a5282bfe2f",
  "status": "in-progres",
  "uploaded": {
    "completed": [
      "https://i.imgur.com/YV08tTg.jpg"
    ],
    "failed": [
      
    ],
    "pending": "https://www.rollingstone.com/wp-content/uploads/2019/04/notre-dame-rebuild.jpg"
  }
}
```

## Get list of all uploaded image links
Gets the links of all images uploaded to Imgur. These links will be accessible by anyone.
Request
```
GET /v1/images
```
The request has no body and no query parameters.
Request bodyNone
Response
On success, return an array of the Imgur links to the successfully uploaded images. 
Response body
Attributes:
* uploaded: An array of the Imgur links to the uploaded images.
Example response body:
```json
{
  "uploaded": [
    "https://i.imgur.com/0i6HX3D.jpg",
    "https://i.imgur.com/q3urwVe.jpg",
    "https://i.imgur.com/uYdqs4i.jpg",
    "https://i.imgur.com/pa8eBQv.jpg",
    "https://i.imgur.com/mepUIVg.jpg",
    "https://i.imgur.com/1hNaxiY.jpg",
    "https://i.imgur.com/6AM3sJb.jpg"
  ]
}
```






## To shut down:

```bash
docker-compose down
```

To change the endpoints, update the code in [api/app.py](api/app.py)

## TO-DO: There is some issue in updation of the completed list which can be fixed using external datastore.

