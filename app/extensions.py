from .config import Config
from .secret import Secret
from celery import Celery
from slack_sdk import WebClient

slack_bot_client = WebClient(Secret.BOT_TOKEN)
celery_instance = Celery(__name__, broker=Config.REDIS_URL, backend=Config.REDIS_URL)


def get_celery_instance():
    return celery_instance


def make_celery(app):
    celery = Celery(app.import_name, broker=Config.REDIS_URL, backend=Config.REDIS_URL)
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
