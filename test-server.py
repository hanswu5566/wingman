import requests
import threading
from flask import Flask, request, jsonify


app = Flask(__name__)

dify_base_url = "https://api.dify.ai/v1"
dify_token = "app-C9bB48tWNbjf4Oc6NWpCW5gR"

zoo_test_slack_id = "U028NRCSKJM"
headers = {"Authorization": f"Bearer {dify_token}", "Content-Type": "application/json"}


def handle_slack_events(data):
    text = data["event"]["text"]
    tag_pattern = f"<@{zoo_test_slack_id}>"
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
            f"{dify_base_url}/chat-messages", headers=headers, json=data
        )
        if response.ok:
            data = response.json()
            print(data["answer"])
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
        thread = threading.Thread(target=handle_slack_events, args=(data,))
        thread.start()

    return jsonify({})


if __name__ == "__main__":
    app.run(debug=True, port=3000)
