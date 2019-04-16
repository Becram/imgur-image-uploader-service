from flask import *
from flask import url_for
from worker import celery
import celery.states as states
from flask_debugtoolbar import DebugToolbarExtension
import logging
from datetime import datetime

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'Dont tell'
toolbar = DebugToolbarExtension(app)

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
                "failed": [null]

        }
}
'''


def get_urllist(data):
    urls_json = json.loads(data)
    url_list = []
    for value in urls_json['urls']:
        app.logger.info(value)
        url_list.append(value)
    return url_list


@app.route('/add')
def upload(url):
    task = celery.send_task('tasks.upload', args=[url], kwargs={})
    # get_list = get_urllist(urls)
    # for url in getlist:
    #     task.subtask(url)

    # app.logger.info(str(get_urllist(urls)))
    response = f"<a href='{url_for('check_task', task_id=task.id, external=True)}'>check status of {task.id} </a> <body> toolbar </body>"
    return response

# @app.route('/add/<int:param1>/<int:param2>')
# def add(param1: int, param2: int) -> str:
#     task = celery.send_task('tasks.add', args=[param1, param2], kwargs={})
#     response = f"<a href='{url_for('check_task', task_id=task.id, external=True)}'>check status of {task.id} </a>"
#     return response


@app.route('/check/<string:task_id>')
def check_task(task_id: str) -> str:
    res = celery.AsyncResult(task_id)
    my_json = json.loads(Jobs)
    my_json['id'] = task_id
    my_json['created'] = datetime.now()
    return jsonify(my_json)

    # if res.state == states.PENDING:

    #   return res.state
    # else:
    #   return str(res.result)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
