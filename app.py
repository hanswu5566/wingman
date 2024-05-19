import secret
from tasks import handle_slack_event
from slack import WebClient
from flask import Flask, request, jsonify

app = Flask(__name__)
bot_client = WebClient(token=secret.bot_token)

@app.route("/",methods=["GET"])
def hello():
    return jsonify({"msg":"hello, are you Hans?"})

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
            handle_slack_event.delay(data)

    return jsonify({})


if __name__ == "__main__":
    app.run(port=8000)
