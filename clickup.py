import json
import config
import requests


def create_clickup_ticket():

    try:
        url = f"https://api.clickup.com/api/v2/space/{config.product_infra_folder}/folder"
        headers = {"Authorization": config.clickup_api}
        r = requests.get(url=url, headers=headers)
        response_dict = json.loads(r.text)
        folders = response_dict["folders"]
        
        clickup_space_folders = []
        for folder in folders:
            tmp_dict = {}
            folder_id = folder['id']
            folder_name = folder['name']
            tmp_dict["folder_id"] = folder_id
            tmp_dict["folder_name"] = folder_name
            clickup_space_folders.append(tmp_dict)
        
        return clickup_space_folders
    
    except:
        print("\n* Function (get_task_member) Failed * ", sys.exc_info())

    

    return



# create ticket 
