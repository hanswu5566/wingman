from ..db import db
from ..extensions import slack_bot_client,celery_instance
from ..models.user import User
from ..models.targets import Targets
from ..models.contexts import Contexts

from ..config import Config
from logger import shared_logger
from copy import deepcopy
from slack_sdk.errors import SlackApiError
from flask import jsonify
from .clickup import (
    get_spaces,
    get_list,
    get_members,
    get_folders,
    create_clickup_ticket,
)


class UserAction:
    SIGN_UP = "sign_up"
    OPEN_SETUP_MODAL = "open_setup_modal"
    CONNECT_TO_CLICKUP = "connect_to_clickup"
    SELECT_CLICKUP_LISTS = "select_clickup_lists"
    SELECT_TARGET_CLICKUP_LIST = "select_target_clickup_list"


class CallBacks:
    SETUP_SERVICES = "setup_services"


roles = [
    "Product Manager",
    "Engineering Manager",
    "Product Designer",
    "Web",
    "Backend",
    "iOS",
    "Android",
]

ONBOARDING_MSG = {
    "blocks": [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Welcome to Wingman! 🎉"},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Welcome to Wingman! We are thrilled to have you join us. \n Wingman is an AI assistant designed to elevate your productivity by leveraging Large Language Models (LLM) to seamlessly integrate with project management software and streamline your daily task management.\n",
            },
        },
    ]
}


def handle_challenge(data):
    if "challenge" in data:
        # Respond with the challenge value to verify this endpoint
        return jsonify({"challenge": data["challenge"]})

def handle_setup_wingman_submission(payload):
    try:
        handle_update_teammates.delay(payload)
        slack_bot_client.chat_postMessage(channel=payload['user']['id'],text='Update teammates successfully done. Try creating another ticket.')
    except Exception as e:
        shared_logger.error(f"Error setting up teammates: {e.response['error']}")
        raise e

    return jsonify({})


@celery_instance.task
def handle_update_teammates(payload):
    teammates = {}
    state_values = payload["view"]["state"]["values"]
    clikcup_lists = (
        state_values.get(UserAction.SELECT_CLICKUP_LISTS, {})
        .get(UserAction.SELECT_CLICKUP_LISTS, {})
        .get("selected_options", [])
    )
    clickup_list_ids = [option["value"] for option in clikcup_lists]

    if len(clickup_list_ids) == 0:
        return {
            "response_action": "errors",
            "errors": {
                UserAction.SELECT_CLICKUP_LISTS: "Need to set at least one clickup list"
            },
        }

    for role in roles:
        role_key = f"select_{role.lower()}"
        if role_key in state_values:
            for key in state_values[role_key]:
                selected_users = state_values[role_key][key].get("selected_users", [])
                for user in selected_users:
                    info = slack_bot_client.users_info(user=user)
                    if (
                        info.data["ok"]
                        and not info.data["user"]["is_bot"]
                        and info.data["user"]["id"] != "USLACKBOT"
                    ):
                        if role.lower() not in teammates:
                            teammates[role.lower()] = []
                        teammates[role.lower()].append(
                            {"id": user, "email": info.data["user"]["profile"]["email"]}
                        )

    target = Targets.get_targets(slack_user_id=payload["user"]["id"])

    if not target:
        new_target = Targets(
            slack_user_id=payload["user"]["id"],
            clickup_lists=clickup_list_ids,
            ios_teammates=teammates.get("ios", []),
            web_teammates=teammates.get("web", []),
            android_teammates=teammates.get("android", []),
            backend_teammates=teammates.get("backend", []),
            product_manager_teammates=teammates.get("product manager", []),
            engineering_manager_teammates=teammates.get("engineering manager", []),
            product_designer_teammates=teammates.get("product designer", []),
        )

        db.session.add(new_target)
    else:
        target.slack_user_id = payload["user"]["id"]
        target.clickup_lists = clickup_list_ids
        target.ios_teammates = teammates.get("ios", target.ios_teammates)
        target.web_teammates = teammates.get("web", target.web_teammates)
        target.android_teammates = teammates.get("android", target.android_teammates)
        target.backend_teammates = teammates.get("backend", target.backend_teammates)
        target.product_manager_teammates = teammates.get(
            "product manager", target.product_manager_teammates
        )
        target.engineering_manager_teammates = teammates.get(
            "engineering manager", target.engineering_manager_teammates
        )
        target.product_designer_teammates = teammates.get(
            "product designer", target.product_designer_teammates
        )

    db.session.commit()


