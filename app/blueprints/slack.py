from flask import Blueprint, request, jsonify
from ..handlers.slack import (
    send_onboarding_msg,
    handle_actions,
    handle_setup_wingman_submission,
    send_connect_to_clickup_msg,
    send_configure_space_and_teammate_msg,
    CallBacks,
)
from ..handlers.dify import handle_clickup_request
from ..models.user import User
from ..models.targets import Targets
from logger import shared_logger
import json


slack_bp = Blueprint("slack", __name__)


@slack_bp.route("/interacts", methods=["POST"])
def slack_interacts():
    payload = json.loads(request.form["payload"])

    if payload["type"] == "block_actions":
        handle_actions(payload)
    elif payload["type"] == "view_submission":
        if payload["view"]["callback_id"] == CallBacks.SETUP_SERVICES:
            errors = handle_setup_wingman_submission(payload)
            if errors:
                return jsonify(errors)

    return jsonify({})


@slack_bp.route("/events", methods=["POST"])
def slack_events():
    try:
        payload = request.json
        if "challenge" in payload:
            # Respond with the challenge value to verify this endpoint
            return jsonify({"challenge": payload["challenge"]})

        if "event" in payload:
            event = payload["event"]
            slack_user_id = event["user"]

            member = User.get_member(slack_user_id)
            teammates = Targets.get_targets(slack_user_id)

            if not member:
                send_onboarding_msg(slack_user_id)
            else:
                if not member.clickup_token:
                    send_connect_to_clickup_msg(
                        channel_id=slack_user_id, user_id=slack_user_id
                    )
                elif not teammates:
                    send_configure_space_and_teammate_msg(
                        channel_id=slack_user_id, user_id=slack_user_id
                    )
                else:
                    handle_clickup_request(payload)

    except Exception as e:
        shared_logger.error(e)

    return jsonify({})
