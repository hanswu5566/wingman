# extensions.py
from app.config import Config
from app.secret import Secret
from celery import Celery
from slack_sdk import WebClient

celery_instance=Celery('ai-me-celery', broker=Config.redis_url, backend=Config.redis_url)
slack_bot_client = WebClient(Secret.bot_token)