def handle_actions(payload):
    action_id = payload["actions"][0]["action_id"]
    trigger_id = payload["trigger_id"]
    user = payload["user"]

    if action_id == UserAction.SIGN_UP:
        if not User.get_member(user["id"]):
            new_user = User(
                slack_user_id=user["id"],
                slack_team_id=user["team_id"],
                slack_user_name=user["name"],
            )

            db.session.add(new_user)
            db.session.commit()
            send_connect_to_clickup_msg(
                channel_id=payload["channel"]["id"],
                user_id=user["id"],
                ts=payload["message"]["ts"],
            )
    elif action_id == UserAction.OPEN_SETUP_MODAL:
        list_options = get_setup_clickup_list_options(user["id"])
        open_wingman_setup_modal(trigger_id, list_options)

    elif action_id == UserAction.SELECT_TARGET_CLICKUP_LIST:
        selected_options = []
        if "state" in payload and "values" in payload["state"]:
            for _, block in payload["state"]["values"].items():
                for action_id, action in block.items():
                    selected_option = action.get("selected_option")
                    if selected_option:
                        selected_options.append(selected_option["value"])

        if len(selected_options) > 0:
            slack_user_id = payload["user"]["id"]
            channel_id = payload['channel']['id']
            ts = payload['container']['message_ts']

            ctx = Contexts.get_contexts(slack_user_id=slack_user_id)
            answer = ctx.last_clickup_dify_answer

            if "action" not in answer:
                slack_bot_client.chat_postMessage(
                    channel=channel_id,ts=ts, text=answer["msg"]
                )
            else:
                action = answer["action"]
                targets = Targets.get_targets(slack_user_id=slack_user_id)
                user = User.get_member(slack_user_id=slack_user_id)
                members = get_members(user.clickup_team_id, user.clickup_token)
                # Trigger clickup ticket creation
                if action == "create_ticket":
                    res = create_clickup_ticket(
                        user.clickup_token,
                        answer,
                        targets,
                        selected_options[0],
                        members,
                    )
                if res:
                    url = res["url"]
                    (
                        slack_bot_client.chat_postMessage(
                            channel=channel_id,ts=ts,text=f"{answer['msg']}: {url}"
                        )
                    )

    return jsonify(
        {
            "response_type": "ephemeral",
            "replace_original": True,
            "delete_original": True,
        }
    )


def get_setup_clickup_list_options(user_id) -> tuple[list, list]:
    user = User.get_member(user_id)
    if not user:
        shared_logger.error(
            {"err": f"Member not found:{user['id']}", "ECODE": "AUTH_002"}
        )
        return jsonify(), 404

    spaces = get_spaces(user.clickup_team_id, user.clickup_token)

    list_options = []

    for sp in spaces:
        folders = get_folders(space_id=sp['id'], access_token=user.clickup_token)
        for folder in folders:
            lists = folder["lists"]
            for list in lists:
                list_options.append(
                    {
                        "text": {"type": "plain_text", "text": f'{folder['name']} : {list["name"]}'},
                        "value": list["id"],
                    }
                )

    return list_options


def open_wingman_setup_modal(trigger_id, list_options):
    select_user_content = []
    for role in roles:
        select_user_content.extend(
            [
                {
                    "type": "section",
                    "text": {"type": "plain_text", "text": f"{role}"},
                    "block_id": f"select_{role.lower()}",
                    "accessory": {
                        "type": "multi_users_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select slack teammates ",
                        },
                    },
                }
            ]
        )

    blocks = [
        {
            "type": "context",
            "elements": [
                {
                    "type": "plain_text",
                    "text": "Wingman will generate tickets and assign team members based on the ticket content and your configured settings.",
                    "emoji": True,
                }
            ],
        },
        {"type": "divider"},
        {
            "type": "input",
            "block_id": UserAction.SELECT_CLICKUP_LISTS,
            "label": {
                "type": "plain_text",
                "text": "Select target ClickUp lists",
            },
            "element": {
                "type": "multi_static_select",
                "action_id": UserAction.SELECT_CLICKUP_LISTS,
                "options": list_options,
                "placeholder": {
                    "type": "plain_text",
                    "text": "Must choose at least one list.",
                },
            },
        },
        {
            "type": "section",
            "text": {"type": "plain_text", "text": "Select Slack teammates"},
        },
    ]

    blocks.extend(select_user_content)

    view = {
        "type": "modal",
        "callback_id": CallBacks.SETUP_SERVICES,
        "title": {"type": "plain_text", "text": "Setup Wingman Service"},
        "blocks": blocks,
        "submit": {
            "type": "plain_text",
            "text": "Submit",
        },
    }

    try:
        slack_bot_client.views_open(trigger_id=trigger_id, view=view)
    except SlackApiError as e:
        shared_logger.error(f"Error sending message: {e.response['error']}")
        raise e


