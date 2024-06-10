from flask import jsonify
from ..extensions import slack_bot_client
from slack_sdk.errors import SlackApiError
from ..texts.slack import  UserAction ,ONBOARDING_MSG,SETUP_MSG
from ..models.user import User
import requests
from logger import shared_logger
from copy import deepcopy


def handle_challenge(data):
    if "challenge" in data:
        # Respond with the challenge value to verify this endpoint
        return jsonify({"challenge": data["challenge"]})
    
def open_setup_modal(trigger_id):
    print(trigger_id)
    modal_view = {
        "type": "modal",
        "callback_id": "modal-identifier",
        "title": {
            "type": "plain_text",
            "text": "My Modal"
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "This is a modal window"
                }
            },
            {
                "type": "input",
                "block_id": "input_block",
                "label": {
                    "type": "plain_text",
                    "text": "Your Input"
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "input_value"
                }
            },
        ],
        "submit": {
						"type": 'plain_text',
						"text": 'Submit',
					},
    }

    slack_bot_client.views_open(trigger_id=trigger_id,view=modal_view)



def handle_interactivities(payload):
    action_id = payload['actions'][0]['action_id']

    if action_id == UserAction.SIGN_UP:
        user = payload['user']
        new_user = User(
            slack_user_id=user['id'],
            slack_team_id=user['team_id'],
            slack_name=user['name'],
        )

        # db.session.add(new_user)
        # db.session.commit()

        send_setup_management_tool_msg(channel_id=payload['channel']['id'],user_id=user['id'],ts=payload['message']['ts'])

    elif action_id == UserAction.SETUP:
        trigger_id = payload['trigger_id']
        try:
            open_setup_modal(trigger_id)
        except SlackApiError as e:
            shared_logger.error(f"Error sending message: {e.response['error']}")


def send_setup_management_tool_msg(channel_id:str,user_id:str,ts=None):
    msg = deepcopy(ONBOARDING_MSG)
    msg['blocks'].extend([{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"Hello <@{user_id}> \n You've completed sign up process. \n It's almost done. Let's pick and setup the management tool"
        }
    },
    {
        "type": "input",
        "element": {
            "type": "multi_static_select",
            "placeholder": {
                "type": "plain_text",
                "text": "Select options",
                "emoji": True
            },
            "options": [
                {
                    "text": {
                        "type": "plain_text",
                        "text": "*plain_text option 0*",
                        "emoji": True
                    },
                    "value": "value-0"
                },
                {
                    "text": {
                        "type": "plain_text",
                        "text": "*plain_text option 1*",
                        "emoji": True
                    },
                    "value": "value-1"
                },
                {
                    "text": {
                        "type": "plain_text",
                        "text": "*plain_text option 2*",
                        "emoji": True
                    },
                    "value": "value-2"
                }
            ],
            "action_id": "multi_static_select-action"
        },
        "label": {
            "type": "plain_text",
            "text": "Label",
            "emoji": True
        }
    }
    
        # {
        #     "type": "button",
        #     "text": {
        #         "type": "plain_text",
        #         "text": "Setup management tool"
        #     },
        #     "style": "primary",
        #     "action_id": UserAction.SETUP
        # }
    
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