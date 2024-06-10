# extensions.py
from .config import Config
from .secret import Secret
from celery import Celery
from slack_sdk import WebClient

celery_instance=Celery('ai-me-celery', broker=Config.REDIS_URL, backend=Config.REDIS_URL)
slack_bot_client = WebClient(Secret.BOT_TOKEN)