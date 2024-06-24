from ..db import db
from ..extensions import slack_bot_client
from ..models.user import User
from ..config import Config
from logger import shared_logger
from copy import deepcopy
from slack_sdk.errors import SlackApiError
from flask import jsonify
from .clickup import get_spaces,get_members

class UserAction:
    SIGN_UP = 'sign_up'
    OPEN_SETUP_MODAL = 'open_setup_modal'
    CONNECT_TO_CLICKUP = 'connect_to_clickup'
    SELECT_CLICKUP_SPACES = 'select_clickup_space'

roles =  ['Product Manager','Engineering Manager','Product Designer','Web','Backend','iOS','Android']

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

def handle_teammates_submission(payload):
    state_values = payload['view']['state']['values']
    # Extract the selected ClickUp spaces
    clickup_spaces = state_values.get(UserAction.SELECT_CLICKUP_SPACES, {}).get(UserAction.SELECT_CLICKUP_SPACES, {}).get('selected_options', [])
    clickup_spaces_ids = [option['value'] for option in clickup_spaces]

    # Define roles based on your roles list
    teammates = {}

    for role in roles:
        role_key = f'select_{role.lower()}'
        if role_key in state_values:
            for key in state_values[role_key]:
                selected_users = state_values[role_key][key].get('selected_users', [])
                teammates[role.lower()] = [user for user in selected_users]

    
    

    # Example: Printing the extracted values
    print("ClickUp Spaces:", clickup_spaces_ids)
    for role, user_ids in teammates.items():
        print(f"{role} Teammates:", user_ids)

    return jsonify({})

def handle_actions(payload):
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
        sp_options = get_setup_clickup_options(user['id'])
        open_wingman_setup_modal(trigger_id,sp_options)

    return jsonify({})


def get_setup_clickup_options(user_id)->tuple[list,list]:
    user = User.get_member(user_id)
    if not user:
        shared_logger.error({"err": f"Member not found:{user['id']}", "ECODE": "AUTH_002"})
        return jsonify(),404
 
    spaces = get_spaces(user.clickup_team_id,user.clickup_token)
    members = get_members(user.clickup_team_id,user.clickup_token)

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

def open_wingman_setup_modal(trigger_id,sp_options):
    select_user_content=[]
    for role in roles:
        select_user_content.extend([
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": f"{role}"
            },
            'block_id':f'select_{role.lower()}',
            "accessory":{
                "type": "multi_users_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select the teammates to whom tickets will be assigned"
                },
            },
        }])

    blocks = [
        {
			"type": "context",
			"elements": [
				{
					"type": "plain_text",
					"text": "Wingman will generate tickets and assign team members based on the ticket content and your configured settings.",
					"emoji": True
				}
			]
		},
        {
            "type": "divider"
        },
        {
            "type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Select target clickup spaces"
			},
            "block_id": UserAction.SELECT_CLICKUP_SPACES,
            "accessory":{
                "type": "multi_static_select",
                "action_id": UserAction.SELECT_CLICKUP_SPACES,
                "options": sp_options,
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select clickup spaces where tickets will reside."
                },
            },
        },
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": "Select Slack teammates"
            }
        },
    ]

    blocks.extend(select_user_content)


    view = {
        "type": "modal",
        "callback_id": "setup-wingman-modal",
        "title": {
            "type": "plain_text",
            "text": "Setup Wingman Service"
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

def send_configure_space_and_teammate_msg(channel_id,user_id,ts=None):
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
                "text": "Almost done. You have my word. This is the last step."
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