def send_configure_space_and_teammate_msg(channel_id, user_id, ts=None):
    if not User.get_member(user_id):
        shared_logger.error({"err": f"Member not found:{user_id}", "ECODE": "AUTH_002"})
        return jsonify(), 404

    user = User.query.filter_by(slack_user_id=user_id).first()

    if not user.clickup_token:
        shared_logger.error(
            {"err": f"Clickup token not found:{user_id}", "ECODE": "AUTH_003"}
        )
        return jsonify(), 404

    msg = deepcopy(ONBOARDING_MSG) if ts else {"blocks": []}

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Setting up the wingman service. It's almost done.",
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Setup Services"},
                    "action_id": UserAction.OPEN_SETUP_MODAL,
                }
            ],
        },
    ]

    msg["blocks"].extend(blocks)

    try:
        if not ts:
            slack_bot_client.chat_postMessage(
                channel=user_id, blocks=msg["blocks"], text="Congrats !"
            )
        else:
            slack_bot_client.chat_update(
                channel=channel_id, blocks=msg["blocks"], ts=ts, text="Congrats"
            )
    except SlackApiError as e:
        shared_logger.error(f"Error sending message: {e.response['error']}")
        raise e


def send_connect_to_clickup_msg(channel_id, user_id, ts=None):
    msg = deepcopy(ONBOARDING_MSG) if ts else {"blocks": []}

    msg["blocks"].extend(
        [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hello <@{user_id}> \n You've completed sign up process.\nLet's integrate your Clickup to finish it.",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "ClickUp OAuth Login"},
                        "url": f"{Config.CLICKUP_REDIRECT_URL}&state={user_id},{channel_id},{ts}",
                        "action_id": UserAction.CONNECT_TO_CLICKUP,
                    }
                ],
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "plain_text",
                        "text": "Currently, only ClickUp is supported. \nWingman stores no confidential information from your ClickUp workspace.",
                    }
                ],
            },
        ]
    )

    try:
        if not ts:
            slack_bot_client.chat_postMessage(
                channel=user_id, blocks=msg["blocks"], text="Congrats !"
            )
        else:
            slack_bot_client.chat_update(
                channel=channel_id, blocks=msg["blocks"], ts=ts, text="Congrats"
            )
    except SlackApiError as e:
        shared_logger.error(f"Error sending message: {e.response['error']}")


def send_onboarding_msg(channel_id: str):
    msg = deepcopy(ONBOARDING_MSG)
    msg["blocks"].extend(
        [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": " \n We need you to sign up to proceed to setup.",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Sign up"},
                        "style": "primary",
                        "action_id": UserAction.SIGN_UP,
                    }
                ],
            },
        ]
    )

    try:
        slack_bot_client.chat_postMessage(
            channel=channel_id, blocks=msg["blocks"], text=""
        )
    except SlackApiError as e:
        shared_logger.error(f"Error sending message: {e.response['error']}")
        raise e


def send_select_list_msg(slack_user_id,channel_id):
    targets = Targets.get_targets(slack_user_id=slack_user_id)

    if not targets:
        msg = f"User {slack_user_id} failed to find targets"
        shared_logger.error(msg)
        return jsonify({"error": msg})

    if len(targets.clickup_lists) == 0:
        msg = f"User {slack_user_id}, clickup lists length is zero"
        shared_logger.error(msg)
        return jsonify({"error": msg})

    user = User.get_member(slack_user_id=slack_user_id)
    if not user:
        msg = f"User {slack_user_id} not exist"
        shared_logger.error(msg)
        return jsonify({"error": msg})

    options = []
    for list_id in targets.clickup_lists:
        list_info = get_list(list_id=list_id, access_token=user.clickup_token)
        name =  f'{list_info['space']['name']}-{list_info['folder']['name']}-{list_info['name']}'
        options.append(
            {
                "text": {"type": "plain_text", "text":name},
                "value": list_id,
            }
        )

    msg = {}
    msg["blocks"] = [
        {
            "type": "input",
            "block_id": UserAction.SELECT_TARGET_CLICKUP_LIST,
            "label": {
                "type": "plain_text",
                "text": f"Now please select the target list for the ticket",
            },
            "element": {
                "type": "static_select",
                "action_id": UserAction.SELECT_TARGET_CLICKUP_LIST,
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select an list to create ticket",
                },
                "options": options,
            },
        }
    ]

    try:
        slack_bot_client.chat_postEphemeral(
            channel=channel_id, user=slack_user_id, blocks=msg["blocks"], text="select_target_space"
        )
    except SlackApiError as e:
        shared_logger.error(f"Error sending message: {e.response['error']}")
        raise e

