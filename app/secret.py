import os

class Secret:
    dify_token = os.getenv('dify_token')
    clickup_token = os.getenv('clickup_token')
    bot_token = os.getenv('bot_token')

    slack_client_id = os.getenv('slack_client_id')
    slack_client_secret = os.getenv('slack_client_secret')

    product_infra_ticket_list_id = "900901259853"
    product_infra_sprint_folder_id = "90091061131"

    bot_slack_id = "U028NRCSKJM"
    whitelist_slack_id = ["U05S521VB1N","U0327PUKEAD"]