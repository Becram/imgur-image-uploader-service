# Imgur REST Image Uploader

##Language: Python
##Framework: Flask
##Container: Docker
##Orchestrator: Docker Compose



This is a service to upload images to imgur.com via its api endpoints.It tasks json object to upload the image ashychronos. It implements [celery](http://www.celeryproject.org/) queue with [Redis](https://redis.io/) to perform the ashynchronity of the tasks. 

First of register an app in [imgur](https://api.imgur.com/oauth2/addclient) and get a **Client-ID** and the id to **celery-queue/tasks.py**

```python
----
Client_ID = 'e5451a6ff4ab502'

celery = Celery('tasks', broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)

---                
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


# Rest API Image upload endpoints

Gets the status of an upload images job.
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
● id: The id of the upload job.
● created: When job was created. In ISO8601 format (YYYY-MM-DDTHH:mm:ss.sssZ) for GMT.
● finished: When job was completed. In same format as created. Is n
ull​ if status is not complete.
● status: The status of the entire upload job. Is one of:
○ pending: indicates job has not started processing.
○ in-progress: job has started processing.
○ complete: job is complete.
● uploaded: An object of arrays containing the set of URLs submitted, in several arrays indicating the status of that image URL upload (pending, complete, failed).

Example response body:

```json
{
"id": "55355b7c-9b86-4a1a-b32e-6cdd6db07183",
"created": "2017-12-22T16:48:29+00:00",
"finished": null,
"status": "in-progress","uploaded": {
"pending": [
"https://www.factslides.com/imgs/black-cat.jpg",
],
"complete": [
"https://i.imgur.com/gAGub9k.jpg",
"https://i.imgur.com/skSpO.jpg"
],
"failed": [
]
}
}
```
Get list of all uploaded image links
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
● uploaded: An array of the Imgur links to the uploaded images.
Example response body:
```json
{
"uploaded": [
         "https://i.imgur.com/gAGub9k.jpg",
         "https://i.imgur.com/skSpO.jpg"
]
}
```






To shut down:

```bash
docker-compose down
```

To change the endpoints, update the code in [api/app.py](api/app.py)

