import sys
import time
import config
import secret
import requests


def create_clickup_ticket(title: str, desc: str, role: str):
    try:
        headers = {
            "Authorization": f"{secret.clickup_token}",
            "Content-Type": "application/json",
        }

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
                print("Error: list not found")
                return

        create_task_url = (
            "https://api.clickup.com/api/v2/list/" + target_list["id"] + "/task"
        )

        payload = {
            "name": title,
            "description": desc,
            "assignees": [config.role_to_clickup_id[role]],
            "custom_fields": [
                {"id": "d987dc02-abc2-4e3a-a350-442f7ca04e27", "value": 9},
            ],
        }

        response = requests.post(create_task_url, json=payload, headers=headers)
        data = response.json()
        return data

    except:
        print("\n* Function (create_task) Failed * ", sys.exc_info())
