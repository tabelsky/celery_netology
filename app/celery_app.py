import pymongo
from celery import Celery
from celery.result import AsyncResult
from gridfs import GridFS
from cachetools import cached
from bson.objectid import ObjectId
from config import CELERY_BACKEND, CELERY_BROKER, MONGO_DSN
from face_checker import match_photos


celery_app = Celery(
    'app',
    backend=CELERY_BACKEND,
    broker=CELERY_BROKER
)


def get_task(task_id: str) -> AsyncResult:
    return AsyncResult(task_id, app=celery_app)


@cached({})
def get_fs():
    mongo = pymongo.MongoClient(MONGO_DSN)
    return GridFS(mongo['files'])


@celery_app.task()
def match_photos(file_name_1, file_name_2):
    print(file_name_1)
    print(file_name_2)
    print(file_name_1.read())
    mongo = pymongo.MongoClient(MONGO_DSN)
    files = GridFS(mongo['files'])

    result = match_photos(file_name_1, file_name_2)
    return result


x = get_fs().get_version('yIV_8FzjxQ_F_RMRyoLjGzhan_zhar.jpeg').read()
print(x)