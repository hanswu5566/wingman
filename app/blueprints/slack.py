from flask import Blueprint, request, jsonify
from ..handlers.slack import send_onboarding_msg,handle_interactivities,send_connect_to_clickup_msg,send_configure_workspace_initial_msg
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

        member = User.get_member(user_id)

        if not member:
            send_onboarding_msg(user_id)
        else:
            if not member.clickup_token:
                send_connect_to_clickup_msg(channel_id=user_id,user_id=user_id)
            elif not member.clickup_workspaces or not member.clickup_folders :
                send_configure_workspace_initial_msg(channel_id=user_id,user_id=user_id)
    
    
    return jsonify({})