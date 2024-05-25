import secret
import requests
import config
import json
import clickup
from celery import Celery
from slack import WebClient
from logger import shared_logger

celery_instance = Celery('ai-me-task', broker=config.redis_url,backend=config.redis_url)
bot_client = WebClient(token=secret.bot_token)

def process_dify(answer, channel):
    # Respond typical error message
    if "action" not in answer:
        bot_client.chat_postMessage(channel=channel, text=answer["msg"])
        return

    action = answer["action"]

    # Trigger clickup ticket creation
    if action == "create_ticket":
        res = clickup.create_clickup_ticket(answer)
        if res:
            url = res["url"]
            (
                bot_client.chat_postMessage(
                    channel=channel, text=f"{answer['msg']}: {url}"
                )
            )

@celery_instance.task
def handle_slack_event(data):
    text = data["event"]["text"]
    channel = data["event"]["channel"]
    tag_pattern = f"<@{config.bot_slack_id}>"
    cleaned_msg = text.replace(tag_pattern, "").strip()

    try:
        response = requests.post(
            f"{config.dify_base_url}/chat-messages",
            headers={
                "Authorization": f"Bearer {secret.dify_token}",
                "Content-Type": "application/json",
            },
            json={
                "inputs": {},
                "query": cleaned_msg,
                "response_mode": "blocking",
                "conversation_id": "",
                "user": "hans.wu",
            },
        )

        if response.ok:
            dify_msg = response.json()
            answer = json.loads(
                (dify_msg["answer"].replace("```json\n", "").replace("\n```", ""))
            )
            process_dify(answer, channel)
    except requests.exceptions.RequestException as e:
        shared_logger.error(f"Error: {e}")
        raise e
    