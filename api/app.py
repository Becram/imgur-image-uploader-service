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

# urls = '''
#     {
#     "urls": [
#         "https://farm3.staticflickr.com/2879/11234651086_681b3c2c00_b_d.jpg",
#         "https://farm4.staticflickr.com/3790/11244125445_3c2f32cd83_k_d.jpg"
#         ]
#     }

# '''


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

    # response = f" check status of  <a href='{url_for('check_task', task_id=task.id)}'>{task.id} </a> "
    return jsonify({"jobId": celery_job.id})







# @app.route("/api/funny")
# def serve_funny_quote():
#     upload_jobs = job_list()
#     nr_of_jobs = len(upload_jobs)
#     return jsonify(upload_jobs)




# # my_job[0] = json.loads(Jobs)

# def get_urllist(data):
#     urls_json = json.loads(data)
#     url_list = []
#     for value in urls_json['urls']:
#         url_list.append(value)
#     return url_list


# @app.route('/add')
# def upload():

#     task=celery.send_task('tasks.upload', args=[urls])
#     response = f"<a href='{url_for('check_task', task_id=task.id)}'>check status of {task.id} </a> <body> toolbar </body>"
#     return response

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
    else:
        pprint("********RESULT: {}".format(res.info))
        if res.info.get('completed') and res.info.get('completed') not in my_job[0]['uploaded']['completed']:
            my_job[0]['uploaded']['completed']=res.info.get('completed')
        if res.info.get('created'):
            my_job[0]['created']=res.info.get('created')
        my_job[0]['uploaded']['pending']= None
        my_job[0]['finished']= res.info.get('finished')
        my_job[0]['status']= res.info.get('status')
        return jsonify(my_job[0])
    # return jsonify(my_job[0])






# @app.route('/v1/images/upload/<string:jobId>')
# def check_task(jobId: str) -> str:
#     res = celery.AsyncResult(jobId)
#     json_job = get_job(jobId)
#     pprint("****{}".format(type(json_job)))
#     # if res.state == 'in-progress':
#     #     pprint("********PENING RESULT: {}".format(res.info))
#     #     if res.info.get('created'):
#     #         my_job[0]['created']=res.info.get('created')
#     #     if res.info.get('pending'):
#     #         my_job[0]['uploaded']['pending']=res.info.get('pending')
#     #     if res.info.get('completed') and res.info.get('completed') not in my_job[0]['uploaded']['completed']:
#     #         my_job[0]['uploaded']['completed'].append(res.info.get('completed'))
#     #     return jsonify(my_job[0])
#     # else:
#     #     pprint("********RESULT: {}".format(res.info))
#     #     if res.info.get('completed') and res.info.get('completed') not in my_job[0]['uploaded']['completed']:
#     #         my_job[0]['uploaded']['completed']=res.info.get('completed')
#     #     if res.info.get('created'):
#     #         my_job[0]['created']=res.info.get('created')
#     #     my_job[0]['uploaded']['pending']= None
#     #     my_job[0]['finished']= res.info.get('finished')
#     #     my_job[0]['status']= res.info.get('status')
#     #     return jsonify(my_job[0])
#     return json.jsonify(json_job)

    # if res.state == states.PENDING:

    #   return res.state
    # else:
    #   return str(res.result)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
