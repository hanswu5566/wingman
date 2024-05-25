import os
from dotenv import load_dotenv

load_dotenv()

dify_token = os.getenv('dify_token')
clickup_token = os.getenv('clickup_token')
bot_token = os.getenv('bot_token')

product_infra_ticket_list_id = "900901259853"
product_infra_sprint_folder_id = "90091061131"

bot_slack_id = "U028NRCSKJM"
whitelist_slack_id = ["U05S521VB1N","U0327PUKEAD"]