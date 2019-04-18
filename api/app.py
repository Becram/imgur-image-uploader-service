from flask import *
from flask import url_for
from worker import celery
from celery import signature
import celery.states as states
from flask_debugtoolbar import DebugToolbarExtension
import logging
from datetime import datetime
from pprint import pprint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Dont tell'


UPLOAD_FOLDER = "/upload_files"
pending = []
completed = []

urls = '''
    {
    "urls": [
        "https://farm3.staticflickr.com/2879/11234651086_681b3c2c00_b_d.jpg",
        "https://farm4.staticflickr.com/3790/11244125445_3c2f32cd83_k_d.jpg"
        ]
    }

'''


Jobs = '''
{
        "id": "id",
        "created": "created",
        "finished": null,
        "status": "in-progress",
         "uploaded": {
                "pending": [],
                "completed": [],
                "failed": []

        }
}
'''
my_json = json.loads(Jobs)

def get_urllist(data):
    urls_json = json.loads(data)
    url_list = []
    for value in urls_json['urls']:
        url_list.append(value)
    return url_list


@app.route('/add')
def upload():

    task=celery.send_task('tasks.upload', args=[urls])
    response = f"<a href='{url_for('check_task', task_id=task.id)}'>check status of {task.id} </a> <body> toolbar </body>"
    return response



@app.route('/check/<string:task_id>')
def check_task(task_id: str) -> str:
    res = celery.AsyncResult(task_id)
    my_json['id'] = task_id
    if res.state == 'in-progress':
        pprint("********PENING RESULT: {}".format(res.info))
        if res.info.get('created'):
            my_json['created']=res.info.get('created')
        if res.info.get('pending'):
            my_json['uploaded']['pending']=res.info.get('pending')
        if res.info.get('completed') and res.info.get('completed') not in my_json['uploaded']['completed']:
            my_json['uploaded']['completed'].append(res.info.get('completed'))
        return jsonify(my_json)
    else:
        pprint("********RESULT: {}".format(res.info))
        if res.info.get('completed') and res.info.get('completed') not in my_json['uploaded']['completed']:
            my_json['uploaded']['completed']=res.info.get('completed')
        if res.info.get('created'):
            my_json['created']=res.info.get('created')
        my_json['uploaded']['pending']= None
        my_json['finished']= res.info.get('finished')
        my_json['status']= res.info.get('status')
        return jsonify(my_json)
    

    # if res.state == states.PENDING:

    #   return res.state
    # else:
    #   return str(res.result)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
