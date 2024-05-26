from extensions import bot_client
from clickup import create_clickup_ticket


def process_dify(answer, channel):
    # Respond typical error message
    if "action" not in answer:
        bot_client.chat_postMessage(channel=channel, text=answer["msg"])
        return

    action = answer["action"]

    # Trigger clickup ticket creation
    if action == "create_ticket":
        res = create_clickup_ticket(answer)
        if res:
            url = res["url"]
            (
                bot_client.chat_postMessage(
                    channel=channel, text=f"{answer['msg']}: {url}"
                )
            )