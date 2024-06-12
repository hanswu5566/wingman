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


def get_workspaces(access_token):
    url = "https://api.clickup.com/api/v2/team"

    headers = {"Authorization": access_token}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data
    except Exception as e:
        shared_logger.error(e)


def get_spaces(workspace_id,access_token):
    url = "https://api.clickup.com/api/v2/team/" + workspace_id + "/space"

    headers = {"Authorization": access_token}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data
    except Exception as e:
        shared_logger.error(e)
