# routes.py
from flask import request, jsonify
from tasks import handle_slack_event
from extensions import celery_instance, bot_client
import config

def register_routes(app):
    @app.route("/", methods=["GET"])
    def hello():
        return jsonify({"msg": "hello, are you Hans?"})

    @app.route("/celery/heartbeat", methods=["GET"])
    def check_celery():
        i = celery_instance.control.inspect()
        active_workers = i.active()
        if active_workers:
            return jsonify(status="alive"), 200
        else:
            return jsonify(status="dead"), 503

    @app.route("/slack/events", methods=["POST"])
    def slack_events():
        try:
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
        except Exception as e:
            # Log the exception
            app.logger.error(f"Error processing Slack event: {e}")
            return jsonify({"error": "Internal Server Error"}), 500
