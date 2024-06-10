from flask import Blueprint, request, jsonify, redirect, url_for
from ..handlers.slack import send_onboarding_msg,handle_interactivities
from slack_sdk.errors import SlackApiError
from ..extensions import slack_bot_client
from ..models.user import User

import json

slack_bp = Blueprint('slack', __name__)


@slack_bp.route("/interacts",methods=["POST"])
def slack_interacts():
    payload = json.loads(request.form['payload'])

    handle_interactivities(payload)
        
    return jsonify({})

@slack_bp.route("/events", methods=["POST"])
def slack_events():
    payload = request.json
    if "challenge" in payload:
        # Respond with the challenge value to verify this endpoint
        return jsonify({"challenge": payload["challenge"]})
    
    if "event" in payload:
        event = payload['event']
        user_id = event['user']
        channel = event['channel']
        text = event['text']

        if not User.is_member(user_id):
            send_onboarding_msg(user_id)




        
    
    return jsonify({})