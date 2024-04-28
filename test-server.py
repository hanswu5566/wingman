import json
import config
import clickup
import requests
import threading
from slack import WebClient
from flask import Flask, request, jsonify

app = Flask(__name__)

bot_client = WebClient(token=config.bot_token)


def process_dify(msg):
    answer = json.loads(msg["answer"])
    action = answer["action"]

    if not action:
        return

    if action == "create_ticket":
        return clickup.create_clickup_ticket(title=answer["title"],desc=answer["description"])



def handle_slack_event(data):
    text = data["event"]["text"]
    tag_pattern = f"<@{config.bot_slack_id}>"
    cleaned_msg = text.replace(tag_pattern, "").strip()

    try:
        response = requests.post(
            f"{config.dify_base_url}/chat-messages",
            headers={
                "Authorization": f"Bearer {config.dify_token}",
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
            result = process_dify(dify_msg)

            bot_client.chat_postMessage(
                channel=data["event"]["channel"],
                text=f"{dify_msg['answer']['msg']}:{result['url']}"
            )
        
    except:
        print("Error:", response)


@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json  # Get JSON data from the request
    # Check if this is a challenge request
    if "challenge" in data:
        # Respond with the challenge value to verify this endpoint
        return jsonify({"challenge": data["challenge"]})

    if "event" in data:
        thread = threading.Thread(target=handle_slack_event, args=(data,))
        thread.start()

    return jsonify({})


if __name__ == "__main__":
    app.run(debug=True, port=3000)
