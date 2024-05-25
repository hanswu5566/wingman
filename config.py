import os
from dotenv import load_dotenv

load_dotenv()

dify_base_url = os.getenv('dify_url')
redis_url = os.getenv('redis_url')

role_to_slack_id = {
    "Product Manager": "U05S521VB1N",
    "Backend": "U9WTAK3AT",
    "iOS": "U8WB2544T",
    "Android": "U0208KZ25JT",
    "Web": "U1JMFP02V",
    "Engineering Manager":"U0316JH17",
    "Product Designer":"U0BNLJ70W"
}

role_to_clickup_id = {
    "Product Manager": 66766950,
    "Product Designer":3801075,
    "Backend": 5706220,
    "iOS": 5712395,
    "Android": 5936285,
    "Web": 5706438,
    "Engineering Manager":1026903,
}

product_infra_ticket_list_id = "900901259853"
product_infra_sprint_folder_id = "90091061131"

bot_slack_id = "U028NRCSKJM"
whitelist_slack_id = ["U05S521VB1N","U0327PUKEAD"]