import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    DIFY_BASE_URL = os.getenv('dify_url')
    REDIS_URL = os.getenv('redis_url')
    SLACK_REDIRECT_URL = os.getenv('slack_redirect_url')

    CLICKUP_REDIRECT_URL=os.getenv('clickup_redirect_url')
    SQLALCHEMY_DATABASE_URI = os.environ.get('postgres_url')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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

    BOT_SLACK_ID = "U028NRCSKJM"
    WHITELIST_SLACK_ID = ["U05S521VB1N","U0327PUKEAD"]