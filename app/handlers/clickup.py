import sys
import time
import requests
from logger import shared_logger


def get_authorized_user(access_token):
    url = "https://api.clickup.com/api/v2/user"

    headers = {"Authorization": access_token}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data
    except Exception as e:
        shared_logger.error(e)


def get_teams(access_token):
    url = "https://api.clickup.com/api/v2/team"

    headers = {"Authorization": access_token}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data["teams"]
    except Exception as e:
        shared_logger.error(e)


def get_space(space_id, access_token):
    url = "https://api.clickup.com/api/v2/space/" + space_id
    headers = {"Authorization": access_token}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data
    except Exception as e:
        shared_logger.error(e)


def get_spaces(team_id, access_token):
    url = "https://api.clickup.com/api/v2/team/" + team_id + "/space"

    headers = {"Authorization": access_token}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data["spaces"]
    except Exception as e:
        shared_logger.error(e)


def get_list(list_id, access_token):
    url = "https://api.clickup.com/api/v2/list/" + list_id
    headers = {"Authorization": access_token}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data
    except Exception as e:
        shared_logger.error(e)


def get_folders(space_id, access_token):
    url = "https://api.clickup.com/api/v2/space/" + space_id + "/folder"

    query = {"archived": "false"}

    headers = {"Authorization": access_token}
    try:
        response = requests.get(url, headers=headers, params=query)
        data = response.json()
        return data["folders"]
    except Exception as e:
        shared_logger.error(e)


def get_members(team_id, access_token):
    url = "https://api.clickup.com/api/v2/team/" + team_id

    headers = {"Authorization": access_token}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data["team"]["members"]
    except Exception as e:
        shared_logger.error(e)


def create_clickup_ticket(access_token, answer, targets, target_list, members):
    title = answer["title"]
    desc = answer["description"]
    roles = answer["roles"]
    priority = answer["priority"]
    duration = answer["duration"]

    assignees = []
    member_dict = {}

    for mb in members:
        member_dict[mb["user"]["email"]] = mb["user"]["id"]

    for role in roles:
        field_name = role.lower().replace(" ", "_") + "_teammates"
        if not hasattr(targets, field_name):
            continue

        teammates = getattr(targets, field_name)
        for tm in teammates:
            if tm["email"] in member_dict:
                assignees.append(member_dict[tm["email"]])

    try:
        create_task_url = "https://api.clickup.com/api/v2/list/" + target_list + "/task"

        headers = {
            "Authorization": access_token,
        }

        payload = {
            "name": title,
            "description": desc,
            "assignees": assignees,
            "priority": priority,
            "due_date": (int(time.time() * 1000) + duration) if duration else None,
        }

        response = requests.post(create_task_url, json=payload, headers=headers)
        data = response.json()
        return data

    except:
        shared_logger.error("\n* Function (create_task) Failed * ", sys.exc_info())
