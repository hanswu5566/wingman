# extensions.py
import config
import secret
from celery import Celery
from slack_sdk import WebClient

celery_instance=None

def init_celery():
    global celery_instance
    if celery_instance is None:
        celery_instance = Celery('ai-me-celery', broker=config.redis_url, backend=config.redis_url)
    return celery_instance

bot_client = None

def init_bot_client():
    global bot_client
    if bot_client is None:
        bot_client = WebClient(token=secret.bot_token)
    return bot_client


init_celery()
init_bot_client()