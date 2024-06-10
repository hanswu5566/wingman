from flask import jsonify,redirect
from ..extensions import slack_bot_client
from slack_sdk.errors import SlackApiError
from ..models.user import User
from ..config import Config
from logger import shared_logger
from copy import deepcopy


class UserAction:
    SIGN_UP = 'sign_up'
    SETUP= 'setup'
    SELECT_MANAGEMENT_TOOL = 'select_management_tool'



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
    
def open_setup_modal(trigger_id):
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

        if not User.is_member(user['id']):
            new_user = User(
                slack_user_id=user['id'],
                slack_team_id=user['team_id'],
                slack_name=user['name'],
            )

            # db.session.add(new_user)
            # db.session.commit()
        
            send_select_management_tool_msg(channel_id=payload['channel']['id'],user_id=user['id'],ts=payload['message']['ts'])

    elif action_id == UserAction.SETUP:
        trigger_id = payload['trigger_id']
        try:
            open_setup_modal(trigger_id)
        except SlackApiError as e:
            shared_logger.error(f"Error sending message: {e.response['error']}")
    elif action_id == UserAction.SELECT_MANAGEMENT_TOOL:
        selected_option = payload['actions']
        if selected_option:
            if selected_option['value'] =='clickup':
                return redirect(f'{Config.CLICKUP_REDIRECT_URL}&state={payload['user']['id']},{payload['channel']['id']}')

        return jsonify({'status': 'ok'})


def send_configure_management_tool_msg(channel_id:str,user_id,ts=None):
    if not User.is_member(user_id):
        return jsonify({{"err": "Member not found", "ECODE": "AUTH_002"}}),400
    
    user = User.query.filter_by(slack_user_id=user_id).first()
    print(user.clickup_token)



def send_select_management_tool_msg(channel_id:str,user_id:str,ts=None):
    msg = deepcopy(ONBOARDING_MSG)
    msg['blocks'].extend([{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"Hello <@{user_id}> \n You've completed sign up process. \n It's almost done. Let's integrate your management tool to finish it."
        }
    },
    {
        "type": "input",
        "element": {
            "type": "static_select",
            "placeholder": {
                "type": "plain_text",
                "text": "Select your management tool",
                "emoji": True
            },
            "options": [
                {
                    "text": {
                        "type": "plain_text",
                        "text": "Clickup",
                    },
                    "value": "clickup"
                }
            ],
            "action_id": UserAction.SELECT_MANAGEMENT_TOOL
        },
        "label": {
            "type": "plain_text",
            "text": "Select an item",
            "emoji": True
        }
    },
    {
        "type": "context",
        "elements": [
            {
                "type": "plain_text",
                "text": "By now, only Clickup is supported.",
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