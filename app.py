import secret
import config
from celery_app import celery_instance,handle_slack_event
from slack import WebClient
from flask import Flask, request, jsonify

app = Flask(__name__)
bot_client = WebClient(token=secret.bot_token)

@app.route("/",methods=["GET"])
def hello():
    return jsonify({"msg":"hello, are you Hans?"})

@app.route("/celery/hearbeat",methods=["GET"])
def check_celery():
    i = celery_instance.control.inspect()
    active_workers = i.active()
    if active_workers:
        return jsonify(status="alive"), 200
    else:
        return jsonify(status="dead"), 503

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json  # Get JSON data from the request
    # Check if this is a challenge request
    if "challenge" in data:
        # Respond with the challenge value to verify this endpoint
        return jsonify({"challenge": data["challenge"]})

    if "event" in data:
        if data["event"]["user"] not in config.whitelist_slack_id:
            bot_client.chat_postMessage(
                channel=data["event"]["channel"],
                text="Sorry, you're not in the whitelist",
            )
        else:
            bot_client.chat_postMessage(
                channel=data["event"]["channel"], text="OK, please wait...."
            )
            handle_slack_event.delay(data)

    return jsonify({})


if __name__ == "__main__":
    app.run(debug=True,port=8000,use_reloader=False)
