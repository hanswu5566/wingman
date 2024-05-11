import sys
import time
import config
import secret
import requests
from logger import shared_logger


headers = {
    "Authorization": f"{secret.clickup_token}",
    "Content-Type": "application/json",
}


def get_target_list():
    try:
        get_folder_url = f"https://api.clickup.com/api/v2/folder/{secret.product_infra_sprint_folder_id}"
        response = requests.get(get_folder_url, headers=headers)

        if response.ok:
            data = response.json()
            lists = data["lists"]
            current_time_millis = int(round(time.time() * 1000))

            target_list = None

            for list in lists:
                if target_list:
                    break
                if current_time_millis < int(
                    list["start_date"]
                ) or current_time_millis > int(list["due_date"]):
                    continue
                target_list = list

            if not target_list:
                shared_logger.error("Error: list not found")
                return

            return target_list

    except:
        shared_logger.error("\n* Function (Get list) Failed * ", sys.exc_info())


def create_clickup_ticket(answer):

    title = answer["title"]
    desc = answer["description"]
    roles = answer["roles"]
    priority = answer["priority"]
    duration = answer["duration"]

    try:
        target_list = get_target_list()
        create_task_url = (
            "https://api.clickup.com/api/v2/list/" + target_list["id"] + "/task"
        )

        payload = {
            "name": title,
            "description": desc,
            "assignees": [
                config.role_to_clickup_id[role]
                for role in roles
                if role in config.role_to_clickup_id
            ],
            "priority": priority,
            "due_date": (int(time.time() * 1000) + duration) if duration else None,
        }

        response = requests.post(create_task_url, json=payload, headers=headers)
        data = response.json()
        return data

    except:
        shared_logger.error("\n* Function (create_task) Failed * ", sys.exc_info())
