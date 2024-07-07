from flask import Blueprint, request, jsonify
from ..handlers.slack import (
    send_onboarding_msg,
    handle_actions,
    handle_add_teammates_submission,
    send_connect_to_clickup_msg,
    send_configure_space_and_teammate_msg,
    send_hint_message,
    CallBacks,
)
from ..handlers.dify import create_clickup_ticket

from ..models.user import User
from ..models.targets import Targets
import json
import re

slack_bp = Blueprint("slack", __name__)


@slack_bp.route("/interacts", methods=["POST"])
def slack_interacts():
    payload = json.loads(request.form["payload"])

    if payload["type"] == "block_actions":
        handle_actions(payload)
    elif payload["type"] == "view_submission":
        if payload["view"]["callback_id"] == CallBacks.SETUP_SERVICES:
            errors = handle_add_teammates_submission(payload)
            if errors:
                return jsonify(errors)
            else:
                send_hint_message(payload["user"]["id"])

    return jsonify({})


@slack_bp.route("/events", methods=["POST"])
def slack_events():
    payload = request.json
    if "challenge" in payload:
        # Respond with the challenge value to verify this endpoint
        return jsonify({"challenge": payload["challenge"]})

    if "event" in payload:
        event = payload["event"]
        user_id = event["user"]

        member = User.get_member(user_id)
        teammates = Targets.get_targets(user_id)

        if not member:
            send_onboarding_msg(user_id)
        else:
            if not member.clickup_token:
                send_connect_to_clickup_msg(channel_id=user_id, user_id=user_id)
            elif not teammates:
                send_configure_space_and_teammate_msg(
                    channel_id=user_id, user_id=user_id
                )

        query = re.sub(r"<@U[A-Z0-9]+>", "", payload["event"]["text"]).strip()

        res = create_clickup_ticket(query)

    return jsonify({})
