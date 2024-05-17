import json
import secret
import config
import clickup
import requests
import threading
from logger import shared_logger
from slack import WebClient
from flask import Flask, request, jsonify

app = Flask(__name__)
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


def handle_slack_event(data):
    text = data["event"]["text"]
    channel = data["event"]["channel"]
    tag_pattern = f"<@{secret.bot_slack_id}>"
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


@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json  # Get JSON data from the request
    # Check if this is a challenge request
    if "challenge" in data:
        # Respond with the challenge value to verify this endpoint
        return jsonify({"challenge": data["challenge"]})

    if "event" in data:
        if data["event"]["user"] != secret.my_slack_id:
            bot_client.chat_postMessage(
                channel=data["event"]["channel"],
                text="Sorry, temporarily I only serve to Hans Wu",
            )
        else:
            bot_client.chat_postMessage(
                channel=data["event"]["channel"], text="OK, please wait...."
            )
            thread = threading.Thread(target=handle_slack_event, args=(data,))
            thread.start()

    return jsonify({})


if __name__ == "__main__":
    app.run(debug=True, port=8000)
