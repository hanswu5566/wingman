from ..config import Config
from ..secret import Secret
from logger import shared_logger
import requests
import json

from .clickup import create_clickup_ticket
from ..extensions import celery_instance
from ..extensions import slack_bot_client
from logger import shared_logger


@celery_instance.task
def handle_slack_event(payload):
    text = payload["event"]["text"]
    channel = payload["event"]["channel"]
    tag_pattern = f"<@{Config.BOT_SLACK_ID}>"
    cleaned_msg = text.replace(tag_pattern, "").strip()

    try:
        response = requests.post(
            f"{Config.DIFY_BASE_URL}/chat-messages",
            headers={
                "Authorization": f"Bearer {Secret.DIFY_TOKEN}",
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


def process_dify(answer, channel):
    # Respond typical error message
    if "action" not in answer:
        slack_bot_client.chat_postMessage(channel=channel, text=answer["msg"])
        return

    action = answer["action"]

    # Trigger clickup ticket creation
    if action == "create_ticket":
        res = create_clickup_ticket(answer)
        if res:
            url = res["url"]
            (
                slack_bot_client.chat_postMessage(
                    channel=channel, text=f"{answer['msg']}: {url}"
                )
            )
