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


def get_spaces(team_id, access_token):
    url = "https://api.clickup.com/api/v2/team/" + team_id + "/space"

    headers = {"Authorization": access_token}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data["spaces"]
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


def create_clickup_ticket(answer):

    title = answer["title"]
    desc = answer["description"]
    roles = answer["roles"]
    priority = answer["priority"]
    duration = answer["duration"]

    # try:
    #     target_list = get_target_list()
    #     create_task_url = (
    #         "https://api.clickup.com/api/v2/list/" + target_list["id"] + "/task"
    #     )

    #     payload = {
    #         "name": title,
    #         "description": desc,
    #         "assignees": [
    #             Config.role_to_clickup_id[role]
    #             for role in roles
    #             if role in Config.role_to_clickup_id
    #         ],
    #         "priority": priority,
    #         "due_date": (int(time.time() * 1000) + duration) if duration else None,
    #     }

    #     response = requests.post(create_task_url, json=payload, headers=headers)
    #     data = response.json()
    #     return data

    # except:
    #     shared_logger.error("\n* Function (create_task) Failed * ", sys.exc_info())
