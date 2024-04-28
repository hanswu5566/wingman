import json
import config
import clickup
import requests
import threading

from flask import Flask, request, jsonify

app = Flask(__name__)

def process_response(data):
    answer = json.loads(data["answer"])
    action = answer["action"]

    if not action:
        return

    if action == "create_ticket":
        clickup.create_clickup_ticket()


def handle_slack_event(data):
    text = data["event"]["text"]
    tag_pattern = f"<@{config.bot_slack_id}>"
    cleaned_msg = text.replace(tag_pattern, "").strip()

    data = {
        "inputs": {},
        "query": cleaned_msg,
        "response_mode": "blocking",
        "conversation_id": "",
        "user": "hans.wu",
    }

    try:
        response = requests.post(
            f"{config.dify_base_url}/chat-messages",
            headers={
                "Authorization": f"Bearer {config.dify_token}",
                "Content-Type": "application/json",
            },
            json=data,
        )
        if response.ok:
            data = response.json()
            process_response(data)
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
