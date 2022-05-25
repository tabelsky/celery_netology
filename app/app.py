import nanoid
from io import BytesIO

from flask import Flask
from flask import request
from flask.views import MethodView
from flask import jsonify


import config
import gridfs
from celery_app import celery_app, get_task, match_photos
from face_checker import FaceChecker
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask('app')

mongo = PyMongo(app, uri=config.MONGO_DSN)
celery_app.conf.update(app.config)


class ContextTask(celery_app.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery_app.Task = ContextTask


class Comparison(MethodView):

    def get(self, task_id):
        task = get_task(task_id)
        print({'status': task.status,
                        'result': task.result})
        return jsonify({})

    def post(self):
        image_pathes = [self.save_image(field) for field in ('image_1', 'image_2')]
        task = match_photos.delay(*image_pathes)
        return jsonify(
            {'task_id': task.id}
        )

    def save_image(self, field) -> str:
        nanoid.generate()
        files = gridfs.GridFS(mongo.db)
        image = request.files.get(field)
        file_name = f'{nanoid.generate()}{image.filename}'

        return str(files.put(image))



comparison_view = Comparison.as_view('comparison')
app.add_url_rule('/comparison/<string:task_id>', view_func=comparison_view, methods=['GET'])
app.add_url_rule('/comparison/', view_func=comparison_view, methods=['POST'])


if __name__ == '__main__':
    app.run()
