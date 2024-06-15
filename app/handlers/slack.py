from flask import jsonify
from ..extensions import slack_bot_client
from slack_sdk.errors import SlackApiError
from ..models.user import User
from ..config import Config
from .clickup import get_spaces
from logger import shared_logger
from copy import deepcopy
from ..db import db

class UserAction:
    SIGN_UP = 'sign_up'
    SELECT_WORKSPACE= 'select_workspace'
    SELECT_SPACE = 'select_space'
    OPEN_SETUP_MODAL = 'open_setup_modal'
    CONNECT_TO_CLICKUP = 'connect_to_clickup'

ONBOARDING_MSG = {
	"blocks": [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Welcome to Wingman! 🎉"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Welcome to Wingman! We are thrilled to have you join us. \nWingman is an AI assistant designed to elevate your productivity by leveraging Large Language Models (LLM) to seamlessly integrate with project management software and streamline your daily task management.\n"
			}
		},
	]
}

def handle_challenge(data):
    if "challenge" in data:
        # Respond with the challenge value to verify this endpoint
        return jsonify({"challenge": data["challenge"]})
    

def handle_interactivities(payload):
    action_id = payload['actions'][0]['action_id']
    if action_id == UserAction.SIGN_UP:
        user = payload['user']

        if not User.get_member(user['id']):
            new_user = User(
                slack_user_id=user['id'],
                slack_team_id=user['team_id'],
                slack_user_name=user['name'],
            )

            db.session.add(new_user)
            db.session.commit()
            send_connect_to_clickup_msg(channel_id=payload['channel']['id'],user_id=user['id'],ts=payload['message']['ts'])
    elif action_id == UserAction.SELECT_WORKSPACE:
        selected_workspace = payload['actions'][0]['selected_option']['value']
        print(payload['actions'][0])
        
        

        return jsonify({})
    

def send_configure_clickup_initial_msg(channel_id,user_id,ts=None):
    if not User.get_member(user_id):
        shared_logger.error({"err": f"Member not found:{user_id}", "ECODE": "AUTH_002"})
        return jsonify(),404
    
    user = User.query.filter_by(slack_user_id=user_id).first()

    if not user.clickup_token:
        shared_logger.error({"err": f"Clickup token not found:{user_id}", "ECODE": "AUTH_003"})
        return jsonify(),404
    

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Almost done, this is the last step."
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Setup target workspace and folders"
                    },
                    "action_id": UserAction.OPEN_SETUP_MODAL
                }
            ]
        }
    ]
    
    msg = deepcopy(ONBOARDING_MSG) if ts else {}
    msg['blocks'].extend(blocks)

    try:
        if not ts:
            slack_bot_client.chat_postMessage(
                channel=channel_id,
                blocks=msg["blocks"],
                text="Congrats !"
            )
        else:
                slack_bot_client.chat_update(
                channel=channel_id,
                blocks=msg["blocks"],
                ts=ts,
                text="Congrats"
            )
    except SlackApiError as e:
        shared_logger.error(f"Error sending message: {e.response['error']}")


def send_connect_to_clickup_msg(channel_id:str,user_id:str,ts=None):
    msg = deepcopy(ONBOARDING_MSG) if ts else {}

    msg['blocks'].extend([{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"Hello <@{user_id}> \n You've completed sign up process. \n It's almost done. Let's integrate your Clickup to finish it."
        }
    },
   {
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "ClickUp OAuth Login"
					},
					"url": f'{Config.CLICKUP_REDIRECT_URL}&state={user_id},{channel_id},{ts}',
					"action_id": UserAction.CONNECT_TO_CLICKUP
				}
			]
    },
    {
        "type": "context",
        "elements": [
            {
                "type": "plain_text",
                "text": "Currently, only ClickUp is supported. \nWingman stores no confidential information from your ClickUp workspace.",
            }
        ]
    }   
    ])

    try:
        if not ts:
            slack_bot_client.chat_postMessage(
                channel=channel_id,
                blocks=msg["blocks"],
                text="Congrats !"
            )
        else:
                slack_bot_client.chat_update(
                channel=channel_id,
                blocks=msg["blocks"],
                ts=ts,
                text="Congrats"
            )
    except SlackApiError as e:
        shared_logger.error(f"Error sending message: {e.response['error']}")

def send_onboarding_msg(channel_id:str):
    msg = deepcopy(ONBOARDING_MSG)
    msg['blocks'].extend([
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": " \n We need you to sign up to proceed to setup."
        }
    },
    {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Sign up"
                },
                "style": "primary",
                "action_id": UserAction.SIGN_UP
            }
        ]
    }
    ])

    try:
        slack_bot_client.chat_postMessage(
            channel=channel_id,
            blocks=msg["blocks"],
            text=""
        )
    except SlackApiError as e:
        shared_logger.error(f"Error sending message: {e.response['error']}")


