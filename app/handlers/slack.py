from flask import jsonify
from ..extensions import slack_bot_client
from slack_sdk.errors import SlackApiError
from ..models.user import User
from ..config import Config
from .clickup import get_workspaces
from logger import shared_logger
from copy import deepcopy
from ..db import db

class UserAction:
    SIGN_UP = 'sign_up'
    OPEN_SETUP_MODAL = 'open_setup_modal'
    CONNECT_TO_CLICKUP = 'connect_to_clickup'
    SELECT_WORKSPACE = 'select_workspace'
    SELECT_SPACES = 'select_space'

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
    trigger_id = payload['trigger_id']
    user = payload['user']

    if action_id == UserAction.SIGN_UP:
        if not User.get_member(user['id']):
            new_user = User(
                slack_user_id=user['id'],
                slack_team_id=user['team_id'],
                slack_user_name=user['name'],
            )

            db.session.add(new_user)
            db.session.commit()
            send_connect_to_clickup_msg(channel_id=payload['channel']['id'],user_id=user['id'],ts=payload['message']['ts'])
    elif action_id == UserAction.OPEN_SETUP_MODAL:
        sp_options = get_spaces_options(user['id'])
        open_configuration_initial_modal(trigger_id,sp_options)

    return jsonify({})


def get_spaces_options(user_id):
    user = User.get_member(user_id)
    if not user:
        shared_logger.error({"err": f"Member not found:{user['id']}", "ECODE": "AUTH_002"})
        return jsonify(),404
 
    spaces = user.clickup_workspace["spaces"]

    sp_options = []
    for sp in spaces:
        sp_options.append({
            "text": {
                "type": "plain_text",
                "text": sp["name"]
            },
            "value": sp["id"]
        })
    
    return sp_options

def open_configuration_initial_modal(trigger_id,sp_options):
    roles =  ['Android','Web','Backend','iOS','PM','EM']

    select_user_content=[]
    for role in roles:
        select_user_content.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Select your {role} teammate"
            },
            "accessory": {
               "type": "users_select",
				"placeholder":{
					"type": "plain_text",
					"text": "Select a user",
				},
            }
        })


    blocks = [
        {
            "type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Select target spaces"
			},
            "accessory":{
                "type": "multi_static_select",
                "action_id": UserAction.SELECT_SPACES,
                "options": sp_options
            },
        },
        {
			"type": "divider"
		},
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Select target spaces"
			},
		}
    ]

    blocks.extend(select_user_content)


    view = {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Setup Clickup"
        },
        "blocks": blocks,
        "submit": {
            "type": "plain_text",
            "text": "Submit",
        },
    }

    try:
        slack_bot_client.views_open(trigger_id=trigger_id,view=view)
    except SlackApiError as e:
        shared_logger.error(f"Error sending message: {e.response['error']}")

def send_configure_workspace_initial_msg(channel_id,user_id,ts=None):
    if not User.get_member(user_id):
        shared_logger.error({"err": f"Member not found:{user_id}", "ECODE": "AUTH_002"})
        return jsonify(),404
    
    user = User.query.filter_by(slack_user_id=user_id).first()

    if not user.clickup_token:
        shared_logger.error({"err": f"Clickup token not found:{user_id}", "ECODE": "AUTH_003"})
        return jsonify(),404
    
    msg = deepcopy(ONBOARDING_MSG) if ts else {"blocks":[]}


    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Almost done. This is the last step."
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Setup clickup"
                    },
                    "action_id": UserAction.OPEN_SETUP_MODAL
                }
            ]
        }
    ]
    
    msg["blocks"].extend(blocks)

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


def send_connect_to_clickup_msg(channel_id,user_id,ts=None):
    msg = deepcopy(ONBOARDING_MSG) if ts else {"blocks":[]}

    msg["blocks"].extend([{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"Hello <@{user_id}> \n You've completed sign up process.\nLet's integrate your Clickup to finish it."
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
                channel=user_id,
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


