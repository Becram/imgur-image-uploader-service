from flask import *
from flask import url_for
from worker import celery
from celery import signature
import celery.states as states
from flask_debugtoolbar import DebugToolbarExtension
import logging
from datetime import datetime
from pprint import pprint
from jobs import job_list
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Dont tell'
file_handler = logging.FileHandler('app.log')

UPLOAD_FOLDER = "/upload_files"
pending = []
completed = []


jobs = [
{
        "id": 'id',
        "created": "created",
        "finished": None,
        "status": "in-progress",
         "uploaded": {
                "pending": [],
                "completed": [],
                "failed": []

        }
}
]



@app.route('/v1/images/jobs', methods=['GET'])
def get_jobs():
    return jsonify({'jobs': [job for job in jobs]})



@app.route('/v1/images/upload', methods=['POST'])
def create_job():
    if not request.json or 'urls' not in request.json:
        abort(400)
    pprint(request.json)
    celery_job=celery.send_task('tasks.upload', args=[json.dumps(request.json)])
    pprint(celery_job.id) 
    job = {
        'id': celery_job.id,
        "created": datetime.now(),
        "finished": None,
        "status": None,
        'uploaded':{
            "pending": [],
            "completed": [],
            "failed": []
        }
    }

    jobs.append(job)

    return jsonify({"jobId": celery_job.id})



@app.route('/v1/images/upload/<string:jobId>', methods=['GET'])
def get_job(jobId):
    res = celery.AsyncResult(jobId)
    my_job = [job for job in jobs if job['id'] == jobId ]
    if len(my_job) == 0:
        abort(404)

    if res.state == 'in-progress':
        pprint("********PENING RESULT: {}".format(res.info))
        if res.info.get('created'):
            my_job[0]['created']=res.info.get('created')
        if res.info.get('pending'):
            my_job[0]['uploaded']['pending']=res.info.get('pending')
        if res.info.get('completed') and res.info.get('completed') not in my_job[0]['uploaded']['completed']:
            my_job[0]['uploaded']['completed'].append(res.info.get('completed'))
        return jsonify(my_job[0])
    elif res.state == 'failed':
        if res.info.get('error'):
            my_job[0]['uploaded']['failed']= res.info.get('error')
    else:    
        pprint("********RESULT: {}".format(res.info))
        if res.info.get('completed') and res.info.get('completed') not in my_job[0]['uploaded']['completed']:
            my_job[0]['uploaded']['completed']=res.info.get('completed')
        if res.info.get('created'):
            my_job[0]['created']=res.info.get('created')
        if res.info.get('error'):
            my_job[0]['uploaded']['failed']= res.info.get('error')
        my_job[0]['uploaded']['pending']= []
        my_job[0]['finished']= res.info.get('finished')
        my_job[0]['status']= res.info.get('status')
        return jsonify(my_job[0])
    # return jsonify(my_job[0])




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
