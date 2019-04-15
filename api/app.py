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
pending=[]
completed=[]
failed=[]


Jobs='''
{
	"jobs":[
	   {
        "id": "id",
        "created": "created",
        "finished": "finished",
        "status": "in-progress",
         "uploaded": {
                "pending": "pending",
                "completed": "completed",
                "failed": null

         }
	   }

	]

}
'''
 


@app.route('/add')
def add() -> str:
    task = celery.send_task('tasks.upload')
    app.logger.info(type(task))
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
    my_json=json.loads(Jobs)
    my_json['jobs'][0]['id']=task_id
    my_json['jobs'][0]['created']=datetime.now()
    return jsonify(my_json)

    # if res.state == states.PENDING:



    #   return res.state
    # else:
    #   return str(res.result)

if __name__ == '__main__':
 	app.run(host="0.0.0.0", port=8080)